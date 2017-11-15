import Component from '@ember/component';

export default Component.extend({
  classNames: 'ui compact dropdown',
  didInsertElement() {
    const self = this;
    this.$().dropdown({
      onChange(value /*, text, $choice*/) {
        self.attrs.value.update(parseFloat(value));
      }
    });
  },
  willDestroyElement() {
    this.$().dropdown('destroy');
  }
});
