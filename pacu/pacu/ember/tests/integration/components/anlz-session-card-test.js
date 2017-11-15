import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('anlz-session-card', 'Integration | Component | anlz session card', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{anlz-session-card}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#anlz-session-card}}
      template block text
    {{/anlz-session-card}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
