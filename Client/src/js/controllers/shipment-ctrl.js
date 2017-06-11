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

app.controller('OutboundEditCtrl', function ($scope, $http, $rootScope, $stateParams, serviceFactory) {
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
        }).catch(function (result) {
            console.log('create outbound shipment failed');
            $rootScope.addAlert('danger', '保存失败');
            if (result.status == 400){
                $scope.error_msg = result.data.msg;
            }
        });
    };
});