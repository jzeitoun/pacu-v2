import Ember from 'ember';

export default Ember.Service.extend({
  all: null,
  computed: Ember.computed('all.@each.{polygon,lastComputedPolygon}', function() {
    var allROIs = this.get('all').toArray();
    var computedROIs = [];
    for (var i=0; i<allROIs.length; i++) {
      var roi = allROIs[i];
      if (roi.get('polygon') == roi.get('lastComputedPolygon')) {
        computedROIs.push(roi);
      };
    };
    return computedROIs;
  }),
  uncomputed: Ember.computed('all.@each.{polygon,lastComputedPolygon}', function() {
    var allROIs = this.get('all').toArray();
    var uncomputedROIs = [];
    for (var i=0; i<allROIs.length; i++) {
      var roi = allROIs[i];
      if (!(roi.get('polygon') == roi.get('lastComputedPolygon'))) {
        uncomputedROIs.push(roi);
      };
    };
    return uncomputedROIs;
  }),
});
