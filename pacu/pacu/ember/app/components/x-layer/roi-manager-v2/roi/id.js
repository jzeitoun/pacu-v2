import Ember from 'ember';
import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: 'text',
  classNames: ['unselectable'],
  classNameBindings: ['hover:visible-id:hidden-id'],
  attributeBindings: ['x','y','fontSize:font-size', 'fill'],
  roi_id: null,
  points: null,
  hover: false,
  selected: false,
  //visible: computed.or('hover', 'selected'),
  fontSize: 20,
  fill: '#FFFFFF',
  x: Ember.computed('points', function() {
    if (!this.get('points')) {
      return 0;
    };
    var pointArray = this.get('points').split(',').map(Number);
    var x = [];
    for (var i=0; i<pointArray.length; i+=2) {
      x.push(pointArray[i]);
    }
    var xMin = Math.min(...x);
    var xMax = Math.max(...x);
    return xMin + ((xMax-xMin)*.95);
  }),
  y: Ember.computed('points', function() {
    if (!this.get('points')) {
      return 0;
    };
    var pointArray = this.get('points').split(',').map(Number);
    var y = [];
    for (var i=1; i<pointArray.length; i+=2) {
      y.push(pointArray[i]);
    }
    var yMin = Math.min(...y);
    var yMax = Math.max(...y);
    return yMin + ((yMax-yMin)*.1);
  }),
});
