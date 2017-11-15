import EmberObject from '@ember/object';

export default [
  {
    name: 'Cell ID',
    valuePath: 'reprId',
  },
  {
    name: 'Anova All F',
    valuePath: 'dtanovaallByCT.value.f',
  },
  {
    name: 'Anova All P',
    valuePath: 'dtanovaallByCT.value.p',
  },
  {
    name: 'SF Cutoff Rel33',
    valuePath: 'dtsfreqfitByCT.value.rc33.0',
  },
  {
    name: 'SF Cutoff Rel33',
    valuePath: 'dtsfreqfitByCT.value.rc33.1',
  },
  {
    name: 'SF Peak',
    valuePath: 'dtsfreqfitByCT.value.peak',
  },
  {
    name: 'SF Pref',
    valuePath: 'dtsfreqfitByCT.value.pref',
  },
  {
    name: 'SF Bandwidth',
    valuePath: 'dtsfreqfitByCT.value.ratio',
  },
  {
    name: 'SF Global OPref',
    valuePath: 'dtorientationbestprefByCT.value',
  }
].map(e => EmberObject.create(e));
