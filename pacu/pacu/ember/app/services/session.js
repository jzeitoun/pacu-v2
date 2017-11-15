import Service from '@ember/service';
import EmberObject, { computed } from '@ember/object';

export default Service.extend({
  jsonapi: computed(function() {
    console.log('get/set jsonapi session');
    return EmberObject.create({
      moduleName:'',
      sessionArgs: [],
      baseName: ''
    });
  }),
});
