import Ember from 'ember';
import Component from '@ember/component';
import EmberObject, { observer, computed } from '@ember/object';

/* global Chart */

const yAxes = {
  type: 'linear',
  position: 'left',
  gridLines: {
    color: 'rgba(255, 255, 255, 0.1)',
    zeroLineColor: 'rgba(255, 255, 255, 0.5)',
    display: true,
    drawTicks: false
  },
  scaleLabel: {
    display: true,
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
    display: true,
    color: 'rgba(255, 255, 255, 0.1)',
    zeroLineColor: 'rgba(255, 255, 255, 0.5)',
    drawTicks: false
  },
  ticks: {
    autoSkip: false,
    display: true,
  },
}

const type = 'line';
const data = { labels:[], datasets:[] }; // dummy as an initial data
const options =  {
  title: {
    display: true,
    text: 'Sum of Gaussians',
    fontStyle: 'normal'
  },
  legend: {display: false},
  tooltips: {enabled: false},
  scales: {
    yAxes: [yAxes],
    xAxes: [xAxes],
  },
  elements: {
    line: {
      borderWidth: 1,
      fill: false,
      tension: 0
    },
    point: {
      backgroundColor: 'rgba(0,0,0,0)',
      radius: 0,
      hoverRadius: 0,
      hitRadius: 0
    }
  },
  //animation: { // important
  //  duration: null,
  //}
};
const config = { type, data, options }

const DataFetcher = EmberObject.extend({
  orientations: computed('datatag', function() {
    var datatag = this.get('datatag');
    return datatag.get('value.orientations') || [];
  }),
  datasets: computed('datatag', function() {
    var datatag = this.get('datatag');
    // if (Ember.isNone(datatag)) { return []; }
    const y_meas = datatag.get('value.y_meas') || [];
    const y_fit = datatag.get('value.y_fit') || [];
    const measureData = {
      borderColor: 'rgba(255, 255, 255, 1)',
      borderWidth: 0.5,
      data: y_meas,
    };
    const fitData = {
      borderColor: 'rgba(255, 0, 0, 1)',
      borderWidth: 1,
      data: y_fit,
    };
    return [measureData, fitData];
  }),
  labels: computed('datatag', function() {
    var datatag = this.get('datatag');
    return datatag.get('value.x') || [];
  }),
});

export default Component.extend({
  tagName: 'canvas',
  classNames: ['noselect'],
  //width: 500,
  height: 52,
  attributeBindings: ['width', 'height'],
  ctx: computed(function() { return this.element.getContext('2d') }),
  chart: computed('ctx', function() {
    var ctx = this.get('ctx');
    return new Chart(ctx, config);
  }),
  // @observes('datapromise') promiseIncoming() {
  //   const prom = this.get('datapromise');
  //   if (Ember.isNone(prom)) {
  //     this.set('datatag', {});
  //   } else {
  //     prom.then(data => {
  //       this.set('datatag', data.get('firstObject.value'));
  //     });
  //   }
  // },
  datatag: EmberObject.create({ value: {} }),
  fetcher: computed('datatag', function() {
    var datatag = this.get('datatag');
    return DataFetcher.create({ datatag });
  }),
  // @observes('dimension.width') dimensionChanged() {
  //   this.get('chart').update();
  // },
  draw: observer('datatag', function() {
    const {chart, fetcher} = this.getProperties('chart', 'fetcher');
    // if (Ember.$.isEmptyObject(this.get('datatag'))) {
    //   chart.data.datasets = datasets;
    //   chart.update();
    //   return;
    // }
    const labels = fetcher.get('labels');
    const datasets = fetcher.get('datasets');
    const orientations = fetcher.get('orientations');
    const ticks = chart.config.options.scales.xAxes[0].ticks;
    ticks.callback = (value /*, index, values */) => {
      if (orientations.includes(value)) {
        return value;
      }
    };
    chart.data.labels = labels;
    chart.data.datasets = datasets;
    chart.update();
  }),

  didInsertElement() {
    Ember.run.next(this, 'draw');
  },
  willDestroyElement() {
    this.get('chart').destroy();
  }
});
