from django.views.generic import TemplateView as BaseTemplateView


__all__ = ['TemplateView']


class TemplateView(BaseTemplateView):
    """ A view that adds extra context and renders the template. """

    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        if hasattr(self, "extra_context") and isinstance(self.extra_context, dict):
            context.update(self.extra_context)
        return context
