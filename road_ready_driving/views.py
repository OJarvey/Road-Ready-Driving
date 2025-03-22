from django.views.generic import TemplateView

class Custom404View(TemplateView):
    template_name = 'errors/404.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


def handler404(request, exception):
    view = Custom404View.as_view()
    return view(request)
