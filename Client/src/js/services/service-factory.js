
app.factory('serviceFactory', function ($rootScope) {
    var host='http://192.168.1.3:8000', services = {};
    $rootScope.host = host;
    services.markets = function () {
        return host + '/api/markets/';
    };
    services.getSettlements = function (productId) {
        if (productId){
            return host + '/api/products/' + productId + '/settlements/';
        }
        return host + '/api/settlements/';
    };
    services.createProduct = function () {
        return host + '/api/products/';
    };
    services.getAllProducts = function () {
        return host + '/api/products/';
    };
    services.getProductDetail = function (id) {
        return host + '/api/products/' + id + '/';
    };
    services.getProductSupply = function (productId) {
        return host + '/api/products/' + productId + '/supply/';
    };
    services.getProductShipments = function (productId) {
        return host + '/api/products/' + productId + '/shipments/';
    };
    services.getProductOrders = function (id) {
        return host + '/api/products/' + id + '/orders';
    };
    services.getProductRefunds = function (id) {
        return host + '/api/products/' + id + '/refunds';
    };
    services.getProductLosts = function (id) {
        return host + '/api/products/' + id + '/losts';
    };
    services.getProductRemovals = function (id) {
        return host + '/api/products/' + id + '/removals';
    };
    services.supplyList = function (productId) {
        return host + '/api/products/' + productId + '/supply/';
    };
    services.outboundShipments = function () {
        return host + '/api/shipments/';
    };
    services.shipmentDetail = function (id) {
        return host + '/api/shipments/' + id + '/';
    };
    services.settlements = function () {
        return host + '/api/settlements/';
    };
    services.settlementDetail = function (id) {
        return host + '/api/settlements/' + id + '/';
    };
    services.settlementProducts = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/products/';
    };
    services.settlementOrders = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/orders/';
    };
    services.settlementRefunds = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/refunds/';
    };
    services.settlementRemovals = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/removals/';
    };
    services.settlementLosts = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/losts/';
    };
    services.settlement = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/orders/';
    };
    services.imageUpload = function () {
        return host + '/image/upload/';
    };
    services.mediaPath = function (imagePath) {
        return host + imagePath;
    };
    services.uploadRemovals = function (settlementId) {
        return host + '/api/settlements/' + settlementId + '/removals/upload/';
    };
    return services;
});