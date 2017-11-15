import Ember from 'ember';

/*

import interaction from 'pacu/utils/interaction';

{
  mouseDown(e) {
    const $target = this.parentView.$();
    return interaction.bindOnce.call(this, $target, e, ...);
  },
  leaving() { console.log('leaving'); },
  moving() { console.log('moving'); },
  movingWith
  movingWithout
  left() { console.log('left'); },
  moved() { console.log('moved'); },
  shot() { console.log('shot'); },
  poked() { console.log('poked'); },
}

 */
export function bindOnce($target,
  {offsetX, offsetY, altKey, metaKey}, ...currier) {
  const [originX, originY] = [offsetX, offsetY];
  const augKey = altKey || metaKey;
  let theleft;
  $target.one('mousemove', ({offsetX, offsetY}) => {
    if (augKey && this.leaving) {
      theleft = this.leaving({x: originX, y: originY}, {x: offsetX, y: offsetY}, ...currier);
    }
    $target.on('mousemove', ({offsetX, offsetY}) => {
      if (this.moving) {
        this.moving({x: originX, y: originY}, {x: offsetX, y: offsetY}, ...currier);
      }
      if (this.movingWith && theleft !== undefined) {
        this.movingWith({x: originX, y: originY}, {x: offsetX, y: offsetY}, ...currier, theleft);
      }
      return false;
    });
    return false;
  });
  Ember.$(document).one('mouseup', ({offsetX, offsetY}) => {
    $target.off('mousemove');
    if (originX === offsetX && originY === offsetY) {
      const f = this[augKey ? 'shot' : 'poked'];
      if (f) { f.call(this, {x: originX, y: originY}, {x: offsetX, y: offsetY}, ...currier); }
    } else {
      if (augKey && this.left) { this.left({x: originX, y: originY}, {x: offsetX, y: offsetY}, ...currier, theleft); }
      if (this.moved) { this.moved({x: originX, y: originY}, {x: offsetX, y: offsetY}, ...currier, theleft); }
    }
    return false;
  });
  return false;
}
