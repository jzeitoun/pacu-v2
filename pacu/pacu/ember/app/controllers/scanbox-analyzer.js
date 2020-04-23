import Ember from 'ember';
import Controller from '@ember/controller';
import { inject as service } from '@ember/service';
import download from 'pacu-v2/utils/download';
import batch from 'pacu-v2/utils/batch';
import firebase from 'firebase';
import { all } from 'rsvp';
import { later, next } from '@ember/runloop';
import JSZip from "npm:jszip";

const { getOwner } = Ember;

const include = 'dtoverallmean,dtorientationbestprefs,dtorientationsmeans,dtorientationsfits,dtanovaeachs,dtsfreqfits,dtanovaalls';
const queryParams = { include };

function pad(number) {
      if (number < 10) {
        return '0' + number;
      }
      return number;
    }

Date.prototype.toCustomString = function() {
  return this.getUTCFullYear() +
    '-' + pad(this.getUTCMonth() + 1) +
    '-' + pad(this.getUTCDate()) +
    '-' + pad(this.getHours()) +
    '-' + pad(this.getUTCMinutes()) +
    '-' + pad(this.getUTCSeconds());
};

export default Controller.extend({
  selection: [],
  roiRecord: service(),
  modalVisibility: false,
  syncModalVisibility: false,
  exportModalVisibility: false,
  insertModalVisibility: false,
  exportMongoVisibility: false,
  autoSync: true,
  roisVisible: true,

  actions: {
    monitorFirebaseConnection() {
      console.log('monitor set up');
      var connectedRef = firebase.app().database().ref('.info/connected');
      connectedRef.on('value', snap => {
        if (snap.val() === true) {
          this.set('fbConnection', true);
        } else {
          this.set('fbConnection', false);
        }
      });
    },

    changeSync() {
      this.toggleProperty('autoSync');
    },

    addROI(roi, file, workspace) {
      file.save(); // saving roi_count to file to maintain compatibility with sqlite structure
      var newROI = this.get('store').createRecord('fb-roi', roi);
      workspace.get('rois').addObject(newROI);
      newROI.save().then(function() {
        return workspace.save();
      });
    },

    updateROI(roi) {
      roi.save()
    },

    deleteROI(roi) {
      roi.destroyRecord().then(() => {
        // Set count to max ID after deleting
        var remainingROIs = this.get('roiRecord.all');
        var remainingIDs = remainingROIs.map(function(roi) {
          return roi.get('roi_id');
        })
        if (remainingIDs.length) {
          var maxID = remainingIDs.reduce(function(a, b) {
            return Math.max(a, b);
          });
        } else {
          var maxID = 0;
        };
        this.model.file.set('roi_count', maxID);
      });
    },

    batchDeleteROI() {
      const selectedROIs = this.get('roiRecord.selected');
      const allROIs = this.get('roiRecord.all');

      let selectedIDs = selectedROIs.map(roi => {
          return roi.get('roi_id')
      })

      let allIDs = allROIs.map(roi => {
          return roi.get('roi_id')
      })

      let remainingIDs = allIDs.filter(id => !selectedIDs.includes(id))

      if (remainingIDs.length) {
        var maxID = remainingIDs.reduce(function(a, b) {
          return Math.max(a, b);
        });
      } else {
        var maxID = 0;
      };

      const database = firebase.database();
      const updates = {}
      const wsID = this.model.firebaseWorkspace.id;
      this.set('modalVisibility', true);
      // get pushKeys of rois to delete
      later(this, () => {
        for (var i=0; i<selectedROIs.length; i++) {
          let key = selectedROIs[i].id;
          updates['/rois/' + key] = null;
          updates['/workspaces/' + wsID + '/rois/' + key] = null;
        };
        // push updates to database
        database.ref().update(updates).then(() => {
          this.model.file.set('roi_count', maxID);
          this.set('modalVisibility', false);
        });
      }, 500);
    },

    resync() {
      const allROIs = this.get('roiRecord.all').toArray();
      const database = firebase.database();
      const updates = {}
      const wsID = this.model.firebaseWorkspace.id;
      this.set('syncModalVisibility', true);
      // get pushKeys of rois to delete
      later(this, () => {
        for (var i=0; i<allROIs.length; i++) {
          let roi = allROIs[i]
          let key = roi.id;
          updates['/rois/' + key] = {
            created: roi.get('created'),
            lastComputedPolygon: roi.get('lastComputedPolygon'),
            neuropilPolygon: roi.get('neuropilPolygon'),
            roi_id: roi.get('roi_id'),
            polygon: roi.get('polygon'),
            workspace: roi.get('workspace.id'),
          }
        };
        // push updates to database
        database.ref().update(updates).then(() => {
          this.set('syncModalVisibility', false);
        });
      }, 500);
    },

    deselectAll() {
      this.get('roiRecord.selected').map(function(roi) {
        roi.set('selected', false);
      });
    },

    updateTable(selectedROIs) {
      const store = this.get('store');
      var activeIDs = selectedROIs.map(function(roi) { return roi.get('roi_id'); })
      //this.get('selection').clear();
      if (activeIDs.length) {
        queryParams.reload = true; // make sure roi is reloaded with stats
        for (var i=0; i<activeIDs.length; i++) {
          store.findRecord('roi', activeIDs[i], queryParams).then(roi => {
            //this.get('selection').pushObject(roi); // may use later to display multiple rois
            this.set('selection', [roi]);
            this.model.workspace.set('activeROI', roi);
          });
        };
      } else {
        this.get('selection').clear();
      };
    },

    saveNeuropilConfig() {
      this.model.firebaseWorkspace.save();
    },

    computeSelected() {
      this.toast.info('Computing selected ROIs...');
      var selectedROIs = this.get('roiRecord.selected');
      this.send('computeROIs', selectedROIs);
    },

    computeUncomputed() {
      this.toast.info('Computing any uncomputed ROIs...');
      var uncomputedROIs = this.get('roiRecord.uncomputed');
      this.send('computeROIs', uncomputedROIs);
    },

    computeSelectedStatsOnly() {
      this.toast.info('Computing selected ROIs...');
      var selectedROIs = this.get('roiRecord.selected');
      this.send('computeROIs', selectedROIs, 'refresh_stats_only');
    },

    computeROIs(rois, action='refresh_all') {
      const store = this.get('store');
      const model = this.model
      const workspace = this.model.workspace;

      // Update roi visual states
      rois.forEach(roi => {
        this.get('roiRecord.selected').map(roi => {
          roi.set('selected', false);
        });
        roi.set('lastComputedPolygon', 'inProgress');
        roi.save();
      });

      // Compute rois sequentially
      rois.reduce(function(cur, roi) {
        return cur.then(function() {
          console.log(`Computing roi ${roi.get('roi_id')}`);
          return fillRecordGap(roi);
        });
      }, Ember.RSVP.resolve()).then(function() {
          //setTimeout(function() { modal.modal('hide'); }, 2000);
      });

      var fillRecordGap = (roi) => {
        // First check if entry exists in backend
        return store.findRecord('roi', roi.get('roi_id')).then(roiData => {
          // If entry exists, compute the ROI
          // Update coordinates and neuropil configuration
          var polygon = pointsToArray(roi.get('polygon')).map(function(point) {
            return {x:point[0], y:point[1]};
          });
          var neuropilPolygon = pointsToArray(roi.get('neuropilPolygon')).map(function(point) {
            return {x:point[0], y:point[1]};
          });
          roiData.setProperties({
            'polygon': polygon,
            'neuropil_polygon': neuropilPolygon,
            'neuropil_enabled': model.firebaseWorkspace.get('neuropil_enabled'),
            'neuropil_ratio': model.firebaseWorkspace.get('neuropil_ratio'),
            'neuropil_factor': model.firebaseWorkspace.get('neuropil_factor')
          });
          return roiData.save().then(() => {
            return store.createRecord('action', {
              model_name: 'ROI',
              model_id: roiData.id,
              action_name: action
            }).save().then((action) => {
              if (action.get('status_code') === 500) {
                this.get('toast').error(action.get('status_text'));
                this.get('toast').error(`ROI ${roiData.id} returned an error.`);
                roi.set('lastComputedPolygon', '');
                return roi.save();
              } else {
                //console.log(`Finished computing ${roiData.id}`)
                roi.set('lastComputedPolygon', roi.get('polygon'));
                return roi.save();
              };
            });
          });
        }).catch(error => {
          // If entry does not exist, add entry and then call function again
          var polygon = pointsToArray(roi.get('polygon')).map(function(point) {
            return {x:point[0], y:point[1]};
          });
          var neuropilPolygon = pointsToArray(roi.get('neuropilPolygon')).map(function(point) {
            return {x:point[0], y:point[1]};
          });
          var newRecord = store.createRecord('roi', {
            polygon: polygon,
            workspace: workspace,
            neuropil_polygon: neuropilPolygon,
            neuropil_enabled: model.firebaseWorkspace.get('neuropil_enabled'),
            neuropil_ratio: model.firebaseWorkspace.get('neuropil_ratio'),
            neuropil_factor: model.firebaseWorkspace.get('neuropil_factor')
          })

          return newRecord.save().then(() => {
            return fillRecordGap(roi);
          }).catch(error => {
            debugger;
          });
        });
      }

      function pointsToArray(strPoints) {
        return strPoints.match(/[^,]+,[^,]+/g).map(function(point) {
          return point.split(',').map(Number);
        });
      }
    },

    ensureWorkspace(file, workspace, firebaseWorkspace) {
      const store = this.get('store');
      var roi_count = file.get('roi_count');
      //Ember.run.next(this, getROIs);

      //function getROIs() {
      //  store.findRecord('workspace', workspace.id, { include: 'rois' }).then(result => {
      //  var totalExistingIDs = result.get('rois').get('length')
      //  var neededEntries = roi_count - totalExistingIDs;
      //  // if not, add extra blank entries
      //  if (neededEntries > 0) {
      //    while(neededEntries--) {
      //      var newRecord = store.createRecord('roi', {
      //        polygon: [
      //          {x:0, y:0},
      //          {x:0, y:10},
      //          {x:10, y:10},
      //          {x:10, y:0}
      //        ],
      //        workspace: workspace
      //      });
      //      newRecord.save().then((newRecord) => {
      //        console.log(`Record ${newRecord.id} added`);
      //      });
      //    };
      //  };
      //});
      //}

      // for workspaces that do not have neuropil config, set defaults
      var { neuropil_enabled, neuropil_factor, neuropil_ratio } = firebaseWorkspace.getProperties('neuropil_enabled', 'neuropil_factor', 'neuropil_ratio');
      if (!neuropil_enabled || !neuropil_factor || !neuropil_ratio) {
        firebaseWorkspace.setProperties(
          {
            'neuropil_enabled': false,
            'neuropil_factor': 0.7,
            'neuropil_ratio': 4.0
          }
        );
        firebaseWorkspace.save();
      };

      // ensure firebaseWorkspace reference exists in file
      file.get('workspaces').then(firebaseWorkspaces => {
        if (!firebaseWorkspaces.includes(firebaseWorkspace)) {
          firebaseWorkspaces.addObject(firebaseWorkspace);
          firebaseWorkspaces.save();
          return file.save();
        };
      });
    },

    exportExcel() {
      var computedROIs = this.get('roiRecord').get('computed');
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ids = [];
      const toast = this.toast;
      for (var i=0; i<computedROIs.length; i++) {
        ids.push(computedROIs[i].get('roi_id'));
      }
      const modal = $('.ui.export-progress.modal');
      modal.modal('show');
      this.model.stream.invokeAsBinary('export_excel', ids.join(), ws).then(data => {
        const ts = (new Date).toCustomString();
        download.fromArrayBuffer(data, `${fname}-${ws}-${ts}.xlsx`, 'application/json');
        modal.modal('hide');
      }).catch(reason => {
        modal.modal('hide');
        toast.error(reason); });
    },

    exportMatlab() {
      var computedROIs = this.get('roiRecord').get('computed');
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ids = [];
      const toast = this.toast;
      for (var i=0; i<computedROIs.length; i++) {
        ids.push(computedROIs[i].get('roi_id'));
      }
      const modal = $('.ui.export-progress.modal');
      modal.modal('show');
      this.model.stream.invokeAsBinary('export_matlab', ids.join(), ws).then(data => {
        const ts = (new Date).toCustomString();
        download.fromArrayBuffer(data, `${fname}-${ws}-${ts}.mat`, 'application/json');
      }).catch(reason => {
        modal.modal('hide');
        toast.error(reason); });
    },

    exportBoth() {
      var computedROIs = this.get('roiRecord').get('computed');
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ids = [];
      const toast = this.toast;
      for (var i=0; i<computedROIs.length; i++) {
        ids.push(computedROIs[i].get('roi_id'));
      }
      const modal = $('.ui.export-progress.modal');
      modal.modal('show');
      this.model.stream.invokeAsBinary('export_both', ids.join(), ws).then(data => {
        const ts = (new Date).toCustomString();
        download.fromArrayBuffer(data, `${fname}-${ws}-${ts}.zip`, 'application/json');
        modal.modal('hide');
      }).catch(reason => {
        modal.modal('hide');
        toast.error(reason); });
    },

    exportJSONROIs() {
      var rois = this.get('roiRecord').get('all');
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ts = (new Date).toCustomString();
      var data = rois.map(function(roi) {
        return roi.getProperties('roi_id','polygon','neuropil_enabled',
          'neuropil_ratio','neuropil_factor','neuropil_polygon');
      });
      download(JSON.stringify(data), `${fname}-${ws}-${ts}-rois.json`, 'plain/text');

      function download(text, name, type) {
          var a = document.createElement("a");
          var file = new Blob([text], {type: type});
          a.href = URL.createObjectURL(file);
          a.download = name;
          a.click();
      }
    },

    exportJSONTraces() {
      this.set('exportModalVisibility', true);
      var computedROIs = this.get('roiRecord').get('computed');
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ids = [];
      const toast = this.toast;
      const modal = $('.ui.export-progress.modal');
      for (var i=0; i<computedROIs.length; i++) {
        ids.push(computedROIs[i].get('roi_id'));
      }
      this.model.stream.invokeAsBinary('export_rois_json', ids.join(), ws).then(data => {
        const ts = (new Date).toCustomString();
        download.fromArrayBuffer(data, `${fname}-${ws}-${ts}-traces.json`, 'application/json');
        this.set('exportModalVisibility', false);
      }).catch(reason => {
        this.set('exportModalVisibility', false);
        toast.error(reason); });
    },

    exportJSONAll() {
      this.set('jsonExportModalVisibility', true);
      var computedROIs = this.get('roiRecord').get('computed');
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ids = [];
      const toast = this.toast;
      const modal = $('.ui.export-progress.modal');
      for (var i=0; i<computedROIs.length; i++) {
        ids.push(computedROIs[i].get('roi_id'));
      }
      this.model.stream.invokeAsBinary('export_json_all', ids.join(), ws).then(data => {
        const ts = (new Date).toCustomString();
        download.fromArrayBuffer(data, `${fname}-${ws}-${ts}-all.json`, 'application/json');
        this.set('jsonExportModalVisibility', false);
      }).catch(reason => {
        this.set('jsonExportModalVisibility', false);
        toast.error(reason); });
    },

    exportToMongo(owner, exp_name, project_name, animal, viewing, hemisphere, session_id, acquisition_id) {
      $('#to-mongo').modal('hide');
      this.set('exportMongoVisibility', true);
      const controller = this;
      const {io, ws} = this.model.name;
      const toast = this.toast
      this.model.stream.invokeAsBinary('to_mongo', ws, owner, exp_name, project_name, animal, viewing,
        hemisphere, session_id, acquisition_id).then(data => {
          this.set('exportMongoVisibility', false);
        }).catch(reason => {
          this.set('exportMongoVisibility', false);
          toast.error(reason);
          console.log(reason)
        });
    },

    loadJSONROIs() {
      Ember.$('#roi-import').click();
    },

    loadJSONTraces() {
      Ember.$('#insert-traces').click();
    },

    importJSONROIs(name, e) {
      var dataFile = e.target.files[0];
      const controller = this;
      const fr = new FileReader();
      fr.onload = (/*e*/) => {
        const data = JSON.parse(fr.result);
        var ids = data.map(function(roi) {
          return roi.roi_id;
        });
        var maxID = Math.max(...ids);
        controller.model.file.set('roi_count', maxID);
        controller.model.file.save() // saving roi_count to file to maintain compatibility with sqlite structure
        var modal = $('.ui.roiImport-progress.modal');
        modal.modal('show');

        later(this, () => {
          // create data structure for atomic update const database = firebase.database();
          const database = firebase.database();
          const updates = {}
          const wsID = controller.model.firebaseWorkspace.id;
          for (var i=0; i<data.length; i++) {
            let key = database.ref().child('rois').push().key;
            updates['/rois/' + key] =
              {
                created: firebase.database.ServerValue.TIMESTAMP,
                roi_id: data[i].roi_id,
                polygon: data[i].polygon,
                workspace: wsID
              }
            updates['/workspaces/' + wsID + '/rois/' + key] = true;
          }

          // push updates to database
          database.ref().update(updates).then(() => {
            modal.modal('hide');
          });
        }, 500);
      };
      fr.readAsText(dataFile);
      Ember.$('#roi-import')[0].value = null;
    },

    insertJSONTraces(name, e) {
      var dataFile = e.target.files[0];
      const controller = this;
      const {io, ws} = this.model.name;
      const toast = this.toast
      const fr = new FileReader();
      fr.onload = (/*e*/) => {
        this.set('insertModalVisibility', true);
        const data = JSON.parse(fr.result);
        controller.model.stream.invokeAsBinary('insert_traces_json', data, ws).then(res => {
          this.set('insertModalVisibility', false);
          toast.success('ROI traces updated.')
        }).catch(reason => {
          this.set('insertModalVisibility', false);
          toast.error(reason); });
        };
      fr.readAsText(dataFile);
      Ember.$('#insert-traces')[0].value = null;
    },

    showProjection(name) {
      var maxIndex = this.model.stream.get('img.maxIndex');
      this.setProperties({'start': 0, 'end': maxIndex});
      const modal = $('#projection-prompt');
      modal.modal('show');
    },

    showModal(name) {
      const modal = $('#' + name);
      modal.modal('show');
    },

    createProjection(start, end) {
      const modal = $('#projection-prompt');
      var numFrames = Number(end) - Number(start);
      const stream = this.model.stream;
      this.set('projBusy', true);
      modal.modal('hide');
      this.get('toast').info(`Generating projections with index range ${start} - ${end}. Total frames: ${numFrames}.`)
      //stream.invoke('ch0.generate_projections', start, end).finally(() => {
      //  this.set('projBusy', false);
      //  stream.mirror('ch0.has_maxp', 'ch0.has_meanp', 'ch0.has_sump');
      //});
      stream.invoke('ch0.generate_projections', start, end).then(() => {
        stream.mirror('ch0.has_maxp', 'ch0.has_meanp', 'ch0.has_sump');
        if (stream.matChannels == 1) {
          return stream.invoke('ch1.generate_projections', start, end).finally(() => {
            this.set('projBusy', false);
            stream.mirror('ch1.has_maxp', 'ch1.has_meanp', 'ch1.has_sump');
          });
        } else {
          this.set('projBusy', false);
        };
      });
    },

    overlayProjection(type) {
      this.toast.info(`Overlaid ${type} projection image.`);
      this.model.stream.overlayProjection(type);
    },

    exportProjection(type) {
      const {io, ws} = this.model.name;
      let fname = io.split('.')[0];
      fname = fname.split('/').slice(-1)[0]
      const ts = (new Date).toCustomString();
      const channels = this.model.stream.get('img.channelOptions')
      switch (type) {
        case 'max':
          this.toast.info('Exporting max projection image...');
          if (channels.contains('Both')) {
            this.model.stream.requestMaxPITiff('ch0').then(data => {
              let zip = new JSZip();
              zip.file(
                `${fname}_green-${ws}-${ts}-max-projection.tif`,
                data,
                {base64: true}
              );
              this.model.stream.requestMaxPITiff('ch1').then(data => {
                zip.file(
                  `${fname}_red-${ws}-${ts}-max-projection.tif`,
                  data,
                  {base64: true}
                );
                zip.generateAsync({type:"arraybuffer"})
                .then(function(content) {
                  download.fromArrayBuffer(content, `${fname}-${ws}-${ts}-max-projection.zip`);
                });
              });
            });
          } else {
            this.model.stream.requestMaxPITiff('ch0').then(data => {
              download.fromArrayBuffer(data, `${fname}-${ws}-${ts}-max-projection.tif`, 'image/tiff');
            });
          }
          break;
        case 'mean':
          this.toast.info('Exporting max projection image...');
          if (channels.contains('Both')) {
            this.model.stream.requestMeanPITiff('ch0').then(data => {
              let zip = new JSZip();
              zip.file(
                `${fname}_green-${ws}-${ts}-mean-projection.tif`,
                data,
                {base64: true}
              );
              this.model.stream.requestMeanPITiff('ch1').then(data => {
                zip.file(
                  `${fname}_red-${ws}-${ts}-mean-projection.tif`,
                  data,
                  {base64: true}
                );
                zip.generateAsync({type:"arraybuffer"})
                .then(function(content) {
                  download.fromArrayBuffer(content, `${fname}-${ws}-${ts}-mean-projection.zip`);
                });
              });
            });
          } else {
            this.model.stream.requestMeanPITiff('ch0').then(data => {
              download.fromArrayBuffer(data, `${fname}-${ws}-${ts}-mean-projection.tif`, 'image/tiff');
            });
          }
          break;
        case 'sum':
          this.toast.info('Exporting max projection image...');
          if (channels.contains('Both')) {
            this.model.stream.requestSumPITiff('ch0').then(data => {
              let zip = new JSZip();
              zip.file(
                `${fname}_green-${ws}-${ts}-sum-projection.tif`,
                data,
                {base64: true}
              );
              this.model.stream.requestSumPITiff('ch1').then(data => {
                zip.file(
                  `${fname}_red-${ws}-${ts}-sum-projection.tif`,
                  data,
                  {base64: true}
                );
                zip.generateAsync({type:"arraybuffer"})
                .then(function(content) {
                  download.fromArrayBuffer(content, `${fname}-${ws}-${ts}-sum-projection.zip`);
                });
              });
            });
          } else {
            this.model.stream.requestSumPITiff('ch0').then(data => {
              download.fromArrayBuffer(data, `${fname}-${ws}-${ts}-sum-projection.tif`, 'image/tiff');
            });
          }
          break;
        default:
          return;
      };
    },

    setCmap(cmap) {
      this.model.stream.set('img.cmap', cmap);
      this.toast.info(`Colormap changed to ${cmap}`);
    },

    setChannel(channel) {
      this.model.stream.set('img.channelDisplay', channel);
      this.toast.info(`Channel display set to ${channel}`);
    },

    updateGreenMin(event) {
      let min = this.model.stream.get('img.min');
      if (event.key == "ArrowDown" && min > 0) {
        this.model.stream.set('img.min', parseInt(min) - 20)
      }
      if (event.key == "ArrowUp" && min < 65535) {
        this.model.stream.set('img.min', parseInt(min) + 20)
      }
    },

    updateGreenMax(event) {
      let max = this.model.stream.get('img.max');
      if (event.key == "ArrowDown" && max > 0) {
        this.model.stream.set('img.max', parseInt(max) - 20)
      }
      if (event.key == "ArrowUp" && max < 65535) {
        this.model.stream.set('img.max', parseInt(max) + 20)
      }
    },

    updateRedMin(event) {
      let red_min = this.model.stream.get('img.red_min');
      if (event.key == "ArrowDown" && red_min > 0) {
        this.model.stream.set('img.red_min', parseInt(red_min) - 20)
      }
      if (event.key == "ArrowUp" && red_min < 65535) {
        this.model.stream.set('img.red_min', parseInt(red_min) + 20)
      }
    },

    updateRedMax(event) {
      let red_max = this.model.stream.get('img.red_max');
      if (event.key == "ArrowDown" && red_max > 0) {
        this.model.stream.set('img.red_max', parseInt(red_max) - 20)
      }
      if (event.key == "ArrowUp" && red_max < 65535) {
        this.model.stream.set('img.red_max', parseInt(red_max) + 20)
      }
    }

    //updateFrameShift() {
    //  const current = this.model.workspace.get('params.frame_shift');
    //  const url = "https://docs.scipy.org/doc/numpy-1.12.0/reference/generated/numpy.roll.html"
    //  const message = `<p>Please specify an integer to pass into the function
    //    <a href="${url}" target="_blank">np.roll</a></p>
    //    <p>This will apply to an initial trace of an ROI.
    //       And then "recompute" will make the trace chopped along with all trials.</p>`;
    //  swal({
    //    title: 'Frame Shift',
    //    html: message,
    //    input: 'number',
    //    inputValue: current,
    //    showCancelButton: true,
    //    inputClass: 'ui input',
    //    inputValidator: function (value) {
    //      return new Promise(function (resolve, reject) {
    //        if (value && isFinite(value) && !isNaN(value)) {
    //          resolve()
    //        } else {
    //          reject(`Cannot send the value "${value}".`)
    //        }
    //      })
    //    }
    //  }).then(result => {
    //    const shift = parseInt(result);
    //    const ws = this.model.workspace;
    //    const params = ws.get('params');
    //    ws.set('params', { ...params, frame_shift: shift});
    //    ws.save().then(() => {
    //      swal({
    //        type: 'success',
    //        title: 'Update success!',
    //        text: 'To take effect, recompute desired ROIs.',
    //      })
    //    });
    //  }).catch(swal.noop);
    //}
  }
});
