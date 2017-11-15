import Ember from 'ember';
import Component from '@ember/component';
import EmberObject, { observer, computed } from '@ember/object';
import Chart from 'npm:chart.js';

/* global Chart */

const yAxes = {
  type: 'linear',
  position: 'left',
  gridLines: {
    color: 'rgba(255, 255, 255, 0.5)',
    display: false
  },
  scaleLabel: {
    display: true,
    labelString: 'dF/F0',
  },
  ticks: { display: true, }
};
const xAxes = {
  type: 'category',
  position: 'bottom',
  scaleLabel: {
    display: false,
    labelString: 'Orientation of Stimulus'
  },
  gridLines: {
    display: false,
    color: 'rgba(255, 255, 255, 0.5)',
    // drawOnChartArea: false,
    // drawTicks: true
  },
  ticks: {
    autoSkip: false,
    display: true,
    // userCallback: function(value, index, values) {
    //   return asd.repetition.indices[index];
    // }
  },
};
const type = 'line';
const data = { labels:[], datasets:[] }; // dummy as an initial data
const options =  {
  // pan: {
  //   enabled: true,
  //   mode: 'xy'
  // },
  // zoom: {
  //   enabled: true,
  //   mode: 'xy',
  // },
  title: {
    display: true,
    text: 'Orientation of Stimulus',
    fontStyle: 'normal'
  },
  legend: {display: false},
  tooltips: {
    enabled: true,
    mode: 'nearest',
    intersect: true,
    // custom: (tooltip) => {
    //   debugger
    // },
    // callbacks: {
    //   beforeTitle(items, data) {
    //     return 'bf title';
    //   },
    //   title(items, data) {
    //     return 'title';
    //   },
    //   afterTitle(items, data) {
    //     return 'af title';
    //   },
    //   beforeBody(items, data) {
    //     return 'bf body';
    //   },
    //   beforeLabel(item, data) {
    //     return 'bf label';
    //   },
    //   label(item, data) {
    //     return 'label';
    //   },
    //   // labelColor(item, chart) { debugger },
    //   afterLabel(item, data) {
    //     return 'af label';
    //   },
    //   afterBody(items, data) {
    //     return 'af body';
    //   },
    //   beforeFooter(items, data) {
    //     return 'bf footer';
    //   },
    //   footer(items, data) {
    //     return 'fter';
    //   },
    //   afterFooter(items, data) {
    //     return 'aftfoot';
    //   },
    //   dataPoints(items, data) {
    //     return 'data points';
    //   },
    // }
  },
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
      radius: 0.1,
      hoverRadius: 8,
      hitRadius: 8
    }
  },
  //animation: { // important
  //  duration: null,
  //},
};
const config = { type, data, options }

