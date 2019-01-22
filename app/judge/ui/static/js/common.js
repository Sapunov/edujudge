const generator_skeleton = `# The function generate will be called as many times
# as specified in this variable
NUMBER_OF_TESTS = 0


def generate():
  """Test generator function
  Must return tuple with test and answer.
  """

  test = None
  answer = None

  # Your code here...

  return str(test), str(answer)`;

const checker_skeleton = `def check_test(test_input, test_output, user_output):
  """Checker function.
  """

  # Your code here...

  return False`;

serialize = function(obj) {
  var str = [];
  for (var p in obj)
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}
