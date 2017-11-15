import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('sbx-analysis/plot/multi-trace', 'Integration | Component | sbx analysis/plot/multi trace', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{sbx-analysis/plot/multi-trace}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#sbx-analysis/plot/multi-trace}}
      template block text
    {{/sbx-analysis/plot/multi-trace}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
