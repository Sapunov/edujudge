function BaseCtrl($scope, $timeout, $http, $interval) {

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
        }, 5 * 1000);
    }

    $scope.say_error = function(text) {

        text = text || 'Произошла ошибка';

        $scope.status_message = text;

        $timeout(function() {
            $scope.status_message = '';
        }, 10 * 1000);
    }

    $scope.errorHandler = function(response) {

        switch ( response.status ) {
            case 404:
                $scope.say_error('Ресурс не найден');
                break;
            case 403:
                $scope.say_error('У вас нет доступа к запрашиваемому ресурсу');
                break;
            default:
                $scope.say_error();
                break;
        }
    }

    function instant_messages() {

        if ( judge.user === undefined ) return;

        $interval(function() {
            $http.get(judge.api + '/im')
            .then(function(response) {
                if ( response.status === 200 ) {
                    let msgs = response.data.messages,
                        data;

                    for ( let i = 0; i < msgs.length; ++i ) {
                        if ( msgs[i].alert_msg !== null ) {
                            $scope.say(msgs[i].alert_msg);
                        }

                        try {
                            data = JSON.parse(msgs[i].payload);
                            $scope.$broadcast('im', {
                                type: msgs[i].msg_type,
                                data: data
                            });
                        } catch (e) {
                            console.log(e);
                        }
                    }
                }
            }, function(response) {});
        }, 2000);
    }

    instant_messages();
}


function HeaderCtrl($scope, $timeout) {

    if ( judge.user !== undefined ) {
        $scope.user = judge.user;
        $scope.name = judge.user.first_name + ' ' + judge.user.last_name;
    }
}


function IndexCtrl($scope, $http) {}


function TaskListCtrl($scope, $http) {

    $scope.tasks = [];

    function loadTasks() {
        $http.get(judge.api + '/tasks')
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.tasks = response.data;
            }
        }, $scope.errorHandler);
    }

    loadTasks();
}


function TaskEditCtrl($scope, $http) {

    $scope.numOfTests = 1;
    $scope.numOfExamples = 1;

    $scope.task = {
        timelimit: 1,
        tests: [],
        examples: [],
        test_generator_path: null
    };

    $scope.codeTab = false;
    $scope.codeMirror = {
        lineNumbers: true,
        mode: 'python',
        readOnly: false
    }
    $scope.sent = false;

    $scope.has_error_codegen = false;
    $scope.error_msg = '';

    $scope.source = generator_skeleton;

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
        }, $scope.errorHandler);
    }

    $scope.deleteExample = function(index) {

        if ( $scope.numOfExamples > 1 ) {
            for ( let i = index; i <= $scope.numOfExamples; ++i ) {
                $scope.task.examples[i] = $scope.task.examples[i + 1];
            }

            $scope.task.examples.splice($scope.numOfExamples - 1, $scope.numOfExamples - 1);
            $scope.numOfExamples--;
        } else {
            $scope.say('Нельзя удалять все примеры');
        }
    }

    $scope.deleteTest = function(index) {

        if ( $scope.numOfTests > 1 ) {
            for ( let i = index; i <= $scope.numOfTests; ++i ) {
                $scope.task.tests[i] = $scope.task.tests[i + 1];
            }

            $scope.task.tests.splice($scope.numOfTests - 1, $scope.numOfTests - 1);
            $scope.numOfTests--;
        } else {
            $scope.say('Нельзя удалять все тесты');
        }
    }

    $scope.generateTests = function(event) {

        event.preventDefault();
        event.stopPropagation();

        toogle_editing();

        $http.post(judge.api + '/tests/generate', { 'source': $scope.source })
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.say('Код отправлен на обработку');
            }
        }, $scope.errorHandler);
    }

    $scope.$on('im', function(event, data) {

        switch ( data.type ) {
            case 'error_testgenerating':
                $scope.has_error_codegen = true;
                $scope.error_msg = data.data;
                toogle_editing();
                break;
            case 'ok_testgenerating':
                $scope.has_error_codegen = false;
                toogle_editing();

                $scope.task.test_generator_path = data.data.test_generator;

                for ( let i = 0; i < data.data.tests.length; ++i ) {
                    $scope.task.tests.push({
                        text: data.data.tests[i].text,
                        answer: data.data.tests[i].answer
                    })
                }

                $scope.numOfTests = $scope.task.tests.length;

                $scope.codeTab = false;
        }
    });

    function toogle_editing() {

        if ( $scope.sent ) {
            $scope.sent = false;
            $scope.codeMirror.readOnly = false;
        } else {
            $scope.sent = true;
            $scope.codeMirror.readOnly = true;
        }
    }
}


