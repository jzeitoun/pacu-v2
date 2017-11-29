import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: 'polygon',
  classNames: ['neuropil'],
  classNameBindings: ['selected', 'dragging', 'pointdrag', 'inProgress', 'computed'],
  attributeBindings: ['points']
});

