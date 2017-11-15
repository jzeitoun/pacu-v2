import Ember from 'ember';
import { helper } from '@ember/component/helper';

const monthNames = [
  "January", "February", "March",
  "April", "May", "June", "July",
  "August", "September", "October",
  "November", "December"
];

export function fromTimestamp([timestamp, ...rest], hash) {
  if (Ember.$.type(timestamp) === 'string') {
    return timestamp;
  }
  const date = new Date(timestamp * 1000);
  const day = date.getDate();
  const monthIndex = date.getMonth();
  const year = date.getFullYear();
  if (hash.detailed) {
    const hour = date.getHours();
    const minute = date.getMinutes();
    return `${day} ${monthNames[monthIndex]} ${year} - ${hour}:${minute}`
  } else {
    return `${day} ${monthNames[monthIndex]} ${year}`
  }
}

export default helper(fromTimestamp);
