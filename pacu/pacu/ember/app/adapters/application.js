import DS from 'ember-data';
import { underscore } from '@ember/string';
import { inject as service } from '@ember/service';

export default DS.JSONAPIAdapter.extend({
  session: service(),
  namespace: 'api',
  host: function() {
    const hostname = location.hostname;
    const port = this.get('session.app.port') + 30000;
    return `http://${hostname}:${port}`
  }.property('session.app.port'),
  headers: function() {
    const m = this.get('session.jsonapi.moduleName');
    const s = this.get('session.jsonapi.sessionArgs');
    const b = this.get('session.jsonapi.baseName');
    return {
      PACU_JSONAPI_MODULE_NAME: m,
      PACU_JSONAPI_SESSION_ARGUMENTS: s,
      PACU_JSONAPI_BASE_NAME: b
    };
  }.property('session.jsonapi.{moduleName,sessionArgs,baseName}').volatile(),

  ajax(url, type, hash) {
    this.set('store.isfetching', true);
    return this._super(url, type, hash).finally(() => {
      this.set('store.isFetching', false);
    });
  },

  pathForType(type) {
    if (type.includes('dtanovaeach')) {
      return type + 's';
    };
    return underscore(this._super(type));
  },
});
