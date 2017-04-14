function BaseCtrl($scope, $timeout, $http) {
    $scope.status_message = '';

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

function HeaderCtrl($scope, $timeout) { }

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
    $scope.codeMirror = {
        lineNumbers: true,
        mode: 'python',
        readOnly: false
    }
    $scope.sent = false;
    $scope.intval = null;

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
                    console.log(response.data.result);
                    $interval.cancel($scope.intval);
                    let msg = (response.data.result.error_code === 0) ? 'Все правильно!' : 'Есть ошибки :=(';
                    $scope.say('Задание ' + response.data.result.task_id + ' проверено. ' + msg);
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
        }
    }

    init();
}


function UserPageCtrl($scope, $http) {

}
