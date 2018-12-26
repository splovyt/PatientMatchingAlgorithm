/**
 * Created by milan on 24/03/17.
 */

var doa = angular.module('doa', ['ngRoute']);

doa.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {

    $routeProvider
        .when('/', {
            templateUrl: "templates/home.html",
            controller:'HomeCtrl'
        })
        .when('/patients/', {
            templateUrl: "templates/patients.html",
            controller:'PatientsCtrl'
        })
        .when('/cancer-types/', {
            templateUrl: "templates/cancer-types.html",
            controller: 'CancerTypesCtrl'
        })
        .otherwise({
                template: "Not found."
            }
        );
}]);

doa.service('apiService', function ($http, $q) {
    var homeUrl = "http://localhost:8080/";

    var get = function (url, callback) { //The callback will get the data as argument

        return $http.get(url)
            .then(function (response) {
                response = response.data;
                callback(response)
            }, function (errors) {
                alert("An error occurred while requesting the data from the server.");
            });
    };

    var post = function (url, data, callback) { //The callback will get the data as argument

        return $http.post(url, data)
            .then(function (response) {
                response = response.data;
                callback(response)
            }, function (errors) {
                alert("An error occurred while sending data to the server.");
            });
    };

    // Get objects from a list of links (in format {href:url})
    var extractObjectsFromList = function(linkList) {
        var objects = []

        for(var i = 0; i < linkList.length; i++){
            get(linkList[i].href, function (object) {
                objects.push(object)
            })
        }

        return objects
    }

    // Get objects from a list of links (in format {href:url}) and execute a given function on them
    // Returns a promise
    var extractObjectsFromListWithCallback = function(linkList, callback) {
        var objects = []
        var calls = []

        for(var i = 0; i < linkList.length; i++){
            calls.push(get(linkList[i].href, function (object) {
                objects.push(object)
            }))
        }

        return $q.all(calls)
            .then(function(results){
                callback(objects)
            }, function(errors){
                callback({"error": "An error occurred while extracting objects from a list."})
            })
    }

    var withPatientsUrl = function (callback) {
        get(homeUrl, function (data) {
            callback(data.patients.first_page.href)
        })
    };

    var withCancerTypesUrl = function (callback) {
        get(homeUrl, function (data) {
            callback(data.cancer_types.href)
        })
    };

    return {
        get: get,
        post: post,
        withPatientsUrl: withPatientsUrl,
        withCancerTypesUrl: withCancerTypesUrl,
        extractObjectsFromList: extractObjectsFromList,
        extractObjectsFromListWithCallback: extractObjectsFromListWithCallback,
        homeUrl: homeUrl
    };
});