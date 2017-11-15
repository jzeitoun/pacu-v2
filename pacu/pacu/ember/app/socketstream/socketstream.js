import Ember from 'ember';
import EmberObject, { computed, observer } from '@ember/object';

const Image = EmberObject.extend({
  mpi: false,
  buffer: null,
  curIndex: 0,
  cmap: 'Jet', // added attribute (JZ)
  max: 255, // added to control colormap contrast (JZ)
  min: 0, // added to control colormap contrast (JZ)
  maxIndex: computed('depth', function() {
    return this.get('depth') - 1;
  }),
});

export default Ember.Object.extend({
  img: computed('ch0Dimension', function() {
    var ch = this.get('ch0Dimension');
    return Image.create(ch);
  }),
  print(...fields) { return this.get('wsx').print(...fields); },
  access(...fields) { return this.get('wsx').access(...fields); },
  mirror(...fields) { return this.get('wsx').mirrorTo(this, ...fields); },
  invoke(func, ...args) { return this.get('wsx').invoke(func, ...args); },
  invokeAsBinary(func, ...args) { return this.get('wsx').invokeAsBinary(func, ...args); },
  init() {
    this._super(...arguments);
    this.mirror('ch0.dimension', 'ch0.has_maxp');
  },
  // this requests frame from backend (JZ)
  // colormap is determined in backend
  // added cmap argument to select colormap
  requestFrame(index) {
    return this.get('wsx').invokeAsBinary(
        'ch0.request_frame', parseInt(index)).then(buffer => {
      this.set('img.buffer', buffer);
      this.set('img.mpi', false);
    });
  },
  set_cmap(cmap) {
    this.get('wsx').invokeAsBinary(
      'ch0.set_cmap', this.get('img.cmap'))
  },
  set_contrast(min, max) {
    this.get('wsx').invokeAsBinary(
      'ch0.set_contrast', min, max)
  },
  indexChanged: observer('img.curIndex', function() {
    this.requestFrame(this.get('img.curIndex'));
  }),
  cmapChanged: observer('img.cmap', function() {
    this.set_cmap(this.get('img.cmap')); // added cmap argument JZ
    this.requestFrame(this.get('img.curIndex'));
  }),
  contrastChanged: observer('img.{min,max}', function() {
    this.set_contrast(this.get('img.min'), this.get('img.max'));
    Ember.run.debounce(this, () => this.requestFrame(this.get('img.curIndex')), 150);
  }),
  mainCanvasDimension: computed(function() {
    return { height: 0 };
  }),

  overlayMPI() {
    swal({
      title: 'Please specify colormap variables',
      html: `
        <div id="cmap-params" class="ui form">
          <h4 class="ui dividing header">Value range is between 0 and 1</h4>
          <div class="four fields">
            <div class="field">
              <label>X Mid1</label>
              <input type="number" name="xmid1" placeholder="X Mid1" value="0.25">
            </div>
            <div class="field">
              <label>Y Mid1</label>
              <input type="number" name="ymid1" placeholder="Y Mid2" value="0.25">
            </div>
            <div class="field">
              <label>X Mid2</label>
              <input type="number" name="xmid2" placeholder="X Mid2" value="0.75">
            </div>
            <div class="field">
              <label>Y Mid2</label>
              <input type="number" name="ymid2" placeholder="Y Mid2" value="0.75">
            </div>
          </div>
        </div>
      `,
      onOpen: function () {
        $('input[name="xmid1"]').focus();
      }
    }).then(result => {
      const xmid1 = parseFloat($('input[name="xmid1"]').val());
      const ymid1 = parseFloat($('input[name="ymid1"]').val());
      const xmid2 = parseFloat($('input[name="xmid2"]').val());
      const ymid2 = parseFloat($('input[name="ymid2"]').val());
      const cmap = { xmid1, ymid1, xmid2, ymid2 };
      this.get('wsx').invokeAsBinary('ch0.request_maxp', cmap).then(buffer => {
        this.set('img.buffer', buffer);
        this.set('img.mpi', true);
      });
    }).catch(swal.noop)
  },

  requestMPITiff() {
    return this.get('wsx').invokeAsBinary('ch0.request_maxp_tiff');
  }
});
