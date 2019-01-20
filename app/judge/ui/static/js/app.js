(function() {
    angular.module('judge', ['ngSanitize', 'ngRoute', 'ui.bootstrap', 'ui.codemirror'])

    .controller('baseCtrl', BaseCtrl)
    .controller('headerCtrl', HeaderCtrl)
    .controller('indexCtrl', IndexCtrl)
    .controller('tasklistCtrl', TaskListCtrl)
    .controller('taskeditCtrl', TaskEditCtrl)
    .controller('taskCtrl', TaskCtrl)
    .controller('userpageCtrl', UserPageCtrl)
    .controller('taskCommentsCtrl', TaskCommentsCtrl)
    .controller('studentsCtrl', StudentsCtrl)
    .controller('dashboardCtrl', DashboardCtrl)

    // Configuring routes
    .config(['$locationProvider', '$routeProvider', '$httpProvider',
        function config($locationProvider, $routeProvider, $httpProvider) {
            $locationProvider.html5Mode(true);

            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

            $routeProvider

            .when('/', {
                templateUrl: 'static/partials/index.html?v=' + judge.version,
                controller: 'indexCtrl'
            })

            .when('/tasks/new', {
                templateUrl: 'static/partials/edittask.html?v=' + judge.version,
                controller: 'taskeditCtrl'
            })

            .when('/tasks/:taskId', {
                templateUrl: 'static/partials/task.html?v=' + judge.version,
                controller: 'taskCtrl'
            })

            .when('/tasks', {
                templateUrl: 'static/partials/tasklist.html?v=' + judge.version,
                controller: 'tasklistCtrl'
            })

            .when('/users/:username', {
                templateUrl: 'static/partials/userpage.html?v=' + judge.version,
                controller: 'userpageCtrl'
            })

            .when('/students', {
                templateUrl: 'static/partials/students.html?v=' + judge.version,
                controller: 'studentsCtrl'
            })

            .when('/dashboard', {
                templateUrl: 'static/partials/dashboard.html?v=' + judge.version,
                controller: 'dashboardCtrl'
            })

            .when('/auth/logout', {
                redirectTo: function() {
                    window.location = '/auth/logout';
                }
            })
        }
    ]);
})();
