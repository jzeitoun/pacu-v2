import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: 'tbody',
  classNames: ['center', 'aligned'],
  subRows: computed('condition.sfrequencies', function() {
    return this.get('condition.sfrequencies');
  }),
  didUpdate() {
  }
});
