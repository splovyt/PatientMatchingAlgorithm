/**
 * Created by milan on 24/03/17.
 */


doa.controller('HomeCtrl', function($scope, $location, $http, $window, apiService) {
    apiService.withPatientsUrl(function (url) {
        $scope.test = url;
    })

    $scope.goToPatients = function () {
        $window.location.href = "#/patients/"
    }

    $scope.goToCancerTypes = function () {
        $window.location.href = "#/cancer-types/"
    }
});