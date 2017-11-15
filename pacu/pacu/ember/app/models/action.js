import DS from 'ember-data';

export default DS.Model.extend({
  model_name: DS.attr(),
  model_id: DS.attr(),
  query_only: DS.attr(),
  action_name: DS.attr(),
  action_args: DS.attr(),
  action_kwargs: DS.attr(),
  status_code: DS.attr(),
  status_text: DS.attr(),
  meta: DS.attr(),
});
