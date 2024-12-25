from django.shortcuts import redirect


class RedirectAuthUser:
    auth_redirect_link = '/'
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.auth_redirect_link)
        return super().dispatch(request, *args, **kwargs)