function TaskCtrl($scope, $http, $routeParams, $location) {

    $scope.taskId = $routeParams.taskId;
    $scope.username = $location.search().username || judge.user.username;
    $scope.alienPage = false;

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
                $scope.say('Решение отправлено на проверку');
            }
        }, $scope.errorHandler);
    }

    $scope.$on('im', function(event, data) {

        switch ( data.type ) {
            case 'test_complete':
                test_complete(data.data);
                break;
        }

    });


    function test_complete(data) {

        $scope.result = data;

        load_solutions();
        toogle_editing();
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

        if ( $scope.username !== undefined && $scope.username !== judge.user.username ) {
            $scope.alienPage = true;
        }

        $http.get(judge.api + '/tasks/' + $scope.taskId)
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.task = response.data;
            }
        }, $scope.errorHandler);

        load_solutions();
    }

    function load_solutions() {

        let url = `/solutions?task_id=${$scope.taskId}&username=${$scope.username}`;

        $http.get(judge.api + url).then(function(response) {
            if ( response.data.length > 0 ) {
                $scope.solutions = response.data;
            }
        }, $scope.errorHandler);
    }

    init();
}


function TaskCommentsCtrl($scope, $http) {

    $scope.comments = null;
    $scope.currentUser = judge.user.username;

    $scope.saveComment = function() {

        $http.post(judge.api + '/comments', {
            'text': $scope.comment,
            'task_id': $scope.taskId,
            'username': $scope.username
        }).then(function(response) {
            if ( response.status === 200 ) {
                prependComment(response.data);
                $scope.comment = null;
                $scope.commentForm.$setPristine();
            }
        }, $scope.errorHandler);
    }

    $scope.deleteComment = function(commentId) {

        $http.delete(judge.api + '/comments/' + commentId)
        .then(function(response) {
            if ( response.status === 204 ) {
                for ( let i = 0; i < $scope.comments.length; ++i ) {
                    if ( $scope.comments[i].id === commentId ) {
                        $scope.comments[i].deleted = true;
                    }
                }
            }
        }, $scope.errorHandler);
    }

    $scope.$on('im', function(event, data) {

        switch ( data.type ) {
            case 'new_comment':
                prependComment(data.data);
                break;
        }
    });

    function prependComment(comment) {

        if ( $scope.comments === null ) {
            $scope.comments = [comment];
        } else {
            $scope.comments.unshift(comment);
        }
    }

    function loadComments() {

        let url = `/comments?task_id=${$scope.taskId}&username=${$scope.username}`;

        $http.get(judge.api + url)
        .then(function(response) {
            if ( response.status === 200 && response.data.length > 0 ) {
                $scope.comments = response.data;
            }
        }, $scope.errorHandler);
    }

    loadComments();
}


function UserPageCtrl($scope, $http, $routeParams) {

    $scope.user = null;
    $scope.alienPage = false;
    $scope.solved_statuses = {
        '-1': 'progress-bar-item pull-left',
        '0': 'progress-bar-item pull-left red-bg',
        '1': 'progress-bar-item pull-left green-bg',
    }

    $scope.tasks = [];
    $scope.students = null;

    function loadTasks(username) {

        $http.get(judge.api + '/tasks?user=' + username)
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.tasks = response.data;
            }
        }, $scope.errorHandler);
    }

    function loadUser(username) {

        $http.get(judge.api + '/users/' + username)
        .then(function(response) {
            if ( response.status === 200 ) {
                $scope.user = response.data;
            }
        }, $scope.errorHandler);
    }

    function loadStudents() {

        $http.get(judge.api + '/users')
        .then(function(response) {
            if ( response.status === 200 && response.data.length > 0 ) {
                $scope.students = response.data;
            }
        }, $scope.errorHandler);
    }

    loadUser($routeParams.username);
    loadTasks($routeParams.username);

    if ( $routeParams.username == judge.user.username ) {
        loadStudents();
    } else {
        $scope.alienPage = true;
    }
}
