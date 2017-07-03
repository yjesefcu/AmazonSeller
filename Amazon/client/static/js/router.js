
app.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/settlement');

    $stateProvider
        .state('index', {
            url:'/'
            // templateUrl: 'index.html',
            // controller: 'HomeCtrl'
        })
        .state('index.products', {
            url:'products',
            templateUrl: '/static/templates/product/products.html'
            // controller: 'ProductCtrl'
        })
        .state('index.productEdit', {
            url: 'products/create',
            templateUrl: '/static/templates/product/product_edit.html'
        })
        .state('index.productDetail', {
            url: 'product/:productId',
            templateUrl: '/static/templates/product/product_detail.html'
        })
        .state('index.productDetailEdit', {
            url: 'product/:productId/edit',
            templateUrl: '/static/templates/product/product_edit.html'
        })
        .state('index.productDetail.settlement', {
            url: '/settlement/:settlementId',
            templateUrl: '/static/templates/product/product_orders.html'
        })
        .state('index.productDetail.settlement.orders', {
            url: '/orders',
            templateUrl: '/static/templates/settlement_order_detail.html',
            controller: 'settlementOrdersCtrl'
        })
        .state('index.shipment', {
            url: 'shipment',
            templateUrl: '/static/templates/shipment/shipments.html'
        })
        .state('index.addSupply', {
            url: 'supply/create',
            templateUrl: '/static/templates/shipment/supply-create.html'
        })
        .state('index.createShipOversea', {
            url: 'shipment/create',
            templateUrl: '/static/templates/shipment/outbound_create.html'
        })
        .state('index.shipmentDetail', {
            url: 'shipment/:id',
            templateUrl: '/static/templates/shipment/shipment_detail.html'
        })
        .state('index.settlement', {
            url: 'settlement',
            templateUrl: '/static/templates/settlement/settlements.html'
        })
        .state('index.settlement.detail', {
            url: '/:settlementId',
            templateUrl: '/static/templates/settlement/settlement_detail.html'
        })
        .state('index.settlement.detail.orders', {
            url: '/orders',
            templateUrl: '/static/templates/settlement_order_detail.html',
            controller: 'settlementOrdersCtrl'
        })
    ;
}]);