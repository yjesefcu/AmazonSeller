app.controller('settlementCtrl', function ($scope, $rootScope, $http, $state, $stateParams, serviceFactory) {
    $scope.settlements = [];
    $scope.selectedSettlement = '';
    $http.get(serviceFactory.settlements(), {
        params: {
            MarketplaceId: $rootScope.MarketplaceId
        }
    }).then(function (result) {
        $scope.settlements = result.data;
    });
    var settlementId = $stateParams.id;
    $scope.selected = '';
    if (settlementId){
        $scope.selectedSettlement = parseInt(settlementId);
    }
    $scope.$watch('selectedSettlement', function (newValue, oldValue) {
        console.log('change');
        if (newValue)
        {
            $state.go('index.settlement.detail', {id: newValue});
        }
    });
});

app.controller('settlementDetailCtrl', function ($scope, $rootScope, $http, $stateParams, $uibModal, serviceFactory) {
    var settlementId = $stateParams.id;
    $scope.products = [];
    $scope.settlement = {};
    $http.get(serviceFactory.settlementDetail(settlementId))
        .then(function (result) {
             $scope.settlement = result.data;
             if (!$scope.settlement.subscribe_fee){
                 openSetModal();
             }
        });
    $http.get(serviceFactory.settlementProducts(settlementId))
        .then(function (result) {
            $scope.products = result.data;
        }).catch(function (result) {
            $rootScope.addAlert('warning', '获取商品列表失败');
        });

    function openSetModal() {
        var modalInstance = $uibModal.open({
            templateUrl : 'templates/settlement/set_fee.html',//script标签中定义的id
            controller : 'setFeeCtrl',//modal对应的Controller
            resolve : {
                data : function() {//data作为modal的controller传入的参数
                    return $scope.settlement;//用于传递数据
                }
            }
        });
    }
    $scope.$on("subscribeFeeChange", function (event, msg) {
         $scope.settlement.subscribe_fee = msg;
     });
})
.controller('setFeeCtrl', function($scope, $rootScope, $http, $state, serviceFactory, $uibModalInstance, data) {
    $scope.settlement = data;
    //在这里处理要进行的操作
    $scope.save = function() {
        $http.patch(serviceFactory.settlementDetail($scope.settlement.id), {
            subscribe_fee: $scope.subscribe_fee
        }).then(function (result) {
            $uibModalInstance.close();
            $scope.$emit("subscribeFeeChange", $scope.subscribe_fee);
        }).catch(function (result) {
            $rootScope.addAlert('danger', '设置失败');
        });
    };
    $scope.cancel = function() {
        $uibModalInstance.close();
    }
});