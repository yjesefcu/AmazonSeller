/**
 * Created by liucaiyun on 2017/5/22.
 */

app.controller('ProductCtrl', function($scope, $http) {
    $scope.formData = {};
    $scope.createProduct = function (form) {

    }
});


app.controller("ProductEditCtrl", function ($scope, $http, serviceFactory) {
    $scope.formData = {};
    $scope.submitForm = function () {
        var url = serviceFactory.createProduct();
        $http.jsonp(url, $scope.formData, {
            header: {
                'Content-Type':'application/x-www-form-urlencoded',
                'Access-Control-Allow-Origin': '*'
            }
            // header: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        // $http({
        //         url: serviceFactory.getAllProducts(),
        //         headers: {
        //             'Access-Control-Allow-Origin': '*'
        //         },
        // });
    }
});