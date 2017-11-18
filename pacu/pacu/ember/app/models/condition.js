import DS from 'ember-data';

export default DS.Model.extend({
  workspaces: DS.hasMany('workspace'),
  trials: DS.hasMany('trial'),
  info: DS.attr(),
  imported: DS.attr(),
  message: DS.attr(),
  pixel_x: DS.attr(),
  pixel_y: DS.attr(),
  focal_pane: DS.attr(),
  dist: DS.attr(),
  width: DS.attr(),
  height: DS.attr(),
  contrast: DS.attr(),
  gamma: DS.attr(),
  on_duration: DS.attr(),
  off_duration: DS.attr(),
  orientations: DS.attr(),
  sfrequencies: DS.attr(),
  tfrequencies: DS.attr(),
  contrasts: DS.attr(),
  repetition: DS.attr(),
  projection: DS.attr(),
  stimulus: DS.attr(),
  handler: DS.attr(),
  keyword: DS.attr(),
  trial_list: DS.attr(),
});