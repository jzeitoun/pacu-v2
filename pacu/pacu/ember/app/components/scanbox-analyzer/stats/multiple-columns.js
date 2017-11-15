import EmberObject from '@ember/object';

export default [
  {
    name: 'OSI',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.osi',
  },
  {
    name: 'CV',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.cv',
  },
  {
    name: 'DCV',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.dcv',
  },
  {
    name: 'DSI',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.dsi',
  },
  {
    name: 'Sigma',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.sigma',
  },
  {
    name: 'OPref',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.o_pref',
  },
//   {
//     name: 'Tau',
//     relPath: 'dtorientationsfitsByCT',
//     valuePath: 'value.tau',
//   },
  {
    name: 'RMax',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.r_max',
  },
  {
    name: 'Residual',
    relPath: 'dtorientationsfitsByCT',
    valuePath: 'value.residual',
  },
  {
    name: 'Anova F',
    relPath: 'dtanovaeachsByCT',
    valuePath: 'f',
  },
  {
    name: 'Anova P',
    relPath: 'dtanovaeachsByCT',
    valuePath: 'p',
  }
].map(e => EmberObject.create(e));
