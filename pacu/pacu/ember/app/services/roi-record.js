import Service from '@ember/service';
import { computed } from '@ember/object';

export default Service.extend({
  all: null,
  selected: computed.filterBy('all', 'selected', true),
  unselected: computed.filterBy('all', 'selected', false),
  computed: computed.filter('all.@each.{polygon,lastComputedPolygon}', function(roi, index, array) {
    return roi.get('polygon') == roi.get('lastComputedPolygon');
  }),
  uncomputed: computed.filter('all.@each.{polygon,lastComputedPolygon}', function(roi, index, array) {
    return roi.get('polygon') != roi.get('lastComputedPolygon');
  }),
});
