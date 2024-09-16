from django.shortcuts import redirect


class RedirectAuthUser:
    auth_redirect_link = '/admin/'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.auth_redirect_link)  # Перенаправляем авторизованного пользователя
        return super().dispatch(request, *args, **kwargs)
