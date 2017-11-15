import Ember from 'ember';
import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  attributeBindings: ['style', 'width', 'height'],
  style: computed('width', 'height', function() {
    var {width:w, height:h} = this.getProperties('width', 'height');
    return Ember.String.htmlSafe(`width: ${w}px; height: ${h}px;`);
  }),
  didInsertElement() {
    Ember.$(document).on('keydown.x-layer', (e) => {
      // check if event sender is valid.
      const keyCode = e.keyCode || e.which;
      // 13 enter
      // 32 space bar
      if (keyCode == 9) { // tab
        // e.preventDefault();
        // this.get('do')('rotateFocus');
        // $('html, body').stop(true, true).animate({
        //   scrollTop: $('html').offset().top
        // }, 100);
      }
      if (keyCode == 13) { // enter
        this.get('do')('hitFocus');
      }
    });
  },
  willDestroyElement() {
    Ember.$(document).off('keydown.x-layer');
  },
});

