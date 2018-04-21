import Component from '@ember/component';

export default Component.extend({
  tagName: 'div',
  classNames: ['custom-modal'],
  classNameBindings: ['visibility:visible-modal'],
  visibility: false,
});
