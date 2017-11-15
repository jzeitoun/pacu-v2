import Ember from 'ember';
import Component from '@ember/component';
import EmberObject, { computed } from '@ember/object';

const observeConfig = {
  attributes: true,
  attributeFilter: ['width', 'height']
};
const Child = EmberObject.extend({
  aspectRatio: computed('height', 'width', function() {
    var {height:h, width:w} = this.getProperties('height', 'width');
    return parseInt(h) / parseInt(w)
  }),
  desiredHeight(width) {
    return this.get('aspectRatio') * width;
  }
});

export default Component.extend({
  /*
  zoomable-container is designed to set its height
  automatically based on the dimension of child element.
  CSS zoom property is not standard and does not guarantee to work on
  every modern browsers. But if we try CSS transform and `scale`,
  DOM does not take place when it is overflown.

  Child element must define two attributes in the tag, width, height.
 */

  attributeBindings: ['style'],
  style: computed('child.aspectRatio', function() {
    var ratio = this.get('child.aspectRatio');
    if (Ember.isNone(this.element.firstElementChild)) { return ''; }
    const pTop = this.$().css('padding-top');
    const pBtm = this.$().css('padding-bottom');
    const containerWidth = this.$().width();
    const childWidth = this.get('child.width');
    const height = containerWidth * ratio;
    const scale = containerWidth/childWidth;
    const heightPadded = height + parseInt(pTop) + parseInt(pBtm);
    const parallelContainerStyle = Ember.String.htmlSafe(`
      height: ${heightPadded}px; overflow-y: scroll
    `);
    this.element.firstElementChild.style.transform = `scale(${scale})`;
    this.element.firstElementChild.style.transformOrigin = 'left top';
    const d = { height, pTop, pBtm, scale, heightPadded, parallelContainerStyle };
    const style = Ember.String.htmlSafe(
      `height: calc(${d.height}px + ${d.pTop} + ${d.pBtm});`
    );
    Ember.run.scheduleOnce('afterRender', this, () => {
      this.set('dimension', d);
      this.set('containerStyle', style);
    });
    return style;
  }),
  child: computed(function() { return Child.create(); }),
  observer: computed(function() {
    return new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        const key = mutation.attributeName;
        const val = mutation.target.getAttribute(mutation.attributeName);
        this.get('child').set(key, val);
      });
    });
  }),

  didInsertElement() {
    window.ASD = this;
    const child = this.element.firstElementChild;
    if (Ember.isNone(child)) { return; }
    Ember.$(window).on(`resize.${this.elementId}`, (/*e*/) => {
      this.notifyPropertyChange('style');
    });
    this.get('observer').observe(child, observeConfig);
  },

  willDestroyElement() {
    Ember.$(window).off(`resize.${this.elementId}`);
    this.get('observer').disconnect();
  }
});
