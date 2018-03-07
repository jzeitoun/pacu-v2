import DS from 'ember-data';
import { computed } from '@ember/object';
import firebase from 'firebase';

export default DS.Model.extend({
  created: DS.attr('date', { defaultValue: firebase.database.ServerValue.TIMESTAMP }),
  roi_id: DS.attr('number'),
  workspace: DS.belongsTo('fb-workspace'), //DS.attr('string'),
  polygon: DS.attr('string'), // list of coordinate pairs
  lastComputedPolygon: DS.attr('string', { defaultValue: '' }),
  neuropilPolygon: DS.attr('string', { defaultValue: '' }),
  hover: false,
  selected: false,
  dragging: false,
  pointdrag: false,
  targetPoint: null,
});
