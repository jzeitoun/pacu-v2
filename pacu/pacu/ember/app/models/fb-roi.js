import DS from 'ember-data';
import { computed } from '@ember/object';

export default DS.Model.extend({
  created: DS.attr('date'),
  roi_id: DS.attr('number'),
  workspace: DS.belongsTo('fb-workspace'), //DS.attr('string'),
  polygon: DS.attr('string'), // list of coordinate pairs
  lastComputedPolygon: DS.attr('string'),
  neuropilPolygon: DS.attr('string', { defaultValue: '' }),
  hover: false,
  selected: false,
  dragging: false,
  pointdrag: false,
  targetPoint: null,
});
