// const mimetype = 'application/octet-stream';

/* global Uint8Array DataView */

export function fromByteString(byteString, filename, mimetype) {
  const a = document.createElement('a');
  a.style = "display: none";
  const blob = new Blob([byteString], {type: mimetype});
  const url = window.URL.createObjectURL(blob);
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(function() {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 100)
}
export function fromArrayBuffer(abuf, filename, mimetype) {
  const a = document.createElement('a');
  a.style = "display: none";
  const blob = new Blob([new DataView(abuf)], { type: mimetype });
  const url = window.URL.createObjectURL(blob);
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(function() {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 100)
}
function str2bytes(str) {
    const bytes = new Uint8Array(str.length);
    for (var i=0; i<str.length; i++) {
        bytes[i] = str.charCodeAt(i);
    }
    return bytes;
}
export function fromBase64(base64, filename, mimetype) {
  fromByteString(str2bytes(atob(base64)), filename, mimetype);
}


