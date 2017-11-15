import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('x-layer/canvas-2d', 'Integration | Component | x layer/canvas 2d', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{x-layer/canvas-2d}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#x-layer/canvas-2d}}
      template block text
    {{/x-layer/canvas-2d}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
