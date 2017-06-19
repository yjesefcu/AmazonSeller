/**
 * Created by liucaiyun on 2017/6/19.
 */
app.directive( "fileModel", [ "$parse", function( $parse ){
    return {
        restrict: "A",
        link: function( scope, element, attrs ){
            var model = $parse( attrs.fileModel );
            var modelSetter = model.assign;

            element.bind( "change", function(){
                scope.$apply( function(){
                    modelSetter( scope, element[0].files[0] );
                    // console.log( scope );
                } )
            } )
        }
    }
}])
.service( "fileUpload", ["$http", '$rootScope', function( $http, $rootScope){
    this.uploadFileToUrl = function( file, uploadUrl, cb){
        var fd = new FormData();
        fd.append( "file", file );
        $http.post( uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: { "Content-Type": undefined }
        })
            .then(function(result){
                // blabla...
                cb && cb(result.data);
            })
            .catch( function(){
                // blabla...
                $rootScope.addAlert('error', '导入文件失败');
            })
    }
}])