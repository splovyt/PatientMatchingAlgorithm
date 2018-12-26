/**
 * Created by milan on 24/03/17.
 */


doa.controller('PatientsCtrl', function($scope, $q, apiService) {

    $scope.firstPage = function() {
        $scope.cancerSubtypesListReadyDeferred = $q.defer();
        getCancerSubtypesList();
        $scope.cancerSubtypesListReadyDeferred.promise.then(
            function(results) {
                apiService.withPatientsUrl(function (url) {
                    loadPage(url)
                })
            }, function (errors) {
                alert("error while fetching cancer subtypes")
            });
    };

    $scope.firstPage();
    $scope.patientsLoading = true;
    $scope.addingPatient = false;
    $scope.inputPatient = {};
    $scope.viewingPatient = false;
    $scope.showMut = false;
    $scope.showMet = false;
    $scope.showExp = false;
    $scope.showCnv = false;

    $scope.search = function () {
        apiService.withPatientsUrl(function (url) {
            var searchUrl = url + "&query=" + $scope.query;
            $scope.query = ""
            loadPage(searchUrl)
        })
    };

    $scope.nextPage = function() {
        loadPage($scope.nextPageUrl)
    };

    $scope.previousPage = function() {
        loadPage($scope.previousPageUrl)
    };

    $scope.addPatient = function () {
        $scope.addingPatient = true;
    };

    $scope.submitPatient = function () {
        apiService.withPatientsUrl(function (url) {
            apiService.post(
                url,
                $scope.inputPatient,
                function (result) {
                    alert("Patient submitted succesfully. Patient id is " + result.id);
                    $scope.finishAddingPatient();
                }
            );
        });
    };

    $scope.finishAddingPatient = function () {
        $scope.inputPatient={};
        $scope.addingPatient = false;
    };

    $scope.viewPatient = function (patient) {
        $scope.selectedPatient = patient;
        addAberrations(patient)
        $scope.viewingPatient = true
    }
    
    $scope.hideSelectedPatient = function () {
        $scope.viewingPatient = false
        $scope.selectedPatient.mutationVafs = null
    };

    function loadPage(url) {
        $scope.patientsLoading = true
        apiService.get(url, function (data) {
            extractPatients(data.patients)
            $scope.nextPageUrl = data.next_page.href
            $scope.previousPageUrl = data.previous_page.href
        })
    }

    // Get the patients from a list of links (in format {href:url})
    function extractPatients(linkList) {
        $scope.patients = []
        apiService.extractObjectsFromListWithCallback(linkList, addCancerInfo)
            .then(function (results) {
                $scope.patientsLoading = false
            })
    }

    function addCancerInfo(patients){
        for(var i=0;i<patients.length;i++) {
            var patient = patients[i]
            $scope.patients.push(patient)
            if('cancer_subtype' in patient) {
                patient.cancerSubtypeName = $scope.cancerSubtypesPerUrl[patient.cancer_subtype.href];
            }
            else {
                patient.cancerSubtypeName = "unknown"
            }
        }
    }

    function addAberrations(patient){
        function userFriendlyAberrationMap(aberrationMap) {
            if(angular.equals(aberrationMap, {})){
                return {'empty':''};
            } else {
                return aberrationMap
            }
        }

        patient.mutationVafs = {'loading':'...'};
        patient.expressions = {'loading':'...'};
        patient.methylations = {'loading':'...'};
        patient.cnvs = {'loading':'...'};
        apiService.get(patient.gene_aberrations.href, function (data) {
            patient.mutationVafs = userFriendlyAberrationMap(data.mutated_gene_vafs);
            patient.expressions = userFriendlyAberrationMap(data.expressions);
            patient.methylations = userFriendlyAberrationMap(data.methylations);
            patient.cnvs = userFriendlyAberrationMap(data.cnvs);
        });
    }

    function getCancerSubtypesList(){
        $scope.cancerSubtypeUrls = {};
        $scope.cancerSubtypesPerUrl = {};
        apiService.withCancerTypesUrl(function (url) {
            apiService.get(url, function (data) {
                apiService.extractObjectsFromListWithCallback(data.cancer_types, getCancerSubtypesListFromTypesList)
            })
        })
    }

    function getCancerSubtypesListFromTypesList(cancerTypes) {
        var calls = []
        for(var i=0;i<cancerTypes.length;i++) {
            var cancerType = cancerTypes[i]
            calls.push(fillCancerSubtypesListForType(cancerType))
        }

        $q.all(calls).then(
            function (results) {
                $scope.cancerSubtypesListReadyDeferred.resolve(results)
            }, function (errors) {
                $scope.cancerSubtypesListReadyDeferred.reject(errors)
            }
        )
    }
    
    function fillCancerSubtypesListForType(cancerType) {
        var cancerTypeName = cancerType.names_per_nomenclature.default[0]
        var calls = []
        var deferred = $q.defer()
        apiService.get(cancerType.subtypes.href, function (subtypesData) {
            calls.push(apiService.extractObjectsFromListWithCallback(subtypesData.cancer_subtypes, function (subtypes) {
                for(var i=0;i<subtypes.length;i++) {
                    var subtype = subtypes[i]
                    var subtypeName = subtype.names_per_nomenclature.default
                    var completeName = cancerTypeName + ': ' + subtypeName
                    $scope.cancerSubtypeUrls[completeName] = subtype.self.href
                    $scope.cancerSubtypesPerUrl[subtype.self.href] = completeName
                }
            }))
        }).then(function (results) {
            $q.all(calls).then(
                function (results) {
                    deferred.resolve(results)
                }, function (errors) {
                    deferred.reject(errors)
                }
            )
        }, function (errors) {
            deferred.reject(errors)
        })

        return deferred.promise
    }

});