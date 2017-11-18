import EmberRouter from '@ember/routing/router';
import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType,
  rootURL: config.rootURL
});

Router.map(function() {
  this.route('scanbox-manager');
  this.route('scanbox-analyzer', { path: '/scanbox-analyzer/*hops' });
  this.route('chart-route');
});

export default Router;
