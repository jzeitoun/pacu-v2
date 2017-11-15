import Ember from 'ember';
import DS from 'ember-data';
import { observer } from '@ember/object';

export default DS.Model.extend({
  created_at: DS.attr('date'),
  updated_at: DS.attr('date'),
  etext: DS.attr('string'),
  etype: DS.attr('string'),
  trial_on_time: DS.attr(),
  trial_off_time: DS.attr(),
  trial_ori: DS.attr(),
  trial_sf: DS.attr(),
  trial_tf: DS.attr(),
  trial_contrast: DS.attr(),
  trial_sequence: DS.attr(),
  trial_order: DS.attr(),
  trial_ran: DS.attr(),
  trial_flicker: DS.attr(),
  trial_blank: DS.attr(),

  roiChanged: observer('roi', function() {
    this.get('roi').then(Ember.run.bind(this, 'cascadeDelete'));
  }),
  cascadeDelete(roi) {
    if (Ember.isPresent(roi)) { return; }
    this.store.unloadRecord(this);
  },
  action(name, ...args) {
    if (this.get('inAction')) { return; }
    this.set('inAction', true);
    this.actions[name].apply(this, args).finally(() => {
      this.set('inAction', false);
    });
  },
  actions: {
    fetch() {
      return this.store.createRecord('action', {
        model_name: 'Datatag',
        model_id: this.id,
        action_name: 'refresh',
      }).save().then((/*data*/) => {
        this.reload();
      });
    }
  },
});
