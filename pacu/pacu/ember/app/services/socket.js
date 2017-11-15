import Ember from 'ember';
import Service from '@ember/service';
import RSVP from 'rsvp';

/* global ArrayBuffer DataView */

function log(...msgs) { console.log(...msgs); }

let sequence = 0;

function mirrorTo(target, route) {
  return this.makeRequest('access', route).then((data) => {
    target.set(route.camelize(), data);
    return data;
  });
}

class PromiseEx extends RSVP.Promise {
  constructor(resolver, label, context) {
    super(resolver, label);
    this.context = context;
    this.gatenames = null;
  }
  gate(...names) {
    if (Ember.isNone(this.gatenames)) {
      this.gatenames = names;
      this.gatenames.forEach((name) => {
        Ember.set(this.context, name, true);
      });
      super.finally(() => {
        this.gatenames.forEach((name) => {
          Ember.set(this.context, name, false);
        });
      });
    }
    return this;
  }
  gateTo(target, ...names) {
    if (Ember.isNone(this.gatenames)) {
      this.gatenames = names;
      this.gatenames.forEach((name) => {
        Ember.set(target, name, true);
      });
      super.finally(() => {
        this.gatenames.forEach((name) => {
          Ember.set(target, name, false);
        });
      });
    }
    return this;
  }
}

class WebSocketEx {
  constructor(context, url, binaryType='arraybuffer') {
    this.context = context;
    this.promises = {};
    this.constructionThens = [];
    this.constructionCatches = [];
    this.constructionFinallys = [];
    this.constructionPromise = new RSVP.Promise((res, rej) => {
      this.socket = new WebSocket(url);
      this.socket.binaryType = binaryType;
      this.socket.onmessage = this.onmessage.bind(this);
      this.socket.onopen = res.bind(this);
      this.socket.onerror = rej.bind(this);
      this.socket.onclose = function() {};
    }).then(() => {
      for (const f of this.constructionThens) f.call(context, this);
    }).catch((e) => {
      for (const f of this.constructionCatches) f.call(context, e);
    }).finally(() => {
      for (const f of this.constructionFinallys) f.call(context);
      this.constructionPromise = null;
      this.constructionThens = null;
      this.constructionCatches = null;
      this.constructionFinallys = null;
    });
  }
  dnit() {
    this.promises = null;
    this.context = null;
    this.socket.close();
    this.onbinaryFunc = null;
  }
  then(func) {
    if (Ember.isNone(this.constructionThens)) {
      console.error('Could not accept promise.');
    } else { this.constructionThens.push(func); }
    return this; // so that chain can go forth...
  }
  catch(func) {
    if (Ember.isNone(this.constructionCatches)) {
      console.error('Could not accept promise.');
    } else { this.constructionCatches.push(func); }
    return this; // so that chain can go forth...
  }
  finally(func) {
    if (Ember.isNone(this.constructionFinallys)) {
      console.error('Could not accept promise.');
    } else { this.constructionFinallys.push(func); }
    return this; // so that chain can go forth...
  }
  _mirror(route) {
    return this.makeRequest('access', route).then((data) => {
      this.context.set(route.camelize(), data);
    });
  }
  mirror(...routes) {
    if (routes.length === 1) {
      return this._mirror(...routes);
    }
    return RSVP.all(
      routes.map(this._mirror.bind(this))
    )
  }
  // `mirrorTo` is preferred than just `mirror`
  mirrorTo(target, ...routes) {
    return RSVP.all(
      routes.map(route => mirrorTo.call(this, target, route)))
  }
  _print(route) {
    return this.access(route).then(log);
  }
  print(...routes) {
    if (routes.length === 1) {
      return this._print(...routes);
    }
    return RSVP.all(
      routes.map(this._print.bind(this))
    )
  }
  _access(route) {
    return this.makeRequest('access', route);
  }
  access(...routes) {
    if (routes.length === 1) {
      return this._access(...routes);
    }
    return RSVP.all(
      routes.map(this._access.bind(this))
    )
  }
  accessAsBinary(route) {
    return this.makeRequest('access', route, {as_binary: true});
  }
  invoke(route, ...args) {
    return this.makeRequest('invoke', route, {args, as_binary: false});
  }
  invokeAsBinary(route, ...args) {
    return this.makeRequest('invoke', route, {args, as_binary: true});
  }
  oncloseFunc(/*buf*/) {}
  onbinaryFunc(/*buf*/) {}
  onclose(func) { this.oncloseFunc = func.bind(this.context); return this; }
  onbinary(func) { this.onbinaryFunc = func.bind(this.context); return this; }
  makeRequest(type, route, payload={as_binary: false}) {
    return new PromiseEx((res, rej) => {
      this.promises[++sequence] = {res, rej};
      this.socket.send(JSON.stringify([sequence, type, route, payload]));
    }, null, this.context);
  }
  onmessage(msg) {
    if (msg.data instanceof ArrayBuffer) {
      const dv = new DataView(msg.data);
      const seq = dv.getUint32(0);
      const err = dv.getUint32(4);
      if (seq in this.promises) {
        const {res, rej} = this.promises[seq];
        if (delete this.promises[seq]) {
          if (err) {
            rej(err);
          } else {
            const chunk = msg.data.slice(8);
            this.onbinaryFunc(chunk);
            res(chunk);
          }
        }
      }
      return;
    }
    const [seq, argument, error] = JSON.parse(msg.data);
    if (seq in this.promises) {
      const {res, rej} = this.promises[seq];
      if (delete this.promises[seq]) {
        if (Ember.isNone(error)) {
          res(argument);
        } else {
          rej(error);
        }
      }
    } else { // SSE-ish
      try {
        this.context[`on_sse_${seq}`](argument, error);
      } catch (err) {
        log('Unhandled SSE message:', `on_sse_${seq}`, err);
      }
    }
  }
  static asBufBased(context, url) {
    return new WebSocketEx(context, url, 'arraybuffer');
  }
  static asBlobBased(context, url) {
    return new WebSocketEx(context, url, 'blob');
  }
}

export default Service.extend({
  create(context, modname, clsname, src) {
    if (Ember.isNone(src)) {
      var url;
      url = `ws://${location.host}/ws/${modname}/${clsname}`;
    } else {
      if (Ember.$.isPlainObject(src)) {
        var qs = Ember.$.param(src);
        url = `ws://${location.host}/ws/${modname}/${clsname}?${qs}`;
      } else {
        url = `ws://${location.host}/ws/${modname}/${clsname}?files=${src}`;
      }
    }
    return new WebSocketEx.asBufBased(context, url);
  }
});
