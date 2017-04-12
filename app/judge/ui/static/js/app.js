(function() {
    angular.module('judge', ['ngRoute'])

    .controller('baseCtrl', BaseCtrl)
    .controller('headerCtrl', HeaderCtrl)
    .controller('indexCtrl', IndexCtrl)
    .controller('tasklistCtrl', TaskListCtrl)
    .controller('taskeditCtrl', TaskEditCtrl)
    .controller('userpageCtrl', UserPageCtrl)


    // Configuring routes
    .config(['$locationProvider', '$routeProvider', '$httpProvider',
        function config($locationProvider, $routeProvider, $httpProvider) {
            $locationProvider.html5Mode(true);

            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

            $routeProvider

            .when('/', {
                templateUrl: 'static/partials/index.html',
                controller: 'indexCtrl'
            })

            .when('/tasks', {
                templateUrl: 'static/partials/tasklist.html',
                controller: 'tasklistCtrl'
            })

            .when('/tasks/new', {
                templateUrl: 'static/partials/edittask.html',
                controller: 'taskeditCtrl'
            })

            .when('/user/:username', {
                templateUrl: 'static/partials/userpage.html',
                controller: 'userpageCtrl'
            })

            .when('/auth/logout', {
                redirectTo: function() {
                    window.location = '/auth/logout';
                }
            })
        }
    ]);
})();
