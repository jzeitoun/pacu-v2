import DS from 'ember-data';

export default DS.Model.extend({
  name: DS.attr('string'),
  rois: DS.hasMany('fb-roi', { async: true }),
  neuropil_enabled: DS.attr({ defaultValue: false }),
  neuropil_factor: DS.attr({ defaultValue: 0.7 }),
  neuropil_ratio: DS.attr({ defaultValue: 4.0 })
});
