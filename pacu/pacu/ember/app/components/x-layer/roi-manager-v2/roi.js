import Component from '@ember/component';
import Ember from 'ember';
import { observer, computed } from '@ember/object';
import { on } from "@ember/object/evented";
import scalePoly from 'pacu-v2/utils/poly-scale';

// filter array by mask
Array.prototype.maskFilter = function(mask) {
  return this.filter((item, i) => mask[i]);
}

// point string array to number array
function pointsToArray(strPoints) {
  if (!strPoints) {
    return [];
  };
  return strPoints.match(/[^,]+,[^,]+/g).map(function(point) {
    return point.split(',').map(Number);
  });
}

function getNeuropilPoints(strPoints, ratio) {
  var points = pointsToArray(strPoints).map(function(point) { return { x: point[0], y: point[1] };
  });
  var neuropilPoints = scalePoly(points, ratio).map(function(point) {
    return [Math.round(point.x), Math.round(point.y)].join()
  }).join();
  return neuropilPoints;
}

export default Component.extend({
  tagName: 'svg',
  classNameBindings: ['visible::hidden'],
  inProgress: computed.equal('lastComputedPoints', 'inProgress'),
  computed: computed('points','lastComputedPoints', 'selected', function() {
    return (this.get('points') == this.get('lastComputedPoints')) && !this.get('inProgress') && !this.get('selected');
  }),
  neuropilChanged: Ember.observer('points', 'neuropilRatio', 'neuropilEnabled', function() {
    var { points, neuropilRatio } = this.getProperties('points', 'neuropilRatio')
    var neuropilPoints = getNeuropilPoints(points, neuropilRatio);
    // necessary to ensure model is updated
    Ember.run.schedule('actions', this, () => {
      this.set('neuropilPoints', neuropilPoints);
    });
  }),
  propertyChanged: observer('points', 'neuropilPoints', 'lastComputedPoints', function() {
    // need to pass in neuropilPoints because setting this property via observer doesn't update model
    Ember.run.debounce(this, 'triggerUpdate', 500);
  }),

  didInsertElement() {
    // ensure neuropil is set on creation of roi
    var { points, neuropilRatio } = this.getProperties('points', 'neuropilRatio')
    var neuropilPoints = getNeuropilPoints(points, neuropilRatio);
    this.set('neuropilPoints', neuropilPoints);
  },

  mouseEnter(e) {
    this.set('hover', true);
  },

  mouseLeave(e) {
    this.set('hover', false);
  },

  mouseDown(e) {
    // if in placeMode or clicking in neuropil, ignore mouseDown
    if (this.get('placeMode') || e.target.classList.contains('neuropil')) {
      return;
    }

    // if handles are disabled, skip hit test
    if (!this.get('disableHandles')) {
      var hitResult = this.hitTest(e, e.target);
    }

    // if pressing the metaKey while clicking in fill, select roi
    if (e.metaKey && !hitResult) {
      e.stopPropagation();
      this.toggleProperty('selected');
      return;
    }

    // if holding shiftKey while selecting vertex, delete vertex
    if (event.shiftKey && hitResult) {
      e.stopPropagation();
      if (hitResult.type == 'vertexHit') {
        var points = pointsToArray(this.get('points'));
        points.splice(hitResult.index, 1);
        this.set('points', points.join());
        return;
      } else {
        return;
      }
    }

    if (!hitResult) {
      return;
    };

    if (hitResult.type == 'strokeHit') {
      //var offset = $('svg').select().offset();
      //var offsetX = e.clientX - offset.left;
      //var offsetY = e.clientY - offset.top;
      //var newPoint = [offsetX, offsetY];
      var newPoint = [e.offsetX, e.offsetY];
      var points = pointsToArray(this.get('points'));
      points.insertAt(hitResult.index, newPoint.join());
      //this.set('targetPoint', hitResult.index);
      this.set('points', points.join());
    };
    this.set('targetPoint', hitResult.index);
  },

  hitTest(e, element) {
    // check for hit on vertex
    var vertexPoints = [];
    for (var i=0; i < element.points.length; i++) {
      vertexPoints.push(element.points[i]);
    };
    var vertexPointList = vertexPoints.map(
      function(p) { return [p.x, p.y]; }
    );
    // if there is a hit on vertex, return vertex
    var tol = 3;
    var vertexHit = vertexPoints.maskFilter(vertexPoints.map(
        function(x) { return checkPoint(e, x, tol); }
      )
    );
    if (vertexHit[0]) {
      var vertexPointVals = vertexPoints.map(
        function(p) { return [p.x, p.y].join(); }
      );
      var index = vertexPointVals.indexOf([vertexHit[0].x, vertexHit[0].y].join());
      return {'type': 'vertexHit',
              'index': index};
    }

    // check for hit on stroke
    var strokePoints = [];
    for (var i=0; i <= element.getTotalLength(); i++) {
        strokePoints.push(element.getPointAtLength(i));
    }
    // if there is a hit on the stroke, return index for new vertex
    var strokeHit = strokePoints.maskFilter(strokePoints.map(
        function(x) { return checkPoint(e, x, tol); }
      )
    );
    strokeHit = strokeHit[0]
    if (strokeHit) {
      var strokePointVals = strokePoints.map(
        function(p) { return [p.x, p.y].join(); }
      );
      var vertexPositions = vertexPoints.map(
        function(point) {
          for (var i=0; i<strokePoints.length; i++) {
            if (isClose(point.x, strokePoints[i].x, 1) && isClose(point.y, strokePoints[i].y, 1)) {
              return i;
            }
          }
        }
      );
      var hitPosition = strokePointVals.indexOf([strokeHit.x, strokeHit.y].join());
      vertexPositions.push(hitPosition);
      vertexPositions.sort((a, b) => (a - b));
      var index = vertexPositions.indexOf(hitPosition);
      return {'type': 'strokeHit',
              'index': index};
    };

    function checkPoint(event, point, tol) {
     // var offset = $('svg').select().offset();
     // var offsetX = event.clientX - offset.left;
     // var offsetY = event.clientY - offset.top;
      var offset = {
        x: event.offsetX,
        y: event.offsetY
      };
      var dist = Math.sqrt(
              Math.pow(offset.x - point.x, 2)
            + Math.pow(offset.y - point.y, 2)
      );
      //var dist = Math.sqrt(
      //        Math.pow(offsetX - point.x, 2)
      //      + Math.pow(offsetY - point.y, 2)
      //);
      if (dist <= tol) {
          return true;
      } else {
          return false;
      }
    }

    function isClose(val, testVal, tol) {
        return testVal > val-tol && testVal < val+tol;
    }
  },
});
