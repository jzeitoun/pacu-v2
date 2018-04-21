import Component from '@ember/component';

export default Component.extend({
  tagName: 'polygon',
  classNames: ['roi'],
  classNameBindings: ['selected', 'dragging', 'pointdrag', 'inProgress', 'computed'],
  attributeBindings: ['points','roi_id:data-roi-id'],
});
