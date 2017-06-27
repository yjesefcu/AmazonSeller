app.controller('settlementCtrl', function ($scope, $rootScope, $http, $state, $stateParams, $interval, serviceFactory) {
    $scope.settlements = [];
    $scope.selectedSettlement = '';
    $scope.isCalculating = false;
    $scope.calcIndex = 0;
    var calcStatusInterval = null;
    $scope.readingReport = false;
    var readingReportInterval = null;
    $scope.isDownloading = false;

    var settlementId = $stateParams.id;
    $scope.selected = '';
    if (settlementId){
        $scope.selectedSettlement = parseInt(settlementId);
    }
    getSettlements();
    function getSettlements(){

        $http.get(serviceFactory.settlements(), {
            params: {
                MarketplaceId: $rootScope.MarketplaceId
            }
        }).then(function (result) {
            $scope.settlements = result.data;
        }).catch(function () {
            $rootScope.addAlert('error', '获取结算列表失败')
        });
    }
    $scope.$watch('selectedSettlement', function (newValue, oldValue) {
        console.log('change');
        if (newValue)
        {
            $state.go('index.settlement.detail', {id: newValue});
        }
    });

    $scope.startCalculate = function (index, id) {
        $scope.calcIndex = index;
        $http.get(serviceFactory.settlementDetail(id) + 'calc/')
            .then(function (result) {
                var errno = result.data.errno;
                $rootScope.addAlert('info', '正在计算，请稍候...');
                $scope.settlements[index]['calc_status'] = errno ? 1 : 10;
                if (!calcStatusInterval){
                    calcStatusInterval = $interval(function () {
                        console.log('query calculating status');
                        $http.get(serviceFactory.settlementDetail(id) + 'calcStatus/').then(function (result) {
                            var errno = result.data.errno;
                            if (errno == 0){
                                $rootScope.addAlert('info', '计算完成');
                                $interval.cancel(calcStatusInterval);
                                calcStatusInterval = null;
                                getSettlements();
                            }else if (errno == 1){
                                $rootScope.addAlert('info', '计算失败');
                                $interval.cancel(calcStatusInterval);
                                calcStatusInterval = null;
                            }
                            $scope.settlements[index]['calc_status'] = errno;
                            console.log('calculating status: ' + errno);
                        }).catch(function (result) {
                            console.log('query calculating status error');
                        });
                    }, 5000);
                }
            }).catch(function (result) {
                $scope.settlements[index]['calc_status'] = 10;
                $rootScope.addAlert('error', '启动计算失败');
            });
    };

    $scope.startReadingReport = function () {
         $http.get(serviceFactory.settlements() + 'sync/', {
             params: {
                 MarketplaceId: $rootScope.MarketplaceId
             }
         }).then(function (result) {
             if (!readingReportInterval){
                 readingReportInterval = $interval(function () {
                     console.log('query getting report status');
                     $http.get(serviceFactory.settlements() + 'syncStatus/', {
                         params: {
                             MarketplaceId: $rootScope.MarketplaceId
                         }}).then(function (result) {
                         if (!result.data.errno){
                             $scope.readingReport = false;
                             $rootScope.addAlert('info', '同步完成');
                             $interval.cancel(readingReportInterval);
                             readingReportInterval = null;
                             getSettlements();
                         }
                         console.log('getting report: ' + result.data.errno);
                     }).catch(function (result) {
                         console.log('query getting report error');
                     });

                 }, 10000);
             }
             $scope.readingReport = true;
             $rootScope.addAlert('info', '正在同步...请勿关闭系统');
         }).catch(function () {
             $rootScope.addAlert('error', '启动失败！')
         })
    };
    $scope.$on('destroy',function(){
        calcStatusInterval && $interval.cancel(calcStatusInterval);
        readingReportInterval && $interval.cancel(readingReportInterval);
        calcStatusInterval = null;
        readingReportInterval = null;
    }) ; //在控制器里，添加$on函数

    $scope.download = function (id) {
        $scope.isDownloading = true;
        $http.get(serviceFactory.settlementDetail(id) + 'download/')
            .then(function (result) {
                $rootScope.addAlert('info', '报告已生成');
                $scope.isDownloading = false;
                window.location.href = serviceFactory.downloadPath(result.data.path);
            }).catch(function (result) {
                $scope.isDownloading = false;
                $rootScope.addAlert('error', '报告生成失败');
            });
    }
});

