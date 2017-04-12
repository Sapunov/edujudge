function BaseCtrl($scope, $timeout) {
    $scope.status_message = '';

    $scope.say = function(text) {
        $scope.status_message = text;

        $timeout(function() {
            $scope.status_message = '';
        }, 3000);
    }

}

function HeaderCtrl($scope) {
    $scope.parts = {
        '/': '/',
        '/questions': 'questions',
        '/stats': 'stats',
        '/questions/add': 'questions'
    };
    $scope.active = null;

    $scope.$on('$routeChangeSuccess', function(event, current) {
        for (var route in $scope.parts) {
            if (current.$$route.regexp.test(route)) {
                $scope.active = $scope.parts[route];
            }
        }
    });

    $scope.isActive = function(name) {
        return $scope.active === name ? "active" : "";
    };
}

function IndexCtrl($scope, $http) {

}

function TasklistCtrl($scope, $http) {

}

function TaskeditCtrl($scope, $http) {

}

function UserpageCtrl($scope, $http) {

}
