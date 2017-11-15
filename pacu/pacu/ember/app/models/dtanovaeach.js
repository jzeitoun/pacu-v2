import DS from 'ember-data';
import Datatag from 'pacu-v2/models/datatag';

export default Datatag.extend({
  f: DS.attr(),
  p: DS.attr(),
  roi: DS.belongsTo('roi'),
});
