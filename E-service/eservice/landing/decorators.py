from django.http import HttpResponseForbidden

def solo_rol_empresa(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'empresa':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return _wrapped_view
