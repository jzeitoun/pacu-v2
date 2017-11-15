import DS from 'ember-data';
import Datatag from 'pacu-v2/models/datatag';

export default Datatag.extend({
  roi: DS.belongsTo('roi'),
  matrix: DS.attr(),
  meantrace: DS.attr(),
  indices: DS.attr(),
  on_frames: DS.attr(),
  bs_frames: DS.attr(),
});
