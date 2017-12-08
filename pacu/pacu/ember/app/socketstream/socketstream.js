import Ember from 'ember';
import EmberObject, { computed, observer } from '@ember/object';

const Image = EmberObject.extend({
  //mpi: false,
  projection: Ember.computed('maxp', 'meanp', 'sump', function() {
    if (this.get('maxp')) { return 'max'; }
    else if (this.get('meanp')) { return 'mean'; }
    else if (this.get('sump')) { return 'sum'; }
    else { return false; };
  }),
  maxp: false,
  meanp: false,
  sump: false,
  buffer: null,
  curIndex: 0,
  cmap: 'Gray', // added attribute (JZ)
  channelDisplay: 'Green', // default to green channel
  showGreen: Ember.computed('channelDisplay', function() {
    if (this.get('channelDisplay') == 'Both' || this.get('channelDisplay') == 'Green') {
      return true;
    } else {
      return false;
    };
  }),
  showRed: Ember.computed('channelDisplay', function() {
    if (this.get('channelDisplay') == 'Both' || this.get('channelDisplay') == 'Red') {
      return true;
    } else {
      return false;
    };
  }),
  max: 255, // added to control colormap contrast (JZ)
  min: 0, // added to control colormap contrast (JZ)
  red_max: 255,
  red_min: 0,
  maxp_max: 255, // added to control colormap contrast (JZ)
  maxp_min: 0, // added to control colormap contrast (JZ)
  meanp_max: 255, // added to control colormap contrast (JZ)
  meanp_min: 0, // added to control colormap contrast (JZ)
  sump_max: 255, // added to control colormap contrast (JZ)
  sump_min: 0, // added to control colormap contrast (JZ)
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
    this.mirror('ch0.dimension', 'ch0.has_meanp', 'ch0.has_maxp', 'ch0.has_sump');
  },
  // this requests frame from backend (JZ)
  // colormap is determined in backend
  // added cmap argument to select colormap
  requestFrame(index) {
    this.set('img.maxp', false);
    this.set('img.meanp', false);
    this.set('img.sump', false);
    this.setRGBContrast();
    console.log('frame requested');
    var ch = this.get('img.channel');
    return this.get('wsx').invokeAsBinary(
        'ch0.request_frame', parseInt(index)).then(buffer => { console.log('frame received');
      this.set('img.buffer', buffer);
    }).catch(reason => { console.log(reason); });
  },

  requestProjection(image_type) {
    console.log('requested projection');
    return this.get('wsx').invokeAsBinary(
        'ch0.request_projection', image_type).then(buffer => { console.log('projection received');
      this.set('img.buffer', buffer);
    });
  },

  setCmap() {
    this.get('wsx').invokeAsBinary(
      'ch0.set_cmap', this.get('img.cmap'));
  },

  setRGBContrast() {
    var {'img.min':min, 'img.max':max, 'img.red_min':red_min, 'img.red_max':red_max} = this.getProperties('img.min', 'img.max', 'img.red_min', 'img.red_max');
    this.get('wsx').invokeAsBinary(
      'ch0.set_rgb_contrast', min, max, red_min, red_max
    );
  },

  setContrast() {
    var image_type = String(this.get('img.projection'));
    switch (image_type) {
      case 'max':
        var min = this.get('img.maxp_min');
        var max = this.get('img.maxp_max');
        break;
      case 'mean':
        var min = this.get('img.meanp_min');
        var max = this.get('img.meanp_max');
        break;
      case 'sum':
        var min = this.get('img.sump_min');
        var max = this.get('img.sump_max');
        break;
      default:
        var min = this.get('img.min');
        var max = this.get('img.max');
    };
    this.get('wsx').invokeAsBinary(
      'ch0.set_contrast', min, max)
  },

  indexChanged: observer('img.curIndex', function() {
    this.setRGBContrast();
    this.requestFrame(this.get('img.curIndex'));
  }),
  channelChanged: observer('img.channelDisplay', function() {
    this.setRGBContrast();
    this.get('wsx').invokeAsBinary(
      'ch0.set_channel', this.get('img.channelDisplay')
    );
    this.requestFrame(this.get('img.curIndex'));
  }),
  cmapChanged: observer('img.cmap', function() {
    this.setCmap(this.get('img.cmap')); // added cmap argument JZ
    if (this.get('img.maxp') || this.get('img.meanp') || this.get('img.sump')) {
      this.requestProjection(this.get('img.projection'));
    } else {
      this.requestFrame(this.get('img.curIndex'));
    };
  }),
  contrastChanged: observer('img.{min,max,red_min,red_max,maxp_min,maxp_max,meanp_min,meanp_max,sump_min,sump_max}', function() {
    this.setRGBContrast();
    if (this.get('img.maxp') || this.get('img.meanp') || this.get('img.sump')) {
      Ember.run.debounce(this, () => this.requestProjection(this.get('img.projection')), 150);
    } else {
      Ember.run.debounce(this, () => this.requestFrame(this.get('img.curIndex')), 150);
    };
  }),
  mainCanvasDimension: computed(function() {
    return { height: 0 };
  }),

  overlayProjection(image_type) {
    //this.set('img.meanp', false);
    //this.set('img.maxp', false);
    //this.set('img.sump', false);
    //switch (image_type) ({
    //  case 'max':
    //    this.set('img.maxp', true);
    //    this.setRGBContrast();
    //    break;
    //  case 'mean':
    //    this.set('img.meanp', true);
    //    this.setRGBContrast();
    //    break;
    //  case 'sum':
    //    this.set('img.sump', true);
    //    this.setRGBContrast();
    //    break;
    //  default:
    //    return;
    //};
    this.set('img.channelDisplay', 'Green');
    this.get('wsx').invokeAsBinary('ch0.request_projection', image_type).then(buffer => {
      this.set('img.buffer', buffer);
    });
  },

  requestMaxPITiff() {
    return this.get('wsx').invokeAsBinary('ch0.request_maxp_tiff');
  },
  requestMeanPITiff() {
    return this.get('wsx').invokeAsBinary('ch0.request_meanp_tiff');
  },
  requestSumPITiff() {
    return this.get('wsx').invokeAsBinary('ch0.request_sump_tiff');
  }
});
