import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('sbx-analysis/plot/orientations', 'Integration | Component | sbx analysis/plot/orientations', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{sbx-analysis/plot/orientations}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#sbx-analysis/plot/orientations}}
      template block text
    {{/sbx-analysis/plot/orientations}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
