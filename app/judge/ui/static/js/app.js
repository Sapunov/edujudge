(function() {
    angular.module('judge', ['ngRoute'])

    .controller('baseCtrl', BaseCtrl)
    .controller('headerCtrl', HeaderCtrl)
    .controller('indexCtrl', IndexCtrl)
    .controller('tasklistCtrl', TasklistCtrl)
    .controller('taskeditCtrl', TaskeditCtrl)
    .controller('userpageCtrl', UserpageCtrl)


    // Configuring routes
    .config(['$locationProvider', '$routeProvider', '$httpProvider',
        function config($locationProvider, $routeProvider, $httpProvider) {
            $locationProvider.html5Mode(true);

            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

            $routeProvider

            .when('/', {
                templateUrl: 'static/partials/test.html',
                controller: 'testCtrl'
            })

            .when('/questions/add', {
                templateUrl: 'static/partials/questions-add.html',
                controller: 'questionsAddCtrl'
            })

            .when('/questions', {
                templateUrl: 'static/partials/questions.html',
                controller: 'questionsCtrl'
            })

            .when('/stats', {
                templateUrl: 'static/partials/stats.html',
                controller: 'statsCtrl'
            })

            .otherwise({
                redirectTo: '/'
            });
        }
    ]);
})();
