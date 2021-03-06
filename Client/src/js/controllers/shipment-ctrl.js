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
});

app.controller('OutboundEditCtrl', function ($scope, $http, $rootScope, $stateParams, $state, serviceFactory) {
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
    }
});