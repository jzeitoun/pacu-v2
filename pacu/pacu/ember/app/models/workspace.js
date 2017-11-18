import Ember from 'ember';
import DS from 'ember-data';
import { computed } from '@ember/object';

export default DS.Model.extend({
  created_at: DS.attr('date'),
  name: DS.attr('string'),
  cur_sfreq: DS.attr(),
  cur_tfreq: DS.attr(), // added for tfrequency
  cur_contrast: DS.attr(),
  cur_pane: DS.attr(),
  baseline_duration: DS.attr(),
  sog_initial_guess: DS.attr(),
  params: DS.attr(),
  // iopath: attr('string'),
  rois: DS.hasMany('roi'),
  // dtoverallmeans: hasMany('dtoverallmean'),
  // colormaps: hasMany('colormap'),
  condition: DS.belongsTo('condition'),
  // ecorrs: hasMany('ephys-correlation'),
  //activeROIs: Ember.computed.filterBy('rois', 'active', true),
  activeROI: null,//Ember.computed.alias('activeROIs.firstObject'),
  //savingROIs: Ember.computed.filterBy('rois', 'isSaving', true),
  //loadingROIs: Ember.computed.filterBy('rois', 'isLoading', true),
  //busyROIs: Ember.computed.uniq('savingROIs', 'loadingROIs'),
  //roisIdle: Ember.computed.empty('busyROIs'),
  //roisBusy: Ember.computed.not('roisIdle'),
  // @computed('rois.[]') dtsOverallMean(rois) {
    // const all = this.store.peekAll('datatag').filterBy('category', 'overall');
    // console.log('dtsOverallMean', all);
    // return all
  // },
  appendROI(payload) {
    payload.workspace = this;
    return this.store.createRecord('roi', payload);
  },
  importROIs(jsonstr) {
    const payloads = JSON.parse(jsonstr);
    for (let polygon of payloads) {
      this.store.createRecord('roi', {
        polygon, workspace: this
      }).save();
    }
  },
  loadedROIs: computed.filterBy('rois', 'isNew', false)
});
