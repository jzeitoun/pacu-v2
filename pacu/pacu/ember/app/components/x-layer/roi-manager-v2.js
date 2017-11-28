import Ember from 'ember';
import firebase from 'firebase';

// filter array by mask
Array.prototype.maskFilter = function(mask) {
  return this.filter((item, i) => mask[i]);
}

// point string array to number array
function pointsToArray(strPoints) {
  return strPoints.match(/[^,]+,[^,]+/g).map(function(point) {
    return point.split(',').map(Number);
  });
}

export default Ember.Component.extend({
  store: Ember.inject.service(),
  roiRecord: Ember.inject.service(),
  tagName: 'svg',
  classNameBindings: ['placeMode'],
  attributeBindings: ['height', 'width'],
  neuropilChanged: Ember.observer('neuropilRatio', 'neuropilFactor', 'neuropilEnabled', function() {
    this.get('updateNeuropil')();
  }),
  selectRect: {
    origin: {
      x: null,
      y: null,
    },
    x: null,
    y: null,
    length: null,
    width: null,
  },
  activeROIChanged: Ember.observer('activeID', function() {
    var rois = this.get('rois');
    var activeROI = rois.filterBy('roi_id', Number(this.get('activeID'))).get('firstObject');
    if (activeROI) {
      activeROI.set('selected', true);
      this.get('updateTable')([activeROI]);
      console.log('active ID changed');
    }
  }),
  selectedROIs: Ember.computed.filterBy('rois', 'selected', true),
  computedROIs: Ember.computed.filterBy('rois', 'computed', true),
  uncomputedROIs: Ember.computed.filterBy('rois', 'computed', false),
  draggedROIs: Ember.computed.filterBy('rois', 'dragging', true),
  targetedROI: Ember.computed.filter('rois.@each.targetPoint', function(roi, index, array) {
    return typeof(roi.get('targetPoint')) == "number";
  }),
  roiPrototype: {
    centroid: {x: null, y: null},
    radius: 10,
    numPoints: 6,
    points: null,
  },
  lastPosition: {
    x: null,
    y: null,
  },
  prototypeChanged: Ember.observer(
      'placeMode',
      'roiPrototype.{radius,numPoints}',
      'roiPrototype.centroid.{x,y}',
    function() { this.updatePrototype(); }
  ),

  actions: {
    triggerUpdate(roi_id) {
      var roi = this.get('rois').filterBy('roi_id', roi_id).get('firstObject');
      this.get('update')(roi);
    },

    computeSelected() {
      this.get('compute')(this.get('selectedROIs'));
    },

    computeUncomputed() {
      this.get('compute')(this.get('uncomputedROIs'));
    },

    computeAll() {
      this.get('compute')(this.get('rois'));
    }
  },

  didInsertElement() {
    // use service to keep a record of roi states
    this.get('roiRecord').set('all', this.get('rois'));
    // ensure workspace is linked to file
    this.get('ensureWorkspace')(this.get('file'), this.get('workspace'), this.get('firebaseWorkspace'));
  },

  mouseDown(e) {
    // add new ROI
    if (this.get('placeMode')) {
      this.incrementProperty('curID');
      this.get('add')(
        {
          created: firebase.database.ServerValue.TIMESTAMP,
          workspace: this.get('firebaseWorkspace'),
          roi_id: this.get('curID'),
          polygon: this.get('roiPrototype.points')
        }, this.get('file'), this.get('firebaseWorkspace'));
      return;
    } else if (e.target.classList.contains('neuropil')) {
      return;
    };

    var newPos = this.get('roiPrototype.centroid');
    this.set('lastPosition.x', newPos.x);
    this.set('lastPosition.y', newPos.y);

    // initiate single point drag
    var targetedROI = this.get('targetedROI')[0];
    if (targetedROI) {
      targetedROI.set('pointdrag', true);
      return;
    };

    // if clicking within an ROI, start drag
    if (e.target.tagName == 'polygon') {
      var selectedROIs = this.get('selectedROIs');
      if (e.target.classList.contains('selected')) {
        selectedROIs.map(function(roi) {
          roi.set('dragging', true);
        })
      } else {
        selectedROIs.map(function(roi) {
          roi.set('selected', false);
        })
        var draggedROI = this.get('rois').filterBy('roi_id', Number(e.target.dataset['roiId']))[0];
        draggedROI.set('dragging', true);
      }
    } else {
      // starting rectangular selection
      this.set('selectRect.origin.x', this.get('roiPrototype.centroid.x'));
      this.set('selectRect.origin.y', this.get('roiPrototype.centroid.y'));
      this.set('selectRect.height', 0);
      this.set('selectRect.widht', 0);
      this.set('selectRect.x', this.get('selectRect.x'));
      this.set('selectRect.y', this.get('selectRect.y'));
      this.set('selectMode', true);
      // deselect all rois
      this.get('selectedROIs').map(function(roi) {
        roi.set('selected', false);
      })
    }

    function generateID(rois) {
      var curIDs = rois.toArray().map(
        function(roi) { return roi.get('roi_id'); }
      );
      for (var i=1; i<1000; i++) {
        if (!curIDs.includes(i)) {
          return i;
        }
      }
    }
  },

  mouseUp(e) {
    if (!this.get('placeMode') && !this.get('selectMode')) {
      this.get('rois').toArray().map(function(roi) {
        roi.set('dragging', false);
        roi.set('pointdrag', false);
        roi.set('targetPoint', null);
      });
      if (e.target.tagName == 'polygon' && !e.target.classList.contains('neuropil')) {
        var clickedROI = this.get('rois').filterBy('roi_id', Number(e.target.dataset['roiId']))[0];
        clickedROI.set('selected', true);
        this.set('activeID', clickedROI.get('roi_id'));
        //this.get('updateTable')([clickedROI]);
        console.log(`Plotting ROI ${clickedROI.get('roi_id')}`);
      };
    };
    this.set('selectMode', false);
  },

  mouseEnter(e) { // add key listener when hovering over canvas
    Ember.$(document).off("keydown");  // this ensures there is only one bound listener
    Ember.$(document).on("keydown", e => {
      var radius = this.get('roiPrototype.radius');
      var numPoints = this.get('roiPrototype.numPoints');
      //console.log(e.key);
      e.preventDefault();
      switch (e.key) {
        case 'ArrowLeft':
          if (this.get('placeMode')) {
            this.set('roiPrototype.numPoints', numPoints-1);
          } else {
            this.get('selectedROIs').forEach(function(roi) {
              var newPoints = pointsToArray(roi.get('polygon')).map(function(point) {
                return [point[0]-1, point[1]];
              });
              roi.set('polygon', newPoints.join());
            });
          };
          break;
        case 'ArrowRight':
          if (this.get('placeMode')) {
            this.set('roiPrototype.numPoints', numPoints+1);
          } else {
            this.get('selectedROIs').forEach(function(roi) {
              var newPoints = pointsToArray(roi.get('polygon')).map(function(point) {
                return [point[0]+1, point[1]];
              });
              roi.set('polygon', newPoints.join());
            });
          };
          break;
        case 'ArrowDown':
          if (this.get('placeMode')) {
            this.set('roiPrototype.radius', radius-1);
          } else {
            this.get('selectedROIs').forEach(function(roi) {
              var newPoints = pointsToArray(roi.get('polygon')).map(function(point) {
                return [point[0], point[1]+1];
              });
              roi.set('polygon', newPoints.join());
            });
          };
          break;
        case 'ArrowUp':
          if (this.get('placeMode')) {
            this.set('roiPrototype.radius', radius+1);
          } else {
            this.get('selectedROIs').forEach(function(roi) {
              var newPoints = pointsToArray(roi.get('polygon')).map(function(point) {
                return [point[0], point[1]-1];
              });
              roi.set('polygon', newPoints.join());
            });
          };
          break;
        case 'm':
          this.toggleProperty('placeMode');
          break;
        case 'n':
          this.toggleProperty('neuropilEnabled');
          break;
        case 'd':
          this.toggleProperty('disableHandles');
          var disableHandles = this.get('disableHandles');
          break;
        case 'Delete':
          this.get('selectedROIs').map(this.get('delete'));
          break;
        case 'Backspace':
          this.get('selectedROIs').map(this.get('delete'));
          break;
        case 'a':
          if (e.metaKey) {
            this.get('rois').map(roi => {
              roi.set('selected', true);
            });
          };
          break;
        default:
          return false;
      }
    });
  },

  mouseLeave(e) { // removes key listener when not hovering over canvas
    // prevents removal of listener when lifting pen tablet (Wacom)
    var width = Number(this.get('width'));
    var height = Number(this.get('height'));
    var xOut = e.offsetX > width || e.offsetX < 0;
    var yOut = e.offsetY > height || e.offsetY < 0;
    if (xOut || yOut) {
      Ember.$(document).off("keydown");
    }
  },

  mouseMove(e) { // update centroid for roi protoype
    var offset = $('svg').select().offset();
    var docOffset = document.getElementById('ember927');
    var newPos = {
      //x: Math.round(e.pageX - offset.left),
      //y: Math.round(e.pageY - offset.top)
      x: Math.round(e.offsetX),
      y: Math.round(e.offsetY),
    };
    var clientPos = {
      x: Math.round(e.clientX - offset.left),
      y: Math.round(e.clientY - offset.top)
    };
    //console.log(`Event Offset: ${e.offsetX},${e.offsetY}`);
    //console.log(`Client: ${e.clientX},${e.clientY}`);
    //console.log(`Client Pos: ${clientPos.x},${clientPos.y}`);
    //console.log(`Page: ${e.pageX},${e.pageY}`);
    //console.log(`Page Pos: ${newPos.x},${newPos.y}`);
    this.set('roiPrototype.centroid.x', newPos.x);
    this.set('roiPrototype.centroid.y', newPos.y);
    var lastPos = this.get('lastPosition');

    // drag all selected ROIs
    var draggedROIs = this.get('draggedROIs');
    if (!draggedROIs.length == 0) {
      draggedROIs.map(function(roi) {
        updatePositions(lastPos, newPos, roi)
      })
    }

    // drag selected point
    var targetedROI = this.get('targetedROI')[0];
    if (targetedROI) {
      updatePoint(lastPos, newPos, targetedROI);
    }

    this.set('lastPosition.x', newPos.x);
    this.set('lastPosition.y', newPos.y);

    // expand selection rectangle
    if (this.get('selectMode')) {
      var rect = {};
      rect.y = this.get('selectRect.origin.y');
      rect.x = this.get('selectRect.origin.x');
      rect.height = newPos.y - rect.y;
      rect.width = newPos.x - rect.x;
      if ( rect.width < 0) {
        this.set('selectRect.x', newPos.x)
        this.set('selectRect.width', Math.abs(rect.width));
      } else {
        this.set('selectRect.x', rect.x)
        this.set('selectRect.width', rect.width);
      }
      if (rect.height < 0) {
        this.set('selectRect.y', newPos.y)
        this.set('selectRect.height', Math.abs(rect.height));
      } else {
        this.set('selectRect.y', rect.y)
        this.set('selectRect.height', rect.height);
      }
      this.selectUnderlyingElements(rect, newPos)
    }

    function updatePositions(lastPos, newPos, roi) {
      var deltaX = newPos.x - lastPos.x;
      var deltaY = newPos.y - lastPos.y;
      var points = pointsToArray(roi.get('polygon'));
      var newPoints = points.map(
        function(point) {
          return [point[0] + deltaX, point[1] + deltaY]
      })
      roi.set('polygon', newPoints.join())
    }

    function updatePoint(lastPos, newPos, roi) {
      var deltaX = newPos.x - lastPos.x;
      var deltaY = newPos.y - lastPos.y;
      var points = pointsToArray(roi.get('polygon'));
      var point = points[roi.get('targetPoint')];
      var newPoint = [point[0] + deltaX, point[1] + deltaY]
      points[roi.get('targetPoint')] = newPoint
      roi.set('polygon', points.join())
    }
  },

  selectUnderlyingElements(rect, newPos) {
    var x1 = Math.min(rect.x, newPos.x);
    var x2 = Math.max(rect.x, newPos.x);
    var y1 = Math.min(rect.y, newPos.y);
    var y2 = Math.max(rect.y, newPos.y);
    // deselect all rois
    this.get('selectedROIs').map(function(roi) {
      roi.set('selected', false);
    });
    // determmine if any points from each roi are within the selection
    var rois = this.get('rois');
    var selectionMask = rois.toArray().map(
      function(roi) {
        var pointsInRange = [];
        var points = pointsToArray(roi.get('polygon'));
        for (var i=0; i<points.length; i++) {
          var point = points[i];
          var xInRange = (point[0] > x1 && point[0] < x2);
          var yInRange = (point[1] > y1 && point[1] < y2);
          pointsInRange.push(xInRange && yInRange);
        }
        return pointsInRange.some(
                  function(element) { return element == true; }
        );
      }
    );
    var selection = rois.toArray().maskFilter(selectionMask);
    selection.map(function(roi) {
      roi.set('selected', true);
    });
  },

  updatePrototype() {
    // triggered on change in placeMode, centroid, radius, or numPoints
    var roiPrototype = this.get('roiPrototype');
    this.set('roiPrototype.points', generateCircularPoints(
                                      roiPrototype.centroid,
                                      roiPrototype.radius,
                                      roiPrototype.numPoints
                                    )
    );

    function generateCircularPoints(centroid, radius, numPoints) {
        var points = [];
        var theta = 2*Math.PI/numPoints;
        for (var i=1; i<=numPoints; i++) {
          var x = radius * Math.cos(theta*i-(Math.PI/2))
          var y = radius * Math.sin(theta*i-(Math.PI/2))
          points.push(
            [centroid.x + Math.round(x), centroid.y + Math.round(y)].join()
          )
        };
        return points.join();
      }
  },

});

