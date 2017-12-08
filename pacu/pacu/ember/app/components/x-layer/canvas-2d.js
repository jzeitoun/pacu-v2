import Ember from 'ember';
import Component from '@ember/component';
import { computed, observer } from '@ember/object';

export default Component.extend({
/* global Uint8ClampedArray */
  tagName: 'canvas',
  img: computed('ctx', 'width', 'height', function() {
    var {ctx:c, width:w, height:h} = this.getProperties('ctx', 'width', 'height');
    if (Ember.isNone(w) || Ember.isNone(h)) { return; }
    this.element.width = w;
    this.element.height = h;
    return c.getImageData(0, 0, w, h);
  }),
  ctx: computed(function() {
    return this.element.getContext('2d');
  }),
  bufferChanged: observer('buffer', function() {
    var {img, ctx, buffer} = this.getProperties('img', 'ctx', 'buffer');
    if (Ember.isNone(img) || Ember.isNone(buffer)) { return; }
    img.data.set(new Uint8ClampedArray(buffer));
    ctx.putImageData(img, 0, 0);
  }),

  didInsertElement() {
    // ensures default value of 255 for contrast slider
    //document.getElementById('max-slider').value = "255"
  }
});
