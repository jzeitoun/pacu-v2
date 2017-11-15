import DS from 'ember-data';
import Datatag from 'pacu-v2/models/datatag';

export default Datatag.extend({
  roi: DS.belongsTo('roi'),
  value: DS.attr(),
});
