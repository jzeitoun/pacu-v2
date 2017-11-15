export function mul(arr1, arr2) {
  const arr = new Array(arr1.length);
  return arr.fill().map((_, index) => {
    return arr1[index] * arr2[index];
  });
}
export function div(arr1, arr2) {
  const arr = new Array(arr1.length);
  return arr.fill().map((_, index) => {
    return arr1[index] / arr2[index];
  });
}
export function sub(arr1, arr2) {
  const arr = new Array(arr1.length);
  return arr.fill().map((_, index) => {
    return arr1[index] - arr2[index];
  });
}
export function add(arr1, arr2) {
  const arr = new Array(arr1.length);
  return arr.fill().map((_, index) => {
    return arr1[index] + arr2[index];
  });
}
export function sum(arr) {
  return arr.reduce((x, y) => x + y);
}
