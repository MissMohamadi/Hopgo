from django.views.generic import TemplateView

class DogWalker_view(TemplateView):
    template_name = 'dog_walker/pet_walker.html'
