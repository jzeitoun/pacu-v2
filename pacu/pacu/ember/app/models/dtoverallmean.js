import DS from 'ember-data';
import Datatag from 'pacu-v2/models/datatag';
import { computed } from '@ember/object';

export default Datatag.extend({
  value: DS.attr({ defaultValue:[] }),
  roi: DS.belongsTo('roi'),
  valueByFocalPlane: computed('value', function() {
    var value = this.get('value');
    const offset = this.get('roi.workspace.cur_pane') || 0;
    const nPanes = this.get('roi.workspace.condition.info.focal_pane_args.n') || 1;
    return value.filter((_, i) => i % nPanes == offset);
  })
});
