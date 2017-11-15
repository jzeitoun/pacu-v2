import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'rect',
  attributeBindings: ['x', 'y', 'width', 'height'],
  x: null,
  y: null,
  width: null,
  height: null,
});

