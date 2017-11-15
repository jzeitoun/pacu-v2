import Ember from 'ember';
import Component from '@ember/component';
import Manager from 'pacu-v2/components/sbx-analysis/plot/multi-trace/chart';
import { computed, observer } from '@ember/object';

/* global Chart */

export default Component.extend({
  tagName: 'canvas',
  classNames: ['noselect'],
  classNameBindings: ['augKeyOn'],
  attributeBindings: ['width', 'height'],
  width: 500,
  height: 128,
  ctx: computed(function() { return this.element.getContext('2d'); }),
  chart: computed('ctx', function() {
    var ctx = this.get('ctx');
    return new Chart(ctx, Manager.config);
  }),
  draw: observer('datatags', function() {
    const datatags = this.get('datatags');
    const chart = this.get('chart');
    const manager = Manager.create({ datatags });
    chart.data.labels = manager.get('labels');
    chart.data.datasets = manager.get('datasets');
    chart.update();
    this.set('dimension.width', chart.scales['y-axis-0'].width);
  }),
  drawIndex: observer('index', function() {
    const index = parseInt(this.get('index'));
    const chart = this.get('chart');
    if (chart.anon) {
      chart.anon.controller.setIndex(index);
    }
  }),

  didInsertElement() {
    Ember.run.next(this, 'draw');
  },

  willDestroyElement() {
    this.get('chart').destroy();
  }
});
