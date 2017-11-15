import DS from 'ember-data';
import { underscore } from '@ember/string';

export default DS.JSONAPISerializer.extend({
  keyForAttribute: function(attr) {
    return underscore(attr);
  },

  serializeAttribute(snapshot, json, key, attributes) {
    if (snapshot.record.get('isNew') || snapshot.changedAttributes()[key]) {
      this._super(snapshot, json, key, attributes);
    }
  }
});
