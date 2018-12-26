/**
 * Created by milan on 24/03/17.
 */

doa.controller('CancerTypesCtrl', function($scope, $http, apiService) {
    //Data from server
    function refresh() {
        apiService.withCancerTypesUrl(function (url) {
            apiService.get(url, function (data) {
                extractCancerTypes(data.cancer_types)
            })
        })
    }


    // Get the cancer types from a list of links (in format {href:url})
    function extractCancerTypes(linkList) {
        $scope.cancerTypes = apiService.extractObjectsFromList(linkList)
    }

    refresh()


    //Input data
    $scope.inputNamesPerNomenclature = {}

    $scope.addInputName = function () {
        nomenclatureName = $scope.inputNomenclatureName

        if(!(nomenclatureName in $scope.inputNamesPerNomenclature)){
            $scope.inputNamesPerNomenclature[nomenclatureName] = []
        }

        $scope.inputNamesPerNomenclature[nomenclatureName].push($scope.inputName)
    }

    $scope.createCancerType = function () {
        newCancerType = {
            "names_per_nomenclature" : $scope.inputNamesPerNomenclature
        }

        $scope.inputNamesPerNomenclature = {}

        apiService.withCancerTypesUrl(function (url) {
            $http.post(url, newCancerType).then(function successCallback(response) {
                alert("Submitted successfully");
            }, function errorCallback(response) {
                alert("Error when submitting: " + response.statusText + '\n' +
                        response.data);
                console.log(response)
            });
        })
        refresh()
    }
});