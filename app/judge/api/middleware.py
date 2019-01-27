from judge.api.models import Profile


class LastActivityMiddleware:

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # '/api/im' не считается, как активность пользователя
        if request.user.is_authenticated() and request.path != '/api/im':
            Profile.get_user_profile(request.user).mark_active()

        return response
