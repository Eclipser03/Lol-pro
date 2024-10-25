from calendar import c
from django.shortcuts import render
from django.views.generic import TemplateView
from store.forms import BoostOrderForms

# Create your views here.

class StoreView(TemplateView):
    template_name = 'store/store.html'

class StoreEloBoostView(TemplateView):
    template_name = 'store/store_elo_boost.html'


class StoreEloBoostChoiceView(TemplateView):
    template_name = 'store/store_elo_boost_choice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_form'] = BoostOrderForms()
        return context


class PlacementMatchesView(TemplateView):
    template_name = 'store/placement_matches.html'
