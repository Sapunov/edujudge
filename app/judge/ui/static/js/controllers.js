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
    $scope.dropdown = false;

    $scope.toggleDropdown = function() {
        $scope.dropdown = !$scope.dropdown;
    }
}

function IndexCtrl($scope, $http) {

}

function TaskListCtrl($scope, $http) {

}

function TaskEditCtrl($scope, $http) {

}

function UserPageCtrl($scope, $http) {

}
