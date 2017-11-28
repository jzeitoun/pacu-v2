import Ember from 'ember';
import DS from 'ember-data';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default DS.Model.extend({
  toast: service(),
  didCreate() {
    this._super(...arguments);
    if(Ember.isNone(this.get('params.cell_id'))) {
      const cid = this.get('id');
      const params = this.get('params');
      this.set('params', { params, cell_id: cid });
      this.save();
    }
  },
  created_at: DS.attr('date'),
  params: DS.attr({ defaultValue: () => ({}) }),
  polygon: DS.attr({ defaultValue: () => { return []; } }),
  neuropil_ratio: DS.attr({ defaultValue: 4.0 }),
  neuropil_factor: DS.attr({ defaultValue: 0.7 }),
  neuropil_polygon: DS.attr({ defaultValue: () => { return []; } }),
  neuropil_enabled: DS.attr({ defaultValue: false }),
  sog_initial_guess: DS.attr(),
  draw_dtoverallmean: DS.attr({ defaultValue: false }),
  centroid: DS.attr({ defaultValue: () => { return {x: -1, y: -1}; } }),
  workspace: DS.belongsTo('workspace'),
  dtorientationsmeans: DS.hasMany('dtorientationsmean'),
  dtorientationsfits: DS.hasMany('dtorientationsfit'),
  dtanovaeachs: DS.hasMany('dtanovaeach'),
  dtsfreqfits: DS.hasMany('dtsfreqfit'),
  dtorientationbestprefs: DS.hasMany('dtorientationbestpref'),
  dtanovaalls: DS.hasMany('dtanovaall'),
  dtoverallmean: DS.belongsTo('dtoverallmean'),

  neuropil: computed('centroid', 'neuropil_ratio', 'neuropil_enabled', function() {
    var { centroid, neuropil_ratio:npRatio, neuropil_enabled:npEnabled } = this.getProperties(
      'centroid', 'neuropil_ratio', 'neuropil_enabled'
    );
    if (!npEnabled) {
      Ember.run.next(this, 'set', 'neuropil_polygon', []);
      return;
    }
    if (npRatio == 2) { return } // double equal for text and float compare
    const polygon = this.get('polygon');
    const npp = outerPointsByRatio(polygon, centroid, npRatio);
    Ember.run.next(this, 'set', 'neuropil_polygon', npp);
    return npp;
  }),

  focus() {
    this.unfocus();
    this.set('active', true);
  },

  enableTrace() {
    this.set('draw_dtoverallmean', true);
    this.save();
  },

  disableTrace() {
    this.set('draw_dtoverallmean', false);
    this.save();
  },

  enableNeuropil() {
    this.set('neuropil_enabled', true);
    return this.save();
  },

  disableNeuropil() {
    this.set('neuropil_enabled', false);
    return this.save();
  },

  askNeuropilRatio() {
    const ratio = prompt("Please enter neuropil ratio amount",
      this.get('neuropil_ratio'));
    const fRatio = parseFloat(ratio);
    if (isNaN(fRatio)) {
      this.get('toast').warning(`Invalid value ${ratio}.`);
    } else {
      this.set('neuropil_ratio', fRatio);
      this.save();
    }
  },

  askNeuropilFactor() {
    const factor = prompt("Please enter neuropil R value",
      this.get('neuropil_factor'));
    const fFactor = parseFloat(factor);
    if (isNaN(fFactor)) {
      this.get('toast').warning(`Invalid value ${factor}.`);
    } else {
      this.set('neuropil_factor', fFactor);
      this.save();
    }
  },

  saveROI() {
    this.save();
  },

  destroyROI() {
    this.destroyRecord();
  },

  refreshAll() {
    if (this.get('inAction')) { return; }
    this.set('inAction', true);
    return this.save().then(() => {
      return this.store.createRecord('action', {
        model_name: 'ROI',
        model_id: this.id,
        action_name: 'refresh_all'
      }).save().then((action) => {
        if (action.get('status_code') === 500) {
          this.get('toast').error(action.get('status_text'));
        } else {
          Ember.run.next(this, 'synchronizeDatatags');
        }
      }).finally(() => {
        this.set('inAction', false);
      });
    });
  },

  synchronizeDatatags() {
    if (this.get('workspace.condition.imported')) {
      this.get('dtorientationsmeans').reload();
      this.get('dtorientationsfits').reload();
      this.get('dtanovaeachs').reload();
      this.get('dtsfreqfits').reload();
      this.get('dtorientationbestprefs').reload();
      this.get('dtanovaalls').reload();
    } else {
      this.get('workspace.dtoverallmeans').reload();
    }
  },

  clearSoGParam() {
    const dt = this.get('cur_dtorientationsfit');
    dt.set('sog_params', null);
    dt.save();
  },

  overrideSoGParam() {
    const dt = this.get('cur_dtorientationsfit');
    const p = dt.get('sog_params');
    const current = `${p.a1_min}, ${p.a1_max}, ${p.a2_min}, ${p.a2_max}, ${p.sigma_min}, ${p.sigma_max}, ${p.offset_min}, ${p.offset_max}`;
    const toggled = !p.override;
    if (toggled) {
      const params = prompt('Please type new parameters', current);
      if (Ember.isNone(params)) { return; }
      try {
        const [a1_min, a1_max, a2_min, a2_max, sigma_min, sigma_max, offset_min, offset_max] = params.split(',').map(parseFloat);
        const newParams = { a1_min, a1_max, a2_min, a2_max, sigma_min, sigma_max, offset_min, offset_max };
        for (let p in newParams) {
          if (isNaN(newParams[p])) {
            throw 'Parameter error';
          }
        }
        dt.set('sog_params', {newParams, override: true});
        dt.save();
      } catch(e) {
        this.get('toast').warning(e);
      }
    } else {
        dt.set('sog_params', {override: false});
        dt.save();
    }
  },

  computeSoG() {
    this.get('toast').info('Recompute SoG fit...');
    if (this.get('inAction')) { return; }
    this.set('inAction', true);
    this.store.createRecord('action', {
      model_name: 'ROI',
      model_id: this.id,
      action_name: 'refresh_orientations_fit'
    }).save().then((action) => {
      if (action.get('status_code') === 500) {
        this.get('toast').error(action.get('status_text'));
      } else {
        Ember.run.next(() => {
          this.get('dtorientationsfits').reload();
        });
      }
    }).finally(() => {
      this.set('inAction', false);
    });
  },

  dtoverallmeanTrace: computed('dtoverallmean', function() {
    return this.get('dtoverallmean');
  }),

  dtorientationsmeanBySF: computed('workspace.cur_sfreq', 'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationsmeans', function() {
    var {'workspace.cur_sfreq':sfreq, 'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, dtorientationsmeans:dts} = this.getProperties(
      'workspace.cur_sfreq', 'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationsmeans'
    );
    console.log('updated dts');
    return dts.filterBy('trial_sf', sfreq).filterBy('trial_contrast', cont).findBy('trial_tf', tfreq);
  }),

  dtorientationsfitBySF: computed('workspace.cur_sfreq', 'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationsfits', function() {
    var {'workspace.cur_sfreq':sfreq, 'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, dtorientationsfits:dts} = this.getProperties(
      'workspace.cur_sfreq', 'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationsfits'
    );
    return dts.filterBy('trial_sf', sfreq).filterBy('trial_contrast', cont).findBy('trial_tf', tfreq);
  }),

  dtsfreqfitByCT: computed('workspace.cur_contrast', 'workspace.cur_tfreq', 'dtsfreqfits', function() {
    var {'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, dtsfreqfits:dts} = this.getProperties(
      'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtsfreqfits'
    );
    return dts.filterBy('trial_contrast', cont).findBy('trial_tf', tfreq);
  }),

  dtorientationbestprefByCT: computed('workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationbestprefs', function() {
    var {'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, dtorientationbestprefs:dts} = this.getProperties(
      'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationbestprefs'
    );
    return dts.filterBy('trial_contrast', cont).findBy('trial_tf', tfreq);
  }),

  dtanovaallByCT: computed('workspace.cur_contrast', 'workspace.cur_tfreq', 'dtanovaalls', function() {
    var {'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, 'dtanovaalls':dts} = this.getProperties(
      'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtanovaalls'
    );
    return dts.filterBy('trial_contrast', cont).findBy('trial_tf', tfreq);
  }),

  dtanovaeachsByCT: computed('workspace.cur_contrast', 'workspace.cur_tfreq', 'dtanovaeachs', function() {
    var {'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, dtanovaeachs:dts} = this.getProperties(
      'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtanovaeachs'
    );
    return dts.filterBy('trial_contrast', cont).filterBy('trial_tf', tfreq);
  }),

  dtorientationsfitsByCT: computed('workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationsfits', function() {
    var {'workspace.cur_contrast':cont, 'workspace.cur_tfreq':tfreq, dtorientationsfits:dts} = this.getProperties(
      'workspace.cur_contrast', 'workspace.cur_tfreq', 'dtorientationsfits'
    );
    return dts.filterBy('trial_contrast', cont).filterBy('trial_tf', tfreq);
  }),

  cur_dtorientationsfit: computed('workspace.cur_contrast', 'workspace.cur_sfreq', 'dtorientationsfits', function() {
    var {'workspace.cur_contrast':cont, 'workspace.cur_sfreq':sfreq, dtorientationsfits:dts} = this.getProperties(
      'workspace.cur_contrast', 'workspace.cur_sfreq', 'dtorientationsfits'
    );
    return dts.filterBy('trial_contrast', ct).filterBy('trial_sf', sf).get('firstObject');
  }),

  reprId: computed('params.cell_id', function() {
    var cid = this.get('params.cell_id');
    return cid || this.get('id');
  }),

  //setCellId() {
  //  const params = this.get('params');
  //  let cid = params.cell_id || '';
  //  cid = prompt('Please type new cell id. Blank will delete current id.', cid);
  //  if (cid.trim() === '') {
  //    cid = null;
  //  }
  //  this.set('params', { params, cell_id: cid });
  //  this.save();
  //},

  //toggleUseSeed() {
  //  const dtbestprefs = this.get('dtorientationbestprefs');
  //  const dt = this.get('cur_dtorientationsfit');
  //  const params = dt.get('sog_params');
  //  const toggled = !params.use_seed;
  //  dt.set('sog_params', { params, use_seed: toggled });
  //  if (toggled) {
  //    Ember.RSVP.all([ dtbestprefs.reload(), dt.save()]).then(() => {
  //      this.get('toast').info(
  //        `A seed value will be used for A1_MAX and A2_MAX to get Sog fit.<br>
  //         This will take precedence over SoG override params.<br>`);
  //    });
  //  } else {
  //    dt.save().then(() => {
  //      this.get('toast').info(
  //        `The seed value will not be used. Sog override params will take precedence if any.`);
  //    });
  //  }
  //}
});
