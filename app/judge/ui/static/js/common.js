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

function humanizeLastActive(lastActiveSeconds, lastActive) {
  if (lastActiveSeconds < 60) {
      return 'только что';
  }

  const minutes = Math.floor(lastActiveSeconds / 60);

  if (minutes <= 60) {
      return `${minutes} минут назад`
  }

  const hours = Math.floor(lastActiveSeconds / (60 * 60));

  if (hours <= 24) {
      return `${hours} часов назад`;
  }

  const years = Math.floor(lastActiveSeconds / (60 * 60 * 24 * 365));

  if (years <= 10) {
      return lastActive;
  }

  return 'никогда';
}
