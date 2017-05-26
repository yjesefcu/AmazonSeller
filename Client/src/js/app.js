/**
 * Created by liucaiyun on 2017/5/4.
 */

var app = angular.module('myApp', ['ui.router']);

app.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/');

    $stateProvider
        .state('index', {
            url:'/',
            // templateUrl: 'index.html',
            // controller: 'HomeCtrl'
        })
        .state('index.products', {
            url:'products',
            templateUrl: 'templates/products.html',
            // controller: 'ProductCtrl'
        })
        .state('index.productEdit', {
            url: 'products/create',
            templateUrl: 'templates/product_edit.html'
        })
        ;
}]);

app.factory('serviceFactory', function () {
    var host='http://192.168.1.3:8000', services = {};
    services.createProduct = function () {
        return host + '/api/products/';
    };
    services.getAllProducts = function () {
        return host + '/api/products/';
    };

    return services;
});
app.config(function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        // Allow same origin resource loads.
        '**'])
});