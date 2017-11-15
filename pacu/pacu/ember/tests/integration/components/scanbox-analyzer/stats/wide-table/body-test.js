import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('scanbox-analyzer/stats/wide-table/body', 'Integration | Component | scanbox analyzer/stats/wide table/body', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{scanbox-analyzer/stats/wide-table/body}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#scanbox-analyzer/stats/wide-table/body}}
      template block text
    {{/scanbox-analyzer/stats/wide-table/body}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
