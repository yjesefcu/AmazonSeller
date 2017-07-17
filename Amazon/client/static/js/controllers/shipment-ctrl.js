app.controller('ShipmentCtrl', function ($scope, $http, $rootScope, serviceFactory) {
    $scope.shipments = [];
    $http.get(serviceFactory.outboundShipments(), {
        params: {
            MarketplaceId: $rootScope.MarketplaceId
        }
    }).then(function (result) {
        $scope.shipments = result.data;
    }).catch(function (result) {

    });

    $scope.deleteShipment = function(index, id){
        $http.delete(serviceFactory.shipmentDetail(id))
            .then(function (result) {
                $rootScope.addAlert('info', '删除成功');
                $scope.shipments.splice(index, 1);
            }).catch(function (result) {
                if (result.status == 400){
                    $rootScope.addAlert('error', '需删除所有商品记录后才能删除');
                    return;
                }
                $rootScope.addAlert('error', '修改失败');
            });
    }
});

app.controller('OutboundEditCtrl', function ($scope, $http, $rootScope, $stateParams, $state, $timeout, serviceFactory) {
    var id = $stateParams.id;
    $scope.formData = {MarketplaceId: $rootScope.MarketplaceId};
    $scope.products = [];
    $scope.error_msg = '';
    $scope.addProductRow = function () {
        $scope.products.push({});
    };
    $scope.isDetail = id ? true : false;
    getShipment(id);
    function getShipment(id) {
        $http.get(serviceFactory.shipmentDetail(id)).then(function (result) {
            $scope.formData = result.data;
            $scope.products = result.data.products;
        });
    }
    $scope.save = function () {
        $scope.error_msg = '';
        var method, url;
        if (id){
            $scope.formData['id'] = id;
            method = 'patch';
            url = serviceFactory.shipmentDetail(id);
        }else{
            method = 'post';
            url = serviceFactory.outboundShipments();
        }
        $scope.formData['products'] = $scope.products;
        $http({
            url: url,
            method: method,
            data: $scope.formData
        }).then(function (result) {
            console.log('create outbound shipment success');
            $state.go('index.shipmentDetail', {id: result.data.id});
        }).catch(function (result) {
            console.log('create outbound shipment failed');
            $rootScope.addAlert('danger', '保存失败');
            if (result.status == 400){
                $scope.error_msg = result.data.msg;
            }
        });
    };

    $scope.remove = function (index) {
        $scope.products.splice(index, 1);
    };

    $scope.saveItem = function (index, id) {    // 保存修改
        $http.patch(serviceFactory.shipmentItemDetail(id), {unit_cost:$scope.products[index].unit_cost})
            .then(function (result) {
                $rootScope.addAlert('info', '修改成功');
                $scope.products[index] = result.data;
                $scope.products[index].isEdit = false;
            }).catch(function (result) {
                $rootScope.addAlert('error', '修改失败');
            });
    };

    $scope.deleteItem = function(index, id){    //删除子项
        $http.delete(serviceFactory.shipmentItemDetail(id))
            .then(function (result) {
                $rootScope.addAlert('info', '删除成功');
                $scope.products.splice(index, 1);
            }).catch(function (result) {
                if (result.status == 400){
                    $rootScope.addAlert('error', '库存 < 原始数量，无法删除');
                    return;
                }
                $rootScope.addAlert('error', '修改失败');
            });
    };

    $scope.deleteShipment = function(){
        $http.delete(serviceFactory.shipmentDetail(id))
            .then(function (result) {
                $rootScope.addAlert('info', '删除成功');
                $timeout(function(){
                    window.history.back();
                }, 1000);
            }).catch(function (result) {
                if (result.status == 400){
                    $rootScope.addAlert('error', '需删除所有商品记录后才能删除');
                    return;
                }
                $rootScope.addAlert('error', '修改失败');
            });
    }
});