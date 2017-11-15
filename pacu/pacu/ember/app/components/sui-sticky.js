import Component from '@ember/component';

export default Component.extend({
  didInsertElement() {
  //creates container same height as child div
    this.$().height(this.$('> div').height());
    this.$('> div').addClass('sticky').sticky({
    });
  },
});
