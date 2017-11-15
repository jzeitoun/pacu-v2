import DS from 'ember-data';

export default DS.Model.extend({
  condition: DS.belongsTo('condition'),
  on_time: DS.attr(),
  off_time: DS.attr(),
  ori: DS.attr(),
  sf: DS.attr(),
  tf: DS.attr(),
  contrast: DS.attr(),
  sequence: DS.attr(),
  order: DS.attr(),
  ran: DS.attr(),
  flicker: DS.attr(),
  blank: DS.attr(),
  datatags: DS.hasMany('datatag'),
});
