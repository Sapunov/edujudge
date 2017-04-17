angular.module('judge')

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
