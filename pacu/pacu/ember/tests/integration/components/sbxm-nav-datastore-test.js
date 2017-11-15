import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('sbxm-nav-datastore', 'Integration | Component | sbxm nav datastore', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{sbxm-nav-datastore}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#sbxm-nav-datastore}}
      template block text
    {{/sbxm-nav-datastore}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
