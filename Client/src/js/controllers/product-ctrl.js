/**
 * Created by liucaiyun on 2017/5/22.
 */

app.controller('ProductCtrl', function($scope, $http) {
    $scope.formData = {};
    $scope.createProduct = function (form) {

    }
});


app.controller("ProductEditCtrl", function ($scope, $http, $sce, serviceFactory) {
    $scope.formData = {'MarketplaceId': 'ATVPDKIKX0DER'};
    $sce.trustAsUrl('http://192.168.1.3');
    $sce.trustAsResourceUrl('http://192.168.1.3');
    $scope.submitForm = function () {
        var url = serviceFactory.createProduct();
        $http.post(url, $scope.formData
            /*{
            header: {
                'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'Access-Control-Allow-Origin': '*'
            }*/
        );
    }
});