/**
 * Created by liucaiyun on 2017/5/22.
 */

app.controller('ProductCtrl', function($scope, $http, $rootScope, $uibModal, serviceFactory) {
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
                $(element.parent().parent()[0]).DataTable({
                    "paging": true,
                    "lengthChange": true,
                    "searching": true,
                    "ordering": false,
                    "info": true,
                    "autoWidth": false
                });
            }, 500);
        }
    };
});
app.controller("ProductEditCtrl", function ($scope, $http, $rootScope, serviceFactory, atomicNotifyService) {
    $scope.formData = {'MarketplaceId': $rootScope.MarketplaceId};
    $scope.productIcon = '';
    $scope.thumb = {};
    $scope.submitForm = function () {
        var url = serviceFactory.createProduct();
        $http.post(url, $scope.formData)
            .then(function (result) {
                $rootScope.addAlert('success', '添加商品成功', 1000);
            }).catch(function (result) {
                if (result.status == 400){
                    var msg = [];
                    for (var key in result.data){
                        msg.push(key+"： " + result.data[key]);
                    }
                    $rootScope.addAlert('danger', '添加商品失败：'+ msg.join('; '));
                }
                else{
                    $rootScope.addAlert('danger', '添加商品失败，状态码：' + result.status);
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
});