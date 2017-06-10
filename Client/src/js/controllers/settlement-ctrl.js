app.controller('settlementCtrl', function ($scope, $rootScope, $http, serviceFactory) {
    $scope.settlements = [];
    $http.get(serviceFactory.settlements(), {
        params: {
            MarketplaceId: $rootScope.MarketplaceId
        }
    }).then(function (result) {
        $scope.settlements = result.data;
    });
});
