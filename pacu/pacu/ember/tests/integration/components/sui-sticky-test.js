import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('sui-sticky', 'Integration | Component | sui sticky', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{sui-sticky}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#sui-sticky}}
      template block text
    {{/sui-sticky}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
