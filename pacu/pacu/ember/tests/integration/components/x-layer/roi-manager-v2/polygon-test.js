import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('x-layer/roi-manager-v2/polygon', 'Integration | Component | x layer/roi manager v2/polygon', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{x-layer/roi-manager-v2/polygon}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#x-layer/roi-manager-v2/polygon}}
      template block text
    {{/x-layer/roi-manager-v2/polygon}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
