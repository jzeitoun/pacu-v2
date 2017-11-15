import Ember from 'ember';
import Route from '@ember/routing/route';
import RSVP from 'rsvp';

/* global swal */

function newWorkspace(io, name, pane) {
  const payload = {iopath: io.info.iopath, name, pane};
  Ember.$.ajax('/api/json/scanbox_manager/workspace', {
    type: 'POST',
    data: payload,
    dataType: 'json'
  }).then(data => {
    io.workspaces.pushObject(data.name);
    swal.close();
  }).fail((err/*, text ,statusText*/) => {
    this.toast.error(err.responseText, err.statusText);
  });
}

function removeImported(io) {
  Ember.$.ajax('/api/json/scanbox_manager/io', {
    type: 'DELETE',
    data: { iopath: io.info.iopath },
    dataType: 'json',
  }).then((/*data*/) => {
    this.currentModel.ios.removeObject(io);
  }).fail((err /*, text, statusText*/) => {
    this.toast.error(err.responseText, err.statusText);
  });
}

function removeWorkspace(io, name) {
  Ember.$.ajax('/api/json/scanbox_manager/workspace', {
    type: 'DELETE',
    data: { iopath: io.info.iopath, name },
    dataType: 'json',
  }).then(() => {
    io.workspaces.removeObject(name);
  }).fail((err/*, text, statusText*/) => {
    this.toast.error(err.responseText, err.statusText);
  });
}

export default Route.extend({
  queryParams: {
    filter: {
      replace: true
    }
  },

  model() {
    return RSVP.hash({
      path: Ember.$.getJSON('/api/json/scanbox_manager/path'),
      conditions: Ember.$.getJSON('/api/json/scanbox_manager/conditions'),
      ios: Ember.$.getJSON('/api/json/scanbox_manager/ios'),
    });
  },

  actions: {
    newWorkspace(io) {
      if (io.info.focal_pane_args) {
        const inputOptions = {};
        for (let i=0; i<io.info.focal_pane_args.n; i++) {
          inputOptions[i] = i;
        }
        swal.setDefaults({
          confirmButtonText: 'Next &rarr;',
          showCancelButton: true,
          customClass: "trj-analyses",
          progressSteps: ['1', '2']
        })
        const steps = [
          {
            title: "New session...",
            text: 'Provide a unique session name. I suggest "main" as a default name.',
            input: 'text'
          },
          {
            title: "With focal pane...",
            text: `You have ${io.info.focal_pane_args.n} panes, which one would you like?`,
            input: 'select',
            inputOptions
          },
        ];
        swal.queue(steps).then(result => {
          const [name, pane] = result;
          if (name === false) return false;
          if (name === "") {
            this.toast.warning('Please provide a name.')
            return false;
          }
          newWorkspace.call(this, io, name, pane);
        }, () => {
          swal.resetDefaults()
        }).then(() => {
          swal.resetDefaults()
        });
      } else {
        swal({
          title: 'New session...',
          text: 'Provide a unique session name. I suggest "main" as a default name.',
          input: 'text',
          inputPlaceholder: "Alphanumeric characters including underscore...",
          customClass: "trj-analyses",
          showCancelButton: true,
          confirmButtonText: 'Submit',
          allowOutsideClick: false,
        }).then(value => {
           if (value === false) return false;
           if (value === "") {
             swal.showInputError("Please provide a name.");
             return false;
           }
          newWorkspace.call(this, io, value);
        }).catch(() => {});
      }
    },

    removeImported(io) {
      swal({
        title: "Are you sure?",
        text: "You will not be able to undo this!",
        type: "warning",
        showCancelButton: true,
        closeOnConfirm: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete it!",
      }).then(() => {
        removeImported.call(this, io);
      }).catch(() => {});
    },

    removeWorkspace(io, ws) {
      swal({
        title: "Are you sure?",
        text: "You will not be able to undo this!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Yes, delete it!",
      }).then(() => {
        removeWorkspace.call(this, io, ws);
      }).catch(() => {});
    },

    openWorkspace(io, ws) {
      const path = `${io.info.iopath}/${ws}`;
      this.transitionTo('scanbox-analyzer', path);
    }
  }
});
