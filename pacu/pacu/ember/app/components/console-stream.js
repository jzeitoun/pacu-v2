import Component from '@ember/component';
import { observer } from '@ember/object';

export default Component.extend({
  didInsertElement() {
    this.viewport = this.$()[0];
    this.updateScroll();
  },

  updateScroll: observer('messages.[]', function() {
    console.log('updated scroll');
    this.viewport.scrollTop = this.viewport.scrollHeight;
    // Ember.run.scheduleOnce('afterRender', this, function() {
    // });
    }),
  //}.on('didUpdate').observes('messages.[]')

});
