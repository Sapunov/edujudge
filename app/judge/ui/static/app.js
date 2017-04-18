;function BaseCtrl($scope, $timeout, $http) {

    $scope.judge_version = judge.version;

    $scope.status_message = '';
    $scope.solved_statuses = {
        '-1': 'hide',
        '0': 'glyphicon glyphicon-remove red',
        '1': 'glyphicon glyphicon-ok green',
    }

    $scope.say = function(text) {
        $scope.status_message = text;

        $timeout(function() {
            $scope.status_message = '';
        }, 3000);
    }

    $scope.say_error = function(text) {
        $scope.status_message = 'Произошла ошибка: ' + text;

        $timeout(function() {
            $scope.status_message = '';
        }, 30 * 1000);
    }

    $scope.get_from_queue = function(qid, callback) {
        $http.get(judge.api + '/queue/' + qid)
        .then(function(response) {
            callback(response);
        });
    }
}

function HeaderCtrl($scope, $timeout) {

    if ( judge.user !== undefined ) {
        $scope.user = judge.user;
        $scope.name = judge.user.first_name + ' ' + judge.user.last_name;
    }
}

function IndexCtrl($scope, $http) {

}

function TaskListCtrl($scope, $http) {

    $scope.tasks = [];

    function loadTasks() {
        $http.get(judge.api + '/tasks')
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.tasks = response.data;
            }
        });
    }

    loadTasks();
}

function TaskEditCtrl($scope, $http) {

    $scope.numOfTests = 1;
    $scope.task = {};
    $scope.task.timelimit = 1;
    $scope.task.tests = [];
    $scope.task.examples = [];

    $scope.getArray = function(num) {
        return new Array(num);
    }

    $scope.saveTask = function() {
        $http.post(judge.api + '/tasks', $scope.task)
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.say('Задание сохранено');
            } else {
                $scope.say_error(response.data);
            }
        });
    }
}


function TaskCtrl($scope, $http, $routeParams, $interval) {

    $scope.taskId = $routeParams.taskId;
    $scope.task = null;
    $scope.solutions = null;
    $scope.codeMirror = {
        lineNumbers: true,
        mode: 'python',
        readOnly: false
    }
    $scope.sent = false;
    $scope.intval = null;
    $scope.result = null;

    $scope.checkTask = function() {

        toogle_editing();

        $http.post(judge.api + '/tasks/' + $scope.taskId + '/check', {
            source: $scope.source
        }).then(function(response) {
            if ( response.status === 200 ) {
                interval_check(response.data.qid);
                $scope.say('Решение отправлено на проверку');
            }
        });
    }

    function interval_check(qid) {

        $scope.intval = $interval(function() {
            $scope.get_from_queue(qid, function(response) {
                if ( response.data.finished ) {
                    let msg = (response.data.result.error === 0) ? 'Все правильно!' : 'Есть ошибки :=(';

                    $interval.cancel($scope.intval);
                    $scope.say('Задание ' + response.data.result.task_id + ' проверено. ' + msg);

                    $scope.result = response.data.result;

                    load_solutions();
                    toogle_editing();
                }
            });
        }, 1000);
    }

    function toogle_editing() {

        if ( $scope.sent ) {
            $scope.sent = false;
            $scope.codeMirror.readOnly = false;
        } else {
            $scope.sent = true;
            $scope.codeMirror.readOnly = true;
        }
    }

    function init() {

        if ( $scope.task === null ) {
            $http.get(judge.api + '/tasks/' + $scope.taskId)
            .then(function(response) {
                if ( response.status === 200 ) {
                    $scope.task = response.data;

                } else if ( response.status === 204 ) {
                    $scope.say_error('Задание не найдено');
                } else {
                    $scope.say_error(response.data);
                }
            });

            load_solutions();
        }
    }

    function load_solutions() {
        $http.get(judge.api + '/solutions?task_id=' + $scope.taskId)
        .then(function(response) {
            if ( response.data.length > 0 ) {
                $scope.solutions = response.data;
            }
        });
    }

    init();
}


function UserPageCtrl($scope, $http, $routeParams) {

    $scope.user = null;
    $scope.solved_statuses = {
        '-1': 'progress-bar-item pull-left',
        '0': 'progress-bar-item pull-left red-bg',
        '1': 'progress-bar-item pull-left green-bg',
    }

    $scope.tasks = [];

    function loadTasks(username) {
        $http.get(judge.api + '/tasks?user=' + username)
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.tasks = response.data;
            }
        });
    }

    function loadUser(username) {
        $http.get(judge.api + '/users/' + username)
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.user = response.data;
            }
        });
    }

    loadUser($routeParams.username);
    loadTasks($routeParams.username);
}
;(function() {
    angular.module('judge', ['ngRoute', 'ui.bootstrap', 'ui.codemirror'])

    .controller('baseCtrl', BaseCtrl)
    .controller('headerCtrl', HeaderCtrl)
    .controller('indexCtrl', IndexCtrl)
    .controller('tasklistCtrl', TaskListCtrl)
    .controller('taskeditCtrl', TaskEditCtrl)
    .controller('taskCtrl', TaskCtrl)
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

            .when('/tasks/new', {
                templateUrl: 'static/partials/edittask.html',
                controller: 'taskeditCtrl'
            })

            .when('/tasks/:taskId', {
                templateUrl: 'static/partials/task.html',
                controller: 'taskCtrl'
            })

            .when('/tasks', {
                templateUrl: 'static/partials/tasklist.html',
                controller: 'tasklistCtrl'
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
;angular.module('judge')

.directive('ngAutofocus', function($timeout) {
    return {
        link: function (scope, element, attrs) {
            scope.$watch(attrs.ngAutofocus, function(val) {
                if (angular.isDefined(val) && val) {
                    $timeout(function() { element[0].focus(); });
                }
            }, true);
        }
    };
})

.directive("mathjaxBind", function() {
    return {
        restrict: "A",
        controller: ["$scope", "$element", "$attrs", function($scope, $element, $attrs) {
            $scope.$watch($attrs.mathjaxBind, function(value) {
                $element.text(value == undefined ? "" : value);
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, $element[0]]);
            });
        }]
    };
});
