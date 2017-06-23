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

app.controller('settlementDetailCtrl', function ($scope, $rootScope, $http, $stateParams, $uibModal, serviceFactory, fileUpload) {
    var settlementId = $stateParams.id;
    $scope.products = [];
    $scope.orders = [];
    $scope.refunds = [];
    $scope.removals = [];
    $scope.losts = [];
    $scope.settlement = {};
    $scope.productLoading = true;
    $scope.orderLoading = true;
    $scope.refundLoading = true;
    $scope.removalLoading = true;
    $scope.lostLoading = true;
    $http.get(serviceFactory.settlementDetail(settlementId))
        .then(function (result) {
             $scope.settlement = result.data;
             // if (!$scope.settlement.subscribe_fee){
             //     openSetModal();
             // }
        });

    getOrders();
    getRefunds();
    getRemovals();
    getLosts();
    getProducts();
    function getProducts() {
        $http.get(serviceFactory.settlementProducts(settlementId))
            .then(function (result) {
                $scope.products = result.data;
                $scope.productLoading = false;
            }).catch(function (result) {
                $scope.productLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }

    function getOrders() {
        $http.get(serviceFactory.settlementOrders(settlementId))
            .then(function (result) {
                $scope.orderLoading = false;
                $scope.orders = result.data;
            }).catch(function (result) {
                $scope.orderLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }
    function getRefunds() {
        $http.get(serviceFactory.settlementRefunds(settlementId))
            .then(function (result) {
                $scope.refundLoading = false;
                $scope.refunds = result.data;
            }).catch(function (result) {
                $scope.refundLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }
    function getRemovals() {
        $http.get(serviceFactory.settlementRemovals(settlementId))
            .then(function (result) {
                $scope.removalLoading = false;
                $scope.removals = result.data;
            }).catch(function (result) {
                $scope.removalLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }
    function getLosts() {
        $http.get(serviceFactory.settlementLosts(settlementId))
            .then(function (result) {
                $scope.lostLoading = false;
                $scope.losts = result.data;
            }).catch(function (result) {
                $scope.lostLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }

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

    $scope.sendFile = function(){
        var url = serviceFactory.uploadRemovals(settlementId),
            file = $scope.fileToUpload;
        if ( !file ) return;
        fileUpload.uploadFileToUrl(file, url, function (data) {
            if (!data.errno){
                $rootScope.addAlert('success', '上传成功，一共找到' + data.data.length + '条记录');
                $scope.removals = data.data;
            }else {
                $rootScope.addAlert('error', '上传失败，请确认上传文件是否移除报告');
            }
        });
    };
    $("#removalFile").filestyle({buttonName: "btn-default", placeholder: "选择亚马逊下载的移除报告", buttonText: "浏览"});
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