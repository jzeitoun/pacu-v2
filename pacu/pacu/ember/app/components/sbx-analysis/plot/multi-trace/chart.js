import Ember from 'ember';
import color from 'pacu-v2/utils/color';
import EmberObject, { computed } from '@ember/object';

const yAxes = {
  type: 'linear',
  position: 'left',
  gridLines: {
    color: 'rgba(255, 255, 255, 0.5)',
    display: false
  },
  scaleLabel: {
    display: true,
    labelString: 'Raw Value'
  },
  ticks: { display: true, }
}

const xAxes = {
  type: 'category',
  position: 'bottom',
  scaleLabel: {
    display: false,
    // labelString: 'Orientation of Stimulus'
  },
  gridLines: {
    display: false,
    color: 'rgba(255, 255, 255, 0.5)',
    // drawOnChartArea: false,
    // drawTicks: true
  },
  ticks: {
    display: true,
    maxTicksLimit: 24
  }
}

//const type = 'lineEx';
const type = 'line';
const data = { labels:[], datasets:[] }; // dummy
const options = {
  title: {
    display: true,
    text: 'ROI Traces',
    fontStyle: 'normal'
  },
  legend: {
    display: true,
    labels: {
      fontSize: 10
    }
  },
  tooltips: {enabled: true},
  scales: {
    yAxes: [yAxes],
    xAxes: [xAxes],
  },
  //hover: {
  //  animationDuration: null
  //},
  elements: {
    // line: {
    //   borderWidth: 1,
    //   fill: false,
    //   tension: 0
    // },
    point: {
      radius: 0,
      hoverRadius: 8,
      hitRadius: 8,
    }
  },
  //animation: {
  //  duration: null
  //}
};

export default EmberObject.extend({
  traces: computed('datatags', function() {
    var dts = this.get('datatags');
    if (dts) {
      if (dts.length) {
        return dts.getEach('valueByFocalPlane');
      } else {
        return dts.get('valueByFocalPlane');
      };
    } else {
      return [];
    };
  }),
  labels: computed('traces', function() {
    var traces = this.get('traces');
    var lens = traces.getEach('length'); // will be either [], [undef,undef...] or [val,val...]
    if (Ember.isEmpty(lens)) {
      return [];
    } else if (!lens[0]) {
      return Array.from(Array(traces.length).keys());
    } else {
      return Array.from(Array(Math.max(...lens)).keys()); // range the JS way.
    };
  }),
  datasets: computed('datatags', function() {
    var dts = this.get('datatags');
    if (dts) {
      if (!dts.length) {
        dts = [dts];
      };
      return dts.map((datatag, index) => {
        return {
          borderColor: datatag.color || color.google20[index],
          borderWidth: 0.5,
          data: datatag.get('valueByFocalPlane'),
          label: `ROI #${datatag.get('roi.reprId')}`,
          lineTension: 0,
          fill: false
        };
      });
    } else {
      return [];
    };
  }),
  rois: computed('datatags', function() {
    var dts = this.get('datatags');
    if (dts) {
      if (dts.length) {
        return dts.getEach('valueByFocalPlane');
      } else {
        return dts;
      };
    } else {
      return [].getEach('valueByFocalPlane');
    };
  })
}).reopenClass({config: { type, data, options }});
