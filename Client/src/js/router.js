
app.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/products');

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
            url: 'product/:productId',
            templateUrl: 'templates/product/product_detail.html'
        })
        .state('index.productDetailEdit', {
            url: 'product/:productId/edit',
            templateUrl: 'templates/product/product_edit.html'
        })
        .state('index.productDetail.settlement', {
            url: '/settlement/:settlementId',
            templateUrl: 'templates/product/product_orders.html'
        })
        .state('index.productDetail.settlement.orders', {
            url: '/orders',
            templateUrl: 'templates/settlement_order_detail.html',
            controller: 'settlementOrdersCtrl'
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
            templateUrl: 'templates/shipment/outbound_create.html'
        })
        .state('index.shipmentDetail', {
            url: 'shipment/:id',
            templateUrl: 'templates/shipment/outbound_create.html'
        })
        .state('index.settlement', {
            url: 'settlement',
            templateUrl: 'templates/settlement/settlements.html'
        })
        .state('index.settlement.detail', {
            url: '/:settlementId',
            templateUrl: 'templates/settlement/settlement_detail.html'
        })
        .state('index.settlement.detail.orders', {
            url: '/orders',
            templateUrl: 'templates/settlement_order_detail.html',
            controller: 'settlementOrdersCtrl'
        })
    ;
}]);