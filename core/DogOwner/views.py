from django.views.generic import TemplateView

class DogOwner_view(TemplateView):
    template_name = 'dog_owner/pet_owner.html'
