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

app.controller('settlementDetailCtrl', function ($scope, $rootScope, $http, $stateParams, serviceFactory) {
    var settlementId = $stateParams.id;
    $scope.products = [];
    $http.get(serviceFactory.settlementProducts(settlementId))
        .then(function (result) {
            $scope.products = result.data;
        }).catch(function (result) {
            $rootScope.addAlert('warning', '获取商品列表失败');
        });
});