app.controller('settlementDetailCtrl', function ($scope, $rootScope, $http, $stateParams, $uibModal, $timeout, serviceFactory, fileUpload) {
    $scope.settlementId = $stateParams.settlementId;
    var settlementId = $scope.settlementId;
    $scope.isSettlement = true;
    $http.get(serviceFactory.settlementDetail(settlementId))
        .then(function (result) {
             $scope.settlement = result.data;
             // if (!$scope.settlement.subscribe_fee){
             //     openSetModal();
             // }
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
    $timeout(function () {

        angular.element("#storageFile").on('change', function(){
            $scope.storageFile = this.files[0];
        });
    }, 1000);
    $scope.sendStorageFile = function(){
        var url = serviceFactory.settlementDetail(settlementId) + 'storage_upload/',
            file = $scope.storageFile;
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


app.controller('settlementOrdersCtrl', function ($scope, $rootScope, $http, $stateParams, $uibModal, serviceFactory, fileUpload, $timeout) {
    var settlementId = $stateParams.settlementId, productId = $stateParams.productId ? $stateParams.productId : '';
    $scope.settlementId = settlementId;
    $scope.isSettlement = productId ? false : true;
    $scope.fileToUpload = null;
    $scope.productSummary = {};
    $scope.products = [];
    $scope.orderSummary = {};
    $scope.orders = [];
    $scope.refundSummary = {};
    $scope.refunds = [];
    $scope.removalSummary = {};
    $scope.removals = [];
    $scope.lostSummary = {};
    $scope.losts = [];
    $scope.settlement = {};
    $scope.productLoading = true;
    $scope.orderLoading = true;
    $scope.refundLoading = true;
    $scope.removalLoading = true;
    $scope.lostLoading = true;
    var getTotalParam = {
        settlement: settlementId,
        product: productId,
        is_total: 1
    }, getListParam = {
        settlement: settlementId,
        is_total: 0
    };
    if (productId){
        getListParam['product'] = productId;
    }
    getOrders();
    getRefunds();
    getRemovals();
    getLosts();
    if ($scope.isSettlement)
    {
        getProducts();
    }

    function getProducts() {
        $http.get(serviceFactory.settlementProducts(settlementId), {
            params: getListParam})
            .then(function (result) {
                $scope.productLoading = false;
                $scope.products = result.data;
            }).catch(function (result) {
                $scope.productLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
            });
        $http.get(serviceFactory.settlementProducts(settlementId), {
            params: getTotalParam})
            .then(function (result) {
                if (result.data.length)
                {
                    $scope.productSummary = result.data[0];
                }
            }).catch(function (result) {
                $rootScope.addAlert('warning', '获取商品列表失败');
            });
    }

    function getOrders() {
        $http.get(serviceFactory.settlementOrders(settlementId), {
            params: getListParam})
            .then(function (result) {
                $scope.orderLoading = false;
                $scope.orders = result.data;
            }).catch(function (result) {
                $scope.orderLoading = false;
                $rootScope.addAlert('warning', '获取商品列表失败');
            });
        $http.get(serviceFactory.settlementOrders(settlementId), {
            params: getTotalParam})
            .then(function (result) {
                if (result.data.length){
                    $scope.orderSummary = result.data[0];
                }
            }).catch(function (result) {
                $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }
    function getRefunds() {
        $http.get(serviceFactory.settlementRefunds(settlementId), {
            params: getListParam})
            .then(function (result) {
                $scope.refundLoading = false;
                $scope.refunds = result.data;
            }).catch(function (result) {
            $scope.refundLoading = false;
            $rootScope.addAlert('warning', '获取商品列表失败');
        });
        $http.get(serviceFactory.settlementRefunds(settlementId), {
            params: getTotalParam})
            .then(function (result) {
                if (result.data.length);
                {
                    $scope.refundSummary = result.data[0];
                }
            }).catch(function (result) {
            $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }
    function getRemovals() {
        $http.get(serviceFactory.settlementRemovals(settlementId), {
            params: getListParam})
            .then(function (result) {
                $scope.removalLoading = false;
                $scope.removals = result.data;
            }).catch(function (result) {
            $scope.removalLoading = false;
            $rootScope.addAlert('warning', '获取商品列表失败');
        });
        $http.get(serviceFactory.settlementRemovals(settlementId), {
            params: getTotalParam})
            .then(function (result) {
                if (result.data.length){
                    $scope.removalSummary =result.data[0];
                }
            }).catch(function (result) {
            $rootScope.addAlert('warning', '获取商品列表失败');
        });
    }
    function getLosts() {
        $http.get(serviceFactory.settlementLosts(settlementId), {
            params: getListParam})
            .then(function (result) {
                $scope.lostLoading = false;
                $scope.losts = result.data;
            }).catch(function (result) {
            $scope.lostLoading = false;
            $rootScope.addAlert('warning', '获取商品列表失败');
        });
        $http.get(serviceFactory.settlementLosts(settlementId), {
            params: getTotalParam})
            .then(function (result) {
                if (result.data.length){
                    $scope.lostSummary =result.data[0];
                }
            }).catch(function (result) {
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
    $timeout(function () {

        angular.element("#removalFile").on('change', function(){
            $scope.fileToUpload = this.files[0];
        });
    }, 1000);
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
    // $("#removalFile").filestyle({buttonName: "btn-default", placeholder: "选择亚马逊下载的移除报告", buttonText: "浏览"});
})