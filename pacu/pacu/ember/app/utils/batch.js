import Ember from 'ember';

export function promiseSequence(targets, task, done, index=1) {
  const entry = targets.copy();
  const len = entry.get('length');
  const promise = new Ember.RSVP.Promise((resolve, reject) => {
    (function next(index) {
      const target = entry.shiftObject();
      if (!target) {
        return resolve(swal.close());
      }
      swal({
        type: 'info',
        title: 'Batch: Compute All',
        text: `Running ${index}/${len}...`,
        showConfirmButton: false,
        showCancelButton: true,
        focusCancel: true,
        cancelButtonClass: "ui red basic button",
        allowOutsideClick: false,
        allowEscapeKey: false,
        allowEnterKey: false,
      }).catch(dismiss => {
        entry.clear();
        swal({
          type: 'warning',
          title: 'Batch: Stop requested',
          text: `It will end after the current process #${index}.
                 Please wait little more...`,
          showConfirmButton: false,
          showCancelButton: false,
          allowOutsideClick: false,
          allowEscapeKey: false,
          allowEnterKey: false,
        });
      });
      target[task]().then(next.bind(null, index + 1));
    })(index);
  });
  return promise;
}
