/**
 * Created by liucaiyun on 2017/5/22.
 */
app.controller('ProductCtrl', function($scope, $http, $rootScope, $uibModal, $location, serviceFactory) {
    $scope.products = [];
    $http.get(serviceFactory.getAllProducts(), {
        params: {
            MarketplaceId: $rootScope.MarketplaceId,
            dataType: "json"
        }
    }).then(function (result) {
        $scope.products = result.data;
    }).catch(function (result) {
        $rootScope.addAlert('danger', '获取商品列表失败，status=' + result.status);
    });

    $scope.openSupplyModal = function (id) {
        var modalInstance = $uibModal.open({
            templateUrl : 'templates/product/add_supply.html',//script标签中定义的id
            controller : 'supplyModalCtrl',//modal对应的Controller
            resolve : {
                data : function() {//data作为modal的controller传入的参数
                    return id;//用于传递数据
                }
            }
        });
    };
});

//模态框对应的Controller
app.controller('supplyModalCtrl', function($scope, $rootScope, $http, serviceFactory, $uibModalInstance, data) {
    $scope.productId = data;
    $scope.supply = {product: data};
    //在这里处理要进行的操作
    $scope.save = function() {
        $scope.supply['inventory'] = $scope.supply['count'];       // 设置剩余数量与总数量一致
        $http.post(serviceFactory.supplyList($scope.productId), $scope.supply)
            .then(function (result) {
                $rootScope.addAlert('success', '添加入库信息成功');
                $uibModalInstance.close();
            }).catch(function (result) {
                if (result.status == 400){
                    var msg = [];
                    for (var key in result.data){
                        msg.push(key+"： " + result.data[key]);
                    }
                    $rootScope.addAlert('danger', '添加入库信息失败：'+ msg.join('; '));
                }
                else{
                    $rootScope.addAlert('danger', '添加入库信息失败，状态码：' + result.status);
                }
        });
    };
    $scope.cancel = function() {
        $uibModalInstance.close();
    }
});

app.directive('tableRepeatDirective', function($timeout) {
    return function(scope, element, attrs) {
        if (scope.$last){   // 表格repeat完毕
            $timeout(function(){
                if (angular.element(element.parent().parent())[0].nodeName == 'TABLE'){
                    angular.element(element.parent().parent()).DataTable({
                        "paging": true,
                        "lengthChange": true,
                        "searching": true,
                        "ordering": false,
                        "info": true,
                        "autoWidth": false
                    });
                }
            }, 1000);
        }
    };
});

app.controller("ProductEditCtrl", function ($scope, $http, $rootScope, $location, $state, $timeout, $stateParams, serviceFactory, atomicNotifyService) {
    $scope.formData = {'MarketplaceId': $rootScope.MarketplaceId};
    $scope.productIcon = '';
    $scope.thumb = {};
    $scope.inbounds = [];
    $scope.showSupplies = false;
    $scope.showShipments = false;
    var productId=$stateParams.id, settlementId=$stateParams.settlementId;
    $scope.isDetail = productId ? true : false;
    if (productId){     // 编辑页面
        $http.get(serviceFactory.getProductDetail(productId)).then(function (result) {
            $scope.formData = result.data;
            $scope.productIcon = serviceFactory.mediaPath(result.data.Image);
        });
        getInboundShipment(productId);
    }
    $scope.submitForm = function () {
        var url = serviceFactory.createProduct(), method='post';
        if (productId){
            url = serviceFactory.getProductDetail(productId);
            method = 'patch';
        }
        $http({
            url: url,
            method: method,
            data: $scope.formData
        })
            .then(function (result) {
                if (productId){
                    $rootScope.addAlert('success', '保存成功', 3000);
                }else{
                    $rootScope.addAlert('success', '添加商品成功', 1000);
                    productId = result.data.id;
                    $scope.formData = result.data;
                }
            }).catch(function (result) {
                if (result.status == 400){
                    var msg = [];
                    for (var key in result.data){
                        msg.push(key+"： " + result.data[key]);
                    }
                    $rootScope.addAlert('danger', '保存失败：'+ msg.join('; '));
                }
                else{
                    $rootScope.addAlert('danger', '保存失败，状态码：' + result.status);
                }
            });
    };

    $scope.img_upload = function(files) {       //单次提交图片的函数
        var data = new FormData(files[0]);      //以下为像后台提交图片数据
        data.append('image', files[0]);
        $http.post(
            serviceFactory.imageUpload(),
            data,
            {
                headers: {'Content-Type': undefined},
                transformRequest: angular.identity
            }
            ).then(function(result) {
                if (result.status == 200) {
                    $scope.productIcon = serviceFactory.mediaPath(result.data);
                    $scope.formData.Image = result.data;
                }
                else{
                    $rootScope.addAlert('danger', '上传图片失败');
                }
            }).catch(function (result) {
                if (result.status == 400){
                    var msg = [];
                    for (var key in result.data){
                        msg.push(key+"： " + result.data[key]);
                    }
                    $rootScope.addAlert('danger', '上传图片失败：'+ msg.join('; '));
                }
                else{
                    $rootScope.addAlert('danger', '上传图片失败，状态码：' + result.status);
                }
            });
    };
    $scope.settlements = [];
    if (productId){
        getSettlements();
    }
    function getSettlements() {
        $http.get(serviceFactory.getSettlements(productId)).then(function (result) {
            $scope.selectedSettlement = result.data[0];
            $scope.settlements = result.data;
            // getOrders(productId, result.data[0]);
            $timeout(function () {
                // $scope.$watch('selectedSettlement', function (newValue, oldValue) {
                // if (typeof(newValue) != 'undefined')
                // {
                //     console.log(newValue);
                // }
                // });
                // 如果settlementId不为空，则默认设置选择该settlement
                $("#settlementSelection").on('change', function () {
                    if ($(this).val())
                    {
                        $state.go('index.productDetail.settlement', {
                            id: productId,
                            settlementId: $(this).val()
                        });
                    }
                });
                $("#settlementSelection option[value='" + settlementId + "']").attr('selected', true);
            }, 500);
        });
    }

    function getInboundShipment(productId) {        // 获取入库货件
        $http.get(serviceFactory.getProductInbounds(productId)).then(function (result) {
            $scope.inbounds = result.data;
        });
    }
});

app.controller('ProductOrdersCtrl', function ($scope, $rootScope, $http, $location, $state, $stateParams, $timeout, serviceFactory) {
    var productId = $stateParams.id, settlementId=$stateParams.settlementId;
    $scope.orders = [];
    $scope.settlements = [];

    getOrders(productId, settlementId);

    function getOrders(productId, settlementId) {
        if (settlementId){
            $http.get(serviceFactory.getProductOrders(productId), {
                params: {
                    settlement: settlementId,
                    MarketplaceId: $rootScope.MarketplaceId
                }
            }).then(function (result) {
                $scope.orders = result.data;
                $timeout(function(){
                    angular.element('#ordersTable').DataTable({
                        "paging": true,
                        "lengthChange": true,
                        "searching": true,
                        "ordering": false,
                        "info": true,
                        "autoWidth": false
                    });
                }, 1000);
            });
        }
    }
});
