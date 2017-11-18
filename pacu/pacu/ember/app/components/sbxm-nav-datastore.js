import Ember from 'ember';
import Component from '@ember/component';
import { inject as service } from '@ember/service';
import EmberObject, { computed, observer } from '@ember/object';

function importRaw(cond={}) {
  const self = this;
  const modname = 'pacu-v2.core.io.scanbox.impl2';
  const clsname = 'ScanboxIO';
  const $console = Ember.$('#import-progress');
  const messages = this.get('messages');
  const rawName = this.get('activeItem.name');
  const ioPath = [].concat(this.get('arrHops'), rawName + '.io').join('/');
  $console.modal('show', {closable: false});
  this.get('socket').create(this, modname, clsname, {path: ioPath}).then(wsx => {
    messages.pushObject({body: 'Please wait...'});
    wsx.invoke('import_raw', cond.id).then(newIO => {
      // console.log('IMPORT RAW DONE', newIO);
      this.get('ios').pushObject(newIO);
      this.get('toast').info(`Data imported successfully.
        Click "New Session" to setup your first analysis.`);
    }).catch(err => {
      console.log(err);
      self.get('toast').error(err.detail, err.title);
    }).finally(function() {
      wsx.dnit();
      Ember.run.later(function() {
        $console.modal('hide');
        messages.clear();
      }, 1000);
    });
  });
}

const params = ['hops', 'src', 'glob', 'days'];

export default Component.extend({
  toast: service(),
  socket: service(),
  hops: '',
  dirs: [],
  sbxs: [],
  conditions: [],
  filterText: '',
  conditionFilterText: '',
  classNames: ['ui', 'inverted', 'segment'],
  messages: computed(function() { return []; }),
  arrHops: computed('hops', function() {
    var hops = this.get('hops');
    return hops.split(',').filter(w => !Ember.isEmpty(w));
  }),
  filteredDIRs: computed('dirs', 'filterText', function() {
    var {dirs, filterText} = this.getProperties('dirs', 'filterText');
    return dirs.filter(dir => dir.name.includes(filterText));
  }),
  filteredSBXs: computed('sbxs', 'filterText', function() {
    var {sbxs, filterText} = this.getProperties('sbxs', 'filterText');
    return sbxs.filter(sbx => sbx.name.includes(filterText));
  }),
  filteredConds: computed('conditions', 'conditionFilterText', function() {
    var {conditions:cs, conditionFilterText:fText} = this.getProperties('conditions', 'conditionFilterText');
    return cs.filterBy('keyword').filter(c => c.keyword.includes(fText));
  }),

  query: observer(...params, function() {
    this.set('busy', true);
    const { hops, src, glob, days } = this.getProperties(params);
    Ember.$.getJSON(src, { hops, glob, days }).then(data => {
      this.set('dirs', data.dirs);
      this.set('sbxs', data.sbxs);
    }).fail((err/* , text, statusText */) => {
      this.set('err', err);
    }).done(() => {
      this.set('err', null);
    }).always(() => {
      this.set('busy', false);
    });
  }),

  init() {
    this._super(...arguments);
    Ember.run.next(this, 'query');
  },

  actions: {
    popHop() {
      const hops = this.get('arrHops');
      hops.pop();
      this.set('hops', hops.join(','));
    },
    addHop(item) {
      const hops = this.get('arrHops');
      hops.push(item.name);
      this.set('hops', hops.join(','));
    },
    openImportModal(item) {
      this.set('activeItem', item);
      this.get('toast').info('Search conditions and click to import with the recording.');
      Ember.$('.sbx.conditions.modal').modal('show');
    },
    importRawWithCondition(cond) {
      Ember.$('.sbx.conditions.modal').modal('hide');
      importRaw.call(this, cond);
    },
    importRawWithoutCondition(/*cond*/) {
      Ember.$('.sbx.conditions.modal').modal('hide');
      importRaw.call(this);
    }
  },

  on_sse_print(msg /*, err*/) {
    if (10 == msg.charCodeAt() || 32 == msg.charCodeAt()) { return; }
    this.get('messages').pushObject({body: msg});
  },
});
