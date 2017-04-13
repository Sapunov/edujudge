function BaseCtrl($scope, $timeout) {
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


function TaskCtrl($scope, $http, $routeParams) {

    $scope.taskId = $routeParams.taskId;
    $scope.task = null;
    $scope.codeMirror = {
        lineNumbers: true,
        mode: 'python',
        readOnly: false
    }
    $scope.sent = false;

    $scope.checkTask = function() {

        disable_editing();

        $http.post(judge.api + '/tasks/' + $scope.taskId + '/check', {
            source: $scope.source
        }).then(function(response) {
            if ( response.status === 200 ) {
                console.log(response.data);
                $scope.say('Решение отправлено на проверку');
            }
        });
    }

    function disable_editing() {
        $scope.sent = true;
        $scope.codeMirror.readOnly = true;
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
