from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class StoreView(TemplateView):
    template_name = 'store/store.html'

class StoreEloBoostView(TemplateView):
    template_name = 'store/store_elo_boost.html'


class StoreEloBoostChoiceView(TemplateView):
    template_name = 'store/store_elo_boost_choice.html'


class PlacementMatchesView(TemplateView):
    template_name = 'store/placement_matches.html'
