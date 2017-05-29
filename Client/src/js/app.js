/**
 * Created by liucaiyun on 2017/5/4.
 */

var app = angular.module('myApp', ['ui.router', 'atomic-notify', 'ui.bootstrap', '720kb.datepicker']);

app.controller('MainCtrl', function ($rootScope) {
   $rootScope.MarketplaceId = 'ATVPDKIKX0DER' ;
    $rootScope.alerts = [];

    $rootScope.addAlert = function (type, msg, timeout) {
        if (typeof(timeout) == 'undefined'){
            timeout = 3000;
        }
        $rootScope.alerts.push({
            type: type, msg: msg, "dismiss-on-timeout": timeout, close: function () {
                return $rootScope.closeAlert(this);
            },
        });
    };
    $rootScope.closeAlert = function (index) {
        $rootScope.alerts.splice(index, 1);
    };
});

app.config(['atomicNotifyProvider', function(atomicNotifyProvider){

    // atomicNotifyProvider.setDefaultDelay(5000);
    // atomicNotifyProvider.useIconOnNotification(true);

}]);

app.factory('serviceFactory', function () {
    var host='http://192.168.1.3:8000', services = {};
    services.createProduct = function () {
        return host + '/api/products/';
    };
    services.getAllProducts = function () {
        return host + '/api/products/';
    };
    services.supplyList = function (productId) {
        return host + '/api/products/' + productId + '/supply/';
    };
    services.imageUpload = function () {
        return host + '/image/upload/';
    };
    services.mediaPath = function (imagePath) {
        return host + '/' + imagePath;
    };
    return services;
});
app.config(function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        // Allow same origin resource loads.
        '**'])
});
