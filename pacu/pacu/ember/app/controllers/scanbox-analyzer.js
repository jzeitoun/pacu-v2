import Ember from 'ember';
import Controller from '@ember/controller';
import { inject as service } from '@ember/service';
import download from 'pacu-v2/utils/download';
import batch from 'pacu-v2/utils/batch';

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

function importROIFileAllChanged(e) { // `this` is the current route
  const input = e.target;
  const route = this;
  const file = e.target.files[0];
  const fr = new FileReader();
  fr.onload = (/*e*/) => {
    const data = JSON.parse(fr.result);
    let news;
    try {
      news = data.rois;
      news.forEach(r => {
        const roi = route.store.createRecord('roi', r.attrs);
        roi.set('workspace', route.currentModel.workspace);
        roi.save();
      });
    } catch(e) {
      console.log(e);
      this.toast.warning('Invalid file');
    } finally {
      this.toast.info(`${news.length} ROI(s) imported.`);
      Ember.$(input).val(null);
    }
  }
  fr.readAsText(file);
}

function importROIFileDiffChanged(e) { // `this` is the current route
  const input = e.target;
  const route = this;
  const file = e.target.files[0];
  const fr = new FileReader();
  fr.onload = (/*e*/) => {
    const data = JSON.parse(fr.result);
    let news;
    try {
      const entry = this.model.workspace.get('loadedROIs').getEach('params.cell_id').compact();
      news = data.rois.filterBy('attrs.params.cell_id').filter(roi => {
        return !entry.includes(roi.attrs.params.cell_id);
      });
      news.forEach(r => {
        const roi = route.store.createRecord('roi', r.attrs);
        roi.set('workspace', route.currentModel.workspace);
        roi.save();
      });
    } catch(e) {
      console.log(e);
      this.toast.warning('Invalid file');
    } finally {
      this.toast.info(`${news.length} ROI(s) imported.`);
      Ember.$(input).val(null);
    }
  }
  fr.readAsText(file);
}
export default Controller.extend({
  init() {
    this._super(...arguments);
    this.set('selection', []);
  },
  roiRecord: service(),
  actions: {
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
      roi.deleteRecord();
      roi.save()
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

    computeROIs(rois, workspace) {
      var store = this.get('store');
      //var singleROIData = store.findRecord('roi-data', 1);
      var roiData = store.findAll('roi').then(result => {
        var roiDataObjects = result.toArray();
        var existingIDs = roiDataObjects.map(function(roi) {
          return Number(roi.id);
        });
        rois.forEach(function(roi) {
          if (!(roi.get('polygon') == roi.get('lastComputedPolygon'))) {
            roi.set('lastComputedPolygon', 'inProgress');
            roi.save();
          };
        });
        rois.forEach(function(roi) {
          // if roi is already computed, skip
          if (roi.get('polygon') == roi.get('lastComputedPolygon')) {
            return;
          };
          // create sqlite record if none exists
          if (!existingIDs.includes(roi.get('roi_id'))) {
            //console.log(existingIDs);
            //console.log(roi.get('roi_id'));
            var polygon = pointsToArray(roi.get('polygon')).map(function(point) {
              return {x:point[0], y:point[1]};
            });
            var newRecord = store.createRecord('roi', {
              polygon: polygon,
              workspace: workspace
            });
            // compute
            newRecord.save().then(() => {
              newRecord.refreshAll().then(() => {
                roi.set('lastComputedPolygon', roi.get('polygon'));
              });
            });
          } else {
            // record exists, skip to compute
            var roiData = roiDataObjects.filterBy('id', String(roi.get('roi_id'))).get('firstObject');
            // update coordinates
            var polygon = pointsToArray(roi.get('polygon')).map(function(point) {
              return {x:point[0], y:point[1]};
            });
            roiData.set('polygon', polygon);
            roiData.save();
            return store.createRecord('action', {
              model_name: 'ROI',
              model_id: roiData.id,
              action_name: 'refresh_all'
            }).save().then((action) => {
              if (action.get('status_code') === 500) {
                //console.log(`ROI ${roiData.id} returned an error.`);
                //this.get('toast').error(action.get('status_text'));
              } else {
                //console.log(`Finished computing ${roiData.id}`)
              };
            }).finally(() => {
              roi.set('lastComputedPolygon', roi.get('polygon'));
              roi.save();
            });
          }
        });
      });

      function pointsToArray(strPoints) {
        return strPoints.match(/[^,]+,[^,]+/g).map(function(point) {
          return point.split(',').map(Number);
        });
      }
    },

    ensureWorkspace(file, workspace, firebaseWorkspace) {
      const store = this.get('store');
      var roi_count = file.get('roi_count');
      var roiData = store.findAll('roi').then(result => {
        var roiDataObjects = result.toArray();
        var existingIDs = roiDataObjects.map(function(roi) {
          return Number(roi.id);
        });
        // check if number of database entries matches firebase roi_count
        if (existingIDs.length) {
          var neededEntries = roi_count - Math.max(...existingIDs);
          // if not, add extra blank entries
          if (neededEntries > 0) {
            while(neededEntries--) {
              var newRecord = store.createRecord('roi', {
                polygon: [
                  {x:0, y:0},
                  {x:0, y:10},
                  {x:10, y:10},
                  {x:10, y:0}
                ],
                workspace: workspace
              });
              newRecord.save().then((newRecord) => {
                console.log(`Record ${newRecord.id} added`);
              });
            };
          };
        };
      });
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
      debugger;
      const {io, ws} = this.model.name;
      const fname = io.split('.')[0];
      const ids = [];
      for (var i=0; i<computedROIs.length; i++) {
        ids.push(computedROIs[i].get('roi_id'));
      }
      console.log(ids);
      this.toast.info(`Exporting data as Excel...`);
      this.model.stream.invokeAsBinary('export_excel', ids.join(), ws).then(data => {
        const ts = (new Date).toCustomString();
        download.fromArrayBuffer(data, `${fname}-${ws}-${ts}.xlsx`, 'application/json');
      }).catch(reason => { debugger; });
    },

    updateModel(model) {
      return model.save().then(() => {
        const name = model.constructor.modelName;
        const id = model.get('id');
        return this.toast.info(`${name} #${id} updated.`);
      });
    },

    deleteModel(model) {
      return model.destroyRecord().then(() => {
        const name = model.constructor.modelName;
        const id = model.get('id');
        return this.toast.info(`${name} #${id} deleted.`);
      });
    },

    exportROIs() {
      this.toast.info('Export ROIs...');
      const url = '/api/json/scanbox_manager/rois_exported';
      const name = this.model.name;
      Ember.$.get(url, name).then(data => {
        const ts = +(new Date);
        download.fromByteString(data, `${ts}-${name.io}-${name.ws}-rois.json`, 'application/json');
      });
    },

    importROIsAll() {
      Ember.$('#roi-import-file-all').click();
    },

    importROIsDiff() {
      Ember.$('#roi-import-file-diff').click();
    },

    reloadTracePlot() {
      this.toast.info('Update traces...');
      this.model.workspace.get('dtoverallmeans').reload();
    },

    initMPI() {
      const stream = this.model.stream;
      this.set('maxpBusy', true);
      stream.invoke('ch0.create_maxp').finally(() => {
        this.set('maxpBusy', false);
        stream.mirror('ch0.has_maxp');
      });
    },

    overlayMPI() {
      this.toast.info('Locating max projection image...');
      this.model.stream.overlayMPI();
    },

    exportMPI() {
      this.toast.info('Exporting max projection image...');
      const wid = this.model.workspace.id;
      this.model.stream.requestMPITiff().then(data => {
        const ts = +(new Date);
        download.fromArrayBuffer(data, `${ts}-${wid}-max-projection.tiff`, 'image/tiff');
      });
    },

    exportSFreqFitDataAsMat(roi) {
      const wid = this.model.workspace.id;
      const rid = roi.id;
      const contrast = this.model.workspace.get('cur_contrast');
      this.model.stream.invokeAsBinary(
      'export_sfreqfit_data_as_mat', wid, rid, contrast
      ).then(data => {
        const ts = +(new Date);
        download.fromArrayBuffer(data, `${ts}-${wid}-${rid}-sfreqfit.mat`, 'application/json');
      });
    },

    exportROITracesAsMat() {
      const wid = this.model.workspace.id;
      this.model.stream.invokeAsBinary(
      'export_traces_as_mat', wid
      ).then(data => {
        const ts = +(new Date);
        download.fromArrayBuffer(data, `${ts}-${wid}-traces.mat`, 'application/json');
      });
    },

    computeAll() {
      const rois = this.model.workspace.get('loadedROIs');
      batch.promiseSequence(rois, 'refreshAll').then(() => {
        this.toast.info('Batch process complete!');
      });
    },

    setCmap(cmap) {
      this.model.stream.set('img.cmap', cmap);
      this.toast.info(`Colormap changed to ${cmap}`);
    },

    neuropilOnAll() {
      const rois = this.model.workspace.get('loadedROIs');
      batch.promiseSequence(rois, 'enableNeuropil').then(() => {
        this.toast.info('Batch process complete!');
      });
    },

    neuropilOffAll() {
      const rois = this.model.workspace.get('loadedROIs');
      batch.promiseSequence(rois, 'disableNeuropil').then(() => {
        this.toast.info('Batch process complete!');
      });
    },

    neuropilRValueAll() {
      const rois = this.model.workspace.get('loadedROIs');

      const factor = prompt("Please enter neuropil R value",
        this.get('neuropil_factor'));
      const fFactor = parseFloat(factor);
      if (isNaN(fFactor)) {
        this.get('toast').warning(`Invalid value ${factor}.`);
      } else {
        rois.setEach('neuropil_factor', fFactor);
        batch.promiseSequence(rois, 'save').then(() => {
          this.toast.info('Batch process complete!');
        });
      }
    },

    //Added by RA.
    //Listenes to state o the ROI toggle and changes a bool representing desired ROI visibility to pass to roi-manager
    changeVisibilityROIs() {
      this.set('toggleROIs', !this.get('toggleROIs'));
    },

    //Added by RA.
    //Responds to selecton in Display Mode dropdown and changes a bool representing if should display minimal or full features. true is minimal. 
    //Passes infor ro roi-manager. Should be updated to pass string for >2 options.
    changeModeROIs(mode){
      this.set('MinModeROIs', mode);
      console.log(mode);
    },

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
