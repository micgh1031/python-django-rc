(function () {
  'use strict';

  angular
    .module('WSI-API', [
      'wsi.users'
    ]);

  angular
    .module('WSI-API')
    .config(config);

  angular
    .module('WSI-API')
    .run(run);

  config.$inject = ['$interpolateProvider'];
  run.$inject = ['$http', '$rootScope'];

  function config($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  }

  function run($http, $rootScope) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';
  }
})();
