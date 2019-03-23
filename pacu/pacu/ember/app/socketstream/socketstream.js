import Ember from 'ember';
import EmberObject, { computed, observer } from '@ember/object';

import { debounce } from '@ember/runloop';

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
  channelDisplay: null,
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
  max: 65535, // added to control colormap contrast (JZ)
  min: 0, // added to control colormap contrast (JZ)
  red_max: 65535,
  red_min: 0,
  maxp_max: 65535, // added to control colormap contrast (JZ)
  maxp_min: 0, // added to control colormap contrast (JZ)
  meanp_max: 65535, // added to control colormap contrast (JZ)
  meanp_min: 0, // added to control colormap contrast (JZ)
  sump_max: 65535, // added to control colormap contrast (JZ)
  sump_min: 0, // added to control colormap contrast (JZ)
  maxIndex: computed('depth', function() {
    return this.get('depth') - 1;
  }),
});

export default EmberObject.extend({
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
    this.mirror('ch0.dimension', 'ch0.has_meanp', 'ch0.has_maxp', 'ch0.has_sump', 'mat.channels', 'mat.chan.sample');
    Ember.run.later(this, 'setChannelOptions', 100);
    const keysToObserve = ['min','max','red_min','red_max'];
    keysToObserve.forEach(key => {
      Ember.run.later(this, () => this.addObserver(`img.${key}`, this, 'contrastChanged'), 100);
    });
    Ember.run.later(this, () => this.addObserver('img.cmap', this, 'cmapChanged'), 100);
    Ember.run.later(this, () => this.addObserver('img.channelDisplay', this, 'channelChanged'), 100);
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

  setChannelOptions() {
    /* Ugly Workaround */
    const channels = this.get('matChannels');
    var channelSet = this.get('channelSet');
    if ( (channels && !this.get('channelSet')) || (!channels && this.get('channelSet')) ) {
      switch (channels) {
        case -1 :
          let activeChannels = this.get('matChanSample');
          if (activeChannels[0] && activeChannels[1]) {
            this.set('img.channelOptions', ['Green', 'Red', 'Both']);
            this.set('img.channelDisplay', 'Green');
            this.set('channelSet', true);
          } else if (activeChannels[0] &! activeChannels[1]){
            this.set('img.channelOptions', ['Green']);
            this.set('img.channelDisplay', 'Green');
            this.set('channelSet', true);
          } else if (activeChannels[1] &! activeChannels[0]) {
            this.set('img.channelOptions', ['Red']);
            this.set('img.channelDisplay', 'Red');
            this.set('channelSet', true);
          }
          break;
        case 1 :
          this.set('img.channelOptions', ['Green', 'Red', 'Both']);
          this.set('img.channelDisplay', 'Green');
          this.set('channelSet', true);
          break;
        case 2 :
          this.set('img.channelOptions', ['Green']);
          this.set('img.channelDisplay', 'Green');
          this.set('channelSet', true);
          break;
        case 3 :
          this.set('img.channelOptions', ['Red']);
          this.set('img.channelDisplay', 'Red');
          this.set('channelSet', true);
          break;
        default :
          return;
      };
    };
      /* End Ugly Workaround */
  },

  requestProjection(image_type) {
    console.log('requested projection');
    this.setRGBContrast();
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
    //debounce(this.get('wsx'), 'invokeAsBinary', ('ch0.set_rgb_contrast', min, max, red_min, red_max), 250, true);
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
    console.log('index changed');
    //this.setRGBContrast();
    this.requestFrame(this.get('img.curIndex'));
  }),
  //channelChanged: observer('img.channelDisplay', function() {
  //  console.log('channel changed');
  //  //this.setRGBContrast();
  //  this.get('wsx').invokeAsBinary(
  //    'ch0.set_channel', this.get('img.channelDisplay')
  //  );
  //  this.requestFrame(this.get('img.curIndex'));
  //}),
  //cmapChanged: observer('img.cmap', function() {
  //  console.log('cmap changed');
  //  this.setCmap(this.get('img.cmap')); // added cmap argument JZ
  //  if (this.get('img.maxp') || this.get('img.meanp') || this.get('img.sump')) {
  //    this.requestProjection(this.get('img.projection'));
  //  } else {
  //    this.requestFrame(this.get('img.curIndex'));
  //  };
  //}),
  //contrastChanged: observer('img.{min,max,red_min,red_max}', function() {
  //  console.log('contrast changed');
  //  //this.setRGBContrast();
  //  if (this.get('img.maxp') || this.get('img.meanp') || this.get('img.sump')) {
  //    Ember.run.debounce(this, () => this.requestProjection(this.get('img.projection')), 150);
  //  } else {
  //    Ember.run.debounce(this, () => this.requestFrame(this.get('img.curIndex')), 150);
  //  };
  //}),
  channelChanged: function() {
    console.log('channel changed');
    //this.setRGBContrast();
    this.get('wsx').invokeAsBinary(
      'ch0.set_channel', this.get('img.channelDisplay')
    );
    this.requestFrame(this.get('img.curIndex'));
  },
  cmapChanged: function() {
    console.log('cmap changed');
    this.setCmap(this.get('img.cmap')); // added cmap argument JZ
    if (this.get('img.maxp') || this.get('img.meanp') || this.get('img.sump')) {
      this.requestProjection(this.get('img.projection'));
    } else {
      this.requestFrame(this.get('img.curIndex'));
    };
  },
  contrastChanged: function() {
    console.log('contrast changed');
    //this.setRGBContrast();
    if (this.get('img.maxp') || this.get('img.meanp') || this.get('img.sump')) {
      Ember.run.debounce(this, () => this.requestProjection(this.get('img.projection')), 150);
    } else {
      Ember.run.debounce(this, () => this.requestFrame(this.get('img.curIndex')), 250);
    };
  },

  mainCanvasDimension: computed(function() {
    return { height: 0 };
  }),

  overlayProjection(image_type) {
    this.set('img.meanp', false);
    this.set('img.maxp', false);
    this.set('img.sump', false);
    switch (image_type) {
      case 'max':
        this.set('img.maxp', true);
        //this.setRGBContrast();
        break;
      case 'mean':
        this.set('img.meanp', true);
        //this.setRGBContrast();
        break;
      case 'sum':
        this.set('img.sump', true);
        //this.setRGBContrast();
        break;
      default:
        return;
    };
    this.set('projection', true);
    let curChannel = this.get('img.channelDisplay');
    if (curChannel == 'Green' || curChannel == 'Both') {
      this.get('wsx').invokeAsBinary('ch0.request_projection', image_type).then(buffer => {
        this.set('img.buffer', buffer);
      });
    } else {
      this.get('wsx').invokeAsBinary('ch1.request_projection', image_type).then(buffer => {
        this.set('img.buffer', buffer);
      });
    };
  },

  requestMaxPITiff(channel) {
    return this.get('wsx').invokeAsBinary(`${channel}.request_maxp_tiff`);
  },
  requestMeanPITiff(channel) {
    return this.get('wsx').invokeAsBinary(`${channel}.request_meanp_tiff`);
  },
  requestSumPITiff(channel) {
    return this.get('wsx').invokeAsBinary(`${channel}.request_sump_tiff`);
  }
});
