import Component from '@ember/component';
import singleCols from './single-columns';
import multipleCols from './multiple-columns';
import { inject as service } from '@ember/service';

export default Ember.Component.extend({
  singleCols,
  multipleCols,
  elementId: 'stats-overview',
  tagName: 'table',
  classNames: ['ui', 'celled', 'unstackable', 'selectable', 'inverted',
    'structured', 'small', 'compact', 'table'],
  didInsertElement() {
    window.T = this;
  },
  didUpdate() {
    console.log(this.get('rois'));
  }
});
