import FirebaseAdapter from 'emberfire/adapters/firebase';
import { pluralize } from 'ember-inflector';

export default FirebaseAdapter.extend({
  /* redirect path to workspaces instead of fbWorkspaces */
  pathForType(modelName) {
    modelName = modelName.split('-')[1];
    var camelized = Ember.String.camelize(modelName);
    return pluralize(camelized);
  },
});
