import Ember from 'ember';
import Route from '@ember/routing/route';
import RSVP from 'rsvp';
import { inject as service } from '@ember/service';

//import actions from 'pacu/scanbox-analyzer/actions';
import SocketStream from 'pacu-v2/socketstream/socketstream';

const modname = 'pacu.core.io.scanbox.impl2';
const clsname = 'ScanboxIOStream';
const moduleName = 'pacu.core.io.scanbox.model.db';
const baseName = 'SQLite3Base';
const include = 'condition,condition.trials';//dtoverallmeans,rois,rois.dtorientationsmeans,rois.dtorientationbestprefs,rois.dtorientationsfits,rois.dtanovaeachs,rois.dtsfreqfits,rois.dtanovaalls';
const queryParam = { include };

export default Route.extend({
  activate() {
    Ember.$(document).on('keyup.conditions', e => {
      var esName, eName;
      const ws = this.currentModel.workspace;
      const cd = this.currentModel.condition;
      switch (e.keyCode) {
        case 83: // s
          esName = 'sfrequencies';
          eName = 'cur_sfreq';
          break;
        case 67: // c
          esName = 'contrasts';
          eName = 'cur_contrast';
          break;
        case 84: // t
          esName = 'tfrequencies';
          eName = 'cur_tfreq';
          break;
        default:
          return false;
      }
      var elements = cd.get(esName);
      var element = ws.get(eName);
      var index = elements.indexOf(element);
      var next = elements[(index+1)%elements.length];
      ws.set(eName, next);
    });
  },
  deactivate() {
    Ember.$(document).off('keyup.conditions');
  },
  socket: service(),
  session: service(),
  model(param) {
    const store = this.get('store');
    window.R = this;
    const hops = param.hops.split('/');
    const wsName = hops.pop();
    const ioName = hops.join('/');
    this.get('session.jsonapi').setProperties({moduleName, baseName,
      sessionArgs: [ioName]
    });
    const kw = {iopath:ioName, wsname: wsName};
    const workspace = new Ember.RSVP.Promise((resolve/*, reject*/) => {
      Ember.$.getJSON('/api/json/scanbox_manager/workspace_id', kw).then(id => {
        resolve(this.store.findRecord('workspace', id, queryParam));
      });
    });
    let cur_pane;
    const condition = workspace.then(ws => {
      if (wsName !== ws.get('name')) {
        swal(
          'Reference error',
          'Session seems to refer to a wrong workspace. Please restart Pacu process in backend!',
          'error'
        )
        this.transitionTo('scanbox-manager');
      }
      cur_pane = ws.get('cur_pane') || 0;
      return ws.get('condition');
    });
    const stream = condition.then(() => {
      return new RSVP.Promise((resolve /*, reject */) => {
        return this.get('socket').create(
          this, modname, clsname, ioName
        ).then((wsx) => {
          wsx.invoke('setup_focal_pane', cur_pane);
          wsx.socket.onclose = () => {
            this.toast.warning('WebSocket connection closed.');
          };
          this.set('wsx', wsx);
          this.toast.success('WebSocket connection estabilished.');
          Ember.run.later(() => {
            resolve(SocketStream.create({ wsx }));
          }, 1000); // necessary
        });
      });
    });
    const name = { io: ioName, ws: wsName };
    const wsAlias = param.hops;
    const file = store.query('file', {
      orderBy: 'name',
      equalTo: ioName
    }).then(function(result) {
      var f = result.get('firstObject');
      if (!f) {
        f = store.createRecord('file', {
          name: ioName
        });
      };
      return f;
    });
    const firebaseWorkspace = store.query('fb-workspace', {
      orderBy: 'name',
      equalTo: wsAlias
    }).then(function(result) {
      var ws = result.get('firstObject');
      if (!ws) {
        ws =  store.createRecord('fb-workspace', {
          name: wsAlias
        });
      };
      ws.get('rois');
      return ws;
    });
    //const rois = this.get('store').query('roi', {
    //  orderBy: 'workspace',
    //  equalTo: wsName
    //}).then(function(rois) {
    //  console.log(rois);
    //  return rois;
    //}).catch(function(reason) {
    //  console.log(reason);
    //});
    return RSVP.hash({ condition, workspace, file, firebaseWorkspace, stream, name });
  },
  afterModel(/*model, transition */) {
    this._super(...arguments);
  },
  setupController(controller, model) {
    this._super(...arguments);
    controller.set('stream', model.stream);
    //Added by RA
    //sets ROI toggle default state.
    this.controller.set('toggleROIs', true);
    //Added by RA
    //sets ROI display mode to default state. Currently default is minimal info.
    this.controller.set('MinModeROIs', false);
  },

  on_sse_print(msg, err) {
    if (10 === msg.charCodeAt() || 32 === msg.charCodeAt()) { return; }
    if(err) { return this.toast.error(err); }
    this.toast.info(msg);
  },

  actions: {
    do(/*action, ...args*/) {
      // alert('not supported');
      // return this.actions[action].apply(this, args);
    },
    willTransition(/*transition*/) {
      this.store.unloadAll(); // releasing all data resources. important.
      this.wsx.dnit();
      this.wsx = null;
      Ember.$('#roi-import-file-all').off('change.pacu-roi-import-all');
      Ember.$('#roi-import-file-diff').off('change.pacu-roi-import-diff');
    },
    didTransition() {
      //Ember.run.schedule('afterRender', () => {
      //  Ember.$('#roi-import-file-all').on('change.pacu-roi-import-all', importROIFileAllChanged.bind(this));
      //  Ember.$('#roi-import-file-diff').on('change.pacu-roi-import-diff', importROIFileDiffChanged.bind(this));
      //});
    }
  }
});
