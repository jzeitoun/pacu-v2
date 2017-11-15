import Controller from '@ember/controller';
import EmberObject, { computed } from '@ember/object';

export default Controller.extend({
  queryParams: ['dsMonthPrev', 'dsGlob', 'dsDays', 'filter'],
  dsDays: 3650,
  dsGlob: '*',
  dsHops: '',
  filter: '',
  filteredModel: computed.filterBy('model.ios', 'info.iopath', 'filter'),
  filteredIOs: computed('model.ios.[]', 'filter', function() {
    var {'model.ios':ios, filter} = this.getProperties('model.ios', 'filter')
    return ios.filter(io => io.info.iopath.includes(filter))
  })
});
