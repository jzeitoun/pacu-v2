/* eslint-env node */
'use strict';

module.exports = function(environment) {
  let ENV = {
    modulePrefix: 'pacu-v2',
    environment,
    rootURL: '/',
    locationType: 'auto',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      },
      EXTEND_PROTOTYPES: {
        // Prevent Ember Data from overriding Date.parse.
        Date: false
      }
    },

    firebase: {
      apiKey: "AIzaSyCfQPiJ0rKVY3-NBriIQyMgQTr0t43zr9c",
      authDomain: "pacu-rois.firebaseapp.com",
      databaseURL: "https://pacu-rois.firebaseio.com",
      projectId: "pacu-rois",
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created
    }
  };

  ENV['ember-toastr'] = {
    toastrOptions: {
      positionClass: 'toast-top-center',
      preventDuplicates: false,
      timeOut: '2000'
    }
  };

  if (environment === 'development') {
    // ENV.APP.LOG_RESOLVER = true;
    // ENV.APP.LOG_ACTIVE_GENERATION = true;
    // ENV.APP.LOG_TRANSITIONS = true;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = true;
    // ENV.APP.LOG_VIEW_LOOKUPS = true;
  }

  if (environment === 'debug') {
    ENV.firebase = {
      apiKey: "AIzaSyBaX7SulTE4gCIIiY5Euu9iKwIUfMrIFaE",
      authDomain: "pacu-development.firebaseapp.com",
      databaseURL: "https://pacu-development.firebaseio.com",
      projectId: "pacu-development",
    };
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.locationType = 'none';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';
  }

  if (environment === 'production') {
    // here you can enable a production-specific feature
  }

  return ENV;
};
