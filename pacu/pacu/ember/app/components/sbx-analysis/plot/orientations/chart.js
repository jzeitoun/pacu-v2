import Ember from 'ember';
// import computed from 'ember-computed-decorators';

// const yAxes = {
//   type: 'linear',
//   position: 'left',
//   gridLines: {
//     color: 'rgba(255, 255, 255, 0.5)',
//     display: false
//   },
//   scaleLabel: {
//     display: false,
//   },
//   ticks: { display: true, }
// }
// 
// const xAxes = {
//   type: 'category',
//   position: 'bottom',
//   scaleLabel: {
//     display: false,
//     // labelString: 'Orientation of Stimulus'
//   },
//   gridLines: {
//     display: false,
//     color: 'rgba(255, 255, 255, 0.5)',
//     // drawOnChartArea: false,
//     // drawTicks: true
//   },
//   ticks: {
//     maxTicksLimit: 24
//   }
// }
// 
// const type = 'lineEx';
// const data = { labels:[], datasets:[] }; // dummy
// const options = {
//   title: {
//     display: true,
//     text: 'Orientation of Stimulus',
//     fontStyle: 'normal'
//   },
//   legend: {
//     display: false,
//     labels: {
//       fontSize: 10
//     }
//   },
//   tooltips: {enabled: true},
//   scales: {
//     yAxes: [yAxes],
//     xAxes: [xAxes],
//   },
//   hover: {
//     animationDuration: null
//   },
//   elements: {
//     // line: {
//     //   borderWidth: 1,
//     //   fill: false,
//     //   tension: 0
//     // },
//     point: {
//       radius: 0,
//       hoverRadius: 0,
//       hitRadius: 0,
//     }
//   },
//   animation: {
//     duration: null
//   }
// };

export default Ember.Object.extend({});
//   @computed('datatags') labels(datatags=[]) {
//     debugger
//     return trace.map((e, i) => i);
//   },
//   @computed('datatags') datasets(datatags=[]) {
//     debugger
//     return [{
//       //borderColor: trace.color || color.google20[index],
//       borderColor: 'red',
//       borderWidth: 0.5,
//       data: trace,
//       label: 'ephys',
//       // label: `ROI #${trace.roi}`,
//     }];
//   }
// }).reopenClass({config: { type, data, options }});
