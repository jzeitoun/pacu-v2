import DS from 'ember-data';

export default DS.Model.extend({
  created: DS.attr('date'),
  roi_id: DS.attr('number'),
  workspace: DS.belongsTo('fb-workspace'), //DS.attr('string'),
  polygon: DS.attr('string'), // list of coordinate pairs
  lastComputedPolygon: DS.attr('string'),
  neuropil_ratio: DS.attr('number', { defaultValue: 4.0 }),
  neuropil_factor: DS.attr('number', { defaultValue: 0.7 }),
  neuropil_polygon: DS.attr('string', { defaultValue: "" }),
  neuropil_enabled: DS.attr('boolean', { defaultValue: false }),
  hover: false,
  selected: false,
  dragging: false,
  pointdrag: false,
  targetPoint: null,
});
