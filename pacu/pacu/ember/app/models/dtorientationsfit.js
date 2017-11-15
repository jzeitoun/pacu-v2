import DS from 'ember-data';
import Datatag from 'pacu-v2/models/datatag';

export default Datatag.extend({
  value: DS.attr(),
  roi: DS.belongsTo('roi'),
  sog_params: DS.attr()
});
