/**
 * Created by liucaiyun on 2018/1/27.
 */
'use strict';

app.controller('PurchasingOrderCreateCtrl', function ($scope, $http, $rootScope, $state) {
    $scope.orders = [];
    $scope.contract = {};

    $scope.addOrderItem = function () {
        $scope.orders.push({});
    };

    $scope.save = function () {
        $http.post('/api/purchasing/', {
            contract: $scope.contract,
            orders: $scope.orders
        }).then(function (result) {
            $state.go('index.purchasing');
        }).catch(function (error) {
            $rootScope.addAlert('error', '创建采购单失败');
        });
    };
});

app.controller('PurchasingOrderListCtrl', function ($scope, $http, $rootScope) {
    $scope.orders = [];

    function getData() {
        $http.get('/api/purchasing/').then(function (result) {
            $scope.orders = result.data;
        }).catch(function (error) {
             $rootScope.addAlert('error', '获取采购单失败');
        });
    }

    getData();
});

app.controller('PurchasingOrderDetailCtrl', function ($scope, $http, $rootScope, $stateParams, $uibModal) {
    $scope.orderId = $stateParams.orderId;
    $scope.order = {};
    $scope.product = {};
    $scope.inbounds = [];

    function getData() {
        $http.get('/api/purchasing/' + $scope.orderId + '/').then(function (result) {
            $scope.order = result.data;
            $scope.product = result.data.product;
        }).catch(function (error) {
            $rootScope.addAlert('error', '获取订单信息失败');
        });
    }

    function getInbounds () {
        $http.get('/api/purchasing/' + $scope.orderId + '/inbounds/').then(function (result) {
            $scope.inbounds = result.data;
        }).catch(function (error) {

        });
    }
    $scope.update = function (params) {
        $http.patch('/api/purchasing/' + $scope.orderId + '/', params).then(function (result) {
            $rootScope.addAlert('info', '提交成功');
            $scope.refresh();
        }).catch(function (error) {
            $rootScope.addAlert('error', '提交失败');
        });
    };

    $scope.createInbound = function (params) {

        $http.post('/api/purchasing/' + $scope.orderId + '/inbounds/', params).then(function (result) {
            $rootScope.addAlert('info', '提交成功');
            $scope.refresh();
        }).catch(function (error) {
            $rootScope.addAlert('error', '提交失败');
        });
    };

    function init() {
        getData();
        getInbounds();
    }

    $scope.refresh = function () {
        init();
    };

    $scope.openInboudModal = function (id) {        // 打开创建入库信息的对话框
        var modalInstance = $uibModal.open({
            templateUrl : '/static/templates/purchasing/create_inbound.html',//script标签中定义的id
            controller : 'PurchasingAddInboundCtrl',//modal对应的Controller
            resolve : {
                data : function() {//data作为modal的controller传入的参数
                    return {
                        id: id,
                        orderId: $scope.orderId,
                        order: $scope.order,
                        product: $scope.product
                    };//用于传递数据
                }
            }
        });
        modalInstance.result.then(function (result) {
            getInbounds();
        });
    };

    $scope.updateInbound = function (inboundId, method, params) {
        var url = '/api/purchasing/' + $scope.orderId + '/inbounds/' + inboundId + '/' + method + '/';
        $http.post(url, params).then(function (result) {
            $rootScope.addAlert('info', '提交成功');
            $scope.refresh();
        }).catch(function (error) {
            $rootScope.addAlert('error', '提交失败');
        });
    };

    $scope.inboundTrafficFeeConfirm = function (inboundId) {
        var modalInstance = $uibModal.open({
            templateUrl : '/static/templates/purchasing/traffic_fee_confirm.html',//script标签中定义的id
            controller : 'InboundTrafficFeeConfirmCtrl',//modal对应的Controller
            resolve : {
                data : function() {//data作为modal的controller传入的参数
                    return {
                        id: inboundId,
                        orderId: $scope.orderId
                    };//用于传递数据
                }
            }
        });
        modalInstance.result.then(function (result) {
            $scope.refresh();
        });
    };
    init();
});

app.controller('PurchasingAddInboundCtrl', function ($scope, $http, $rootScope, $state, data, $uibModalInstance) {
    var inboundId=data.id, orderId = data.orderId;
    $scope.product = data.product;
    $scope.order = data.order;
    $scope.inbound = {};

    $scope.save = function () {
        var params = {
            inbound: $scope.inbound
        };
        if (productChanged) {
            params.product = $scope.product;
        }
        var prevStatus = $scope.order.status;
        $http.post('/api/purchasing/' + orderId + '/inbounds/' + inboundId + '/putin/', params).then(function (result) {
            $rootScope.addAlert('info', '提交成功');
            $uibModalInstance.close();
            $state.go('index.purchasingDetail({orderId: orderId})');
        }).catch(function (error) {
            $rootScope.addAlert('error', '提交失败');
        });
    };

    var productChanged = false;
    $scope.productChanged = function () {
        productChanged = true;
    };

    $scope.cancel = function() {
        $uibModalInstance.close();
    };
});

app.controller('InboundTrafficFeeConfirmCtrl', function ($scope, $http, $uibModalInstance, $rootScope, data) {
    var orderId=data.orderId, inboundId = data.id;

    $scope.submit = function () {
        $http.post('/api/purchasing/' + orderId + '/inbounds/' + inboundId + '/payed/', {
            traffic_fee_payed: $scope.traffic_fee_payed
        }).then(function (result) {
            $rootScope.addAlert('info', '提交成功');
            $uibModalInstance.close();
        }).catch(function (error) {
            $rootScope.addAlert('error', '提交失败');
        });
    };
});