const DataFetcher = Ember.Object.extend({
  // @computed('datatags.@each.value') unavailable(datatags=[[]]) {
  //   return datatags.getEach('value').any(Ember.isNone);
  // },
  // @computed('datatags.@each.value') byTrials(datatags=[[]]) {
  //   const byTrials = [];
  //   const dts = datatags.copy();
  //   // making 2d array
  //   const nReps = this.get('condition.repetition');
  //   while (dts.length) { byTrials.push(dts.splice(0, nReps)); }
  //   return byTrials;
  // },
  // @computed('byTrials') meantrace(byTrials) {
  //   const mt = byTrials.map(t => {
  //     var ons = t.map(r=>r.get('value.on'));
  //     var onsT = ons[0].map((_, i) => ons.map(row => row[i]));
  //     var onmean = onsT.map( dp => dp.reduce((a, b) => a + b) / dp.length);
  //     var bss = t.map(r=>r.get('value.baseline'));
  //     var bssT = bss[0].map((_, i) => bss.map(row => row[i]));
  //     var bsmean = bssT.map( dp => dp.reduce((a, b) => a + b) / dp.length);
  //     return { on: onmean, baseline: bsmean }
  //   })
  //   return mt;
  // },
  // @computed('byTrials') byReps(byTrials) {
  //   // transpose it
  //   return byTrials[0].map((_, i) => byTrials.map(row => row[i]));
  // },
  // @computed('meantrace', 'byReps') datasets(meantrace, byReps) {
  //   const borderColor = 'rgba(255, 255, 255, 0.5)';
  //   const borderWidth = 0.5;
  //   const datasets = byReps.map(rep => {
  //     let data = [].concat(...rep.map(trial => {
  //       if (Ember.isEmpty(trial)) { return []; }
  //       let {baseline, on} = trial.get('value');
  //       return [].concat(baseline, on);
  //     }));
  //     return { data, borderColor, borderWidth };
  //   });
  //   datasets.push({
  //     data: [].concat(...meantrace.map(mt => [].concat(mt.baseline, mt.on))),
  //     borderColor: "rgba(255, 0, 0, 1)", borderWidth: 1.5
  //   });
  //   return datasets;
  // },
  datasets: computed('datatag', function() {
    var datatag = this.get('datatag');
    const borderColor = 'rgba(255, 255, 255, 0.5)';
    const borderWidth = 0.5;
    const datasets = datatag.get('matrix').map(data => {
      return { data, borderColor, borderWidth };
    });
    datasets.push({
      data: datatag.get('meantrace'),
      borderColor: "rgba(255, 0, 0, 1)", borderWidth: 1.5
    });
    return datasets;
  }),
  labels: computed('datatag', function() {
    var datatag = this.get('datatag');
    return datatag.get('meantrace').map((e, i) => i);
  }),
  indices: computed('datatag', function() {
    var datatag = this.get('datatag');
    return datatag.get('indices');
  }),
  onFrames: computed('datatag', function() {
    var datatag = this.get('datatag');
    return datatag.get('on_frames');
  }),
  bsFrames: computed('datatag', function() {
    var datatag = this.get('datatag');
    return datatag.get('off_frames');
  }),
});

export default Component.extend({
  tagName: 'canvas',
  classNames: ['noselect'],
  // width: 500,
  height: 52,
  attributeBindings: ['width', 'height'],
  ctx: computed(function() { return this.element.getContext('2d'); }),
  chart: computed('ctx', function() {
    var ctx = this.get('ctx');
    const self = this;
    const chart = new Chart(ctx, config);
    const draw = chart.draw;
    chart.draw = function() {
      draw.apply(this, arguments);
      self.chartDidDraw(this, ...arguments);
    };
    return chart;
  }),
  datatag: EmberObject.create({ meantrace: [], matrix: [], indices: {}, on_frames: null, bs_frames: null }),
  fetcher: computed('datatag', function() {
    var datatag = this.get('datatag');
    return DataFetcher.create({ datatag });
  }),
  draw: observer('datatag', function() {
    const {chart, fetcher} = this.getProperties('chart', 'fetcher');
    const indices = fetcher.get('indices');
    //   chart.boxes[2].options.text = 'Orientation of Stimulus - No selection'
    const ticks = chart.config.options.scales.xAxes[0].ticks;
    ticks.userCallback = (value, index /*, values*/) => indices[index];
    chart.data.labels = fetcher.get('labels');
    chart.data.datasets = fetcher.get('datasets');
    chart.update();
    // try {
    // } catch (err) {
    //   console.log('ERROR on Orientations plot', err);
    // }
  }),

  chartDidDraw(chart) {
    //console.log('chart did draw');
    const fetcher = this.get('fetcher');
    const indices = fetcher.get('indices');
    if (Ember.$.isEmptyObject(indices)) { return }
    const onFrames = fetcher.get('onFrames');
    let { top, height } = chart.scales['y-axis-0'];
    let width = chart.scales['x-axis-0'].getPixelForTick(onFrames) - chart.scales['x-axis-0'].getPixelForTick(0);
    chart.chart.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    for (let x in indices) {
      let x0 = chart.scales['x-axis-0'].getPixelForTick(parseInt(x));
      chart.chart.ctx.fillRect(x0, top, width, height);
    }
  },
  didUpdate() {
    //debugger;
  },
  didInsertElement() {
    Ember.run.next(this, 'draw');
  },
  willDestroyElement() {
    this.get('chart').destroy();
  }
});
