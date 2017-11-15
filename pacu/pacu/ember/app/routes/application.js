import Ember from 'ember';
import Route from '@ember/routing/route';
import RSVP from 'rsvp';
import { inject as service } from '@ember/service';

export default Route.extend({
  session: service('session'),
  actions: {
    toggleFullscreen() {
      this.fullscreen.toggle();
    },

    toastInfo(title, detail) {
      this.toast.info(detail, title);
    },

    toastWarning(title, detail) {
      this.toast.warning(detail, title);
    },
  },

  model() {
    const app = Ember.$.getJSON('/api/json/application/info');
    const routes = [
      {
        content: 'Scanbox V2 Manager',
        linkTo: 'scanbox-manager',
        icon: 'cube',
        color: 'black',
      },
    ];
    return RSVP.hash({ app, routes });
  },

  afterModel(model /*, transition */) {
    this._super(...arguments);
    this.get('session').set('app', model.app);
  },
});
