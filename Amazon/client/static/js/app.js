/**
 * Created by liucaiyun on 2017/5/4.
 */

var app = angular.module('myApp', ['ui.router', 'atomic-notify', 'ui.bootstrap', '720kb.datepicker']);

app.controller('MainCtrl', function ($scope, $state, $http, $rootScope, $location, serviceFactory) {
    $rootScope.currentMarket = {'country': '美国'};
    $rootScope.MarketplaceId = 'ATVPDKIKX0DER' ;
    $rootScope.alerts = [];
    $scope.markets = [];
    $rootScope.currentcy = 'USD';
    $scope.currentUrl = $location.$$path;
    $rootScope.addAlert = function (type, msg, timeout) {
        if (typeof(timeout) == 'undefined'){
            timeout = 3000;
        }
        $rootScope.alerts.push({
            type: type, msg: msg, "dismiss-on-timeout": timeout, close: function () {
                return $rootScope.closeAlert(this);
            }
        });
    };
    $rootScope.closeAlert = function (index) {
        $rootScope.alerts.splice(index, 1);
    };

    $http.get(serviceFactory.markets())
        .then(function (result) {
             $scope.markets = result.data;
             $rootScope.currentMarket = result.data[0];
             $rootScope.currency = $rootScope.currentMarket.currency;
        });

    $scope.chooseMarket = function (index) {
        $rootScope.currentMarket = $scope.markets[index];
        $rootScope.MarketplaceId = $rootScope.currentMarket.MarketplaceId;
        $rootScope.currency = $rootScope.currentMarket.currency;
        $state.go('index');
    }
});

app.config(['atomicNotifyProvider', function(atomicNotifyProvider){

    // atomicNotifyProvider.setDefaultDelay(5000);
    // atomicNotifyProvider.useIconOnNotification(true);

}]);

app.config(function($sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        // Allow same origin resource loads.
        '**'])
});
