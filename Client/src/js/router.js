
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
            templateUrl: 'templates/product/products.html',
            // controller: 'ProductCtrl'
        })
        .state('index.productEdit', {
            url: 'products/create',
            templateUrl: 'templates/product/product_edit.html'
        })
        .state('index.productDetail', {
            url: 'product/:id',
            templateUrl: 'templates/product/product_detail.html'
        })
        .state('index.shipment', {
            url: 'shipment',
            templateUrl: 'templates/shipment/shipments.html'
        })
        .state('index.addSupply', {
            url: 'supply/create',
            templateUrl: 'templates/shipment/supply-create.html'
        })
        .state('index.createShipOversea', {
            url: 'shipment/create',
            templateUrl: 'templates/shipment/oversea-create.html'
        })
        .state('index.settlement', {
            url: 'settlement',
            templateUrl: 'templates/settlements.html'
        })
    ;
}]);