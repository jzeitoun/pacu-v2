import Component from '@ember/component';

export default Component.extend({
  tagName: 'div',
  classNames: ['modal-banner'],
  classNameBindings: ['visibility:visible'],
  visibility: false,
});
