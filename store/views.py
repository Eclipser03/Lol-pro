import json

from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from store.forms import BoostOrderForms
from store.models import Coupon


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

    def post(self, request, *args, **kwargs):
        print(request.POST)
        form = BoostOrderForms(request.POST)
        if form.is_valid():
            form.save()
        return redirect('store:store_elo_boost_choice')


class PlacementMatchesView(TemplateView):
    template_name = 'store/placement_matches.html'


def check_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon_code = data.get('coupon')

        coupon = Coupon.objects.filter(name=coupon_code)

        if not coupon.exists():
            response_data = {'success': False, 'message': 'Купон не найден'}
            return JsonResponse(response_data)

        coupon = coupon.last()


        if coupon.is_active and coupon.count > 0 and coupon.end_date > timezone.now():
            response_data = {'success': True, 'discount': coupon.sale}

        else:
            response_data = {'success': False, 'message': 'Купон недействителен или закончился'}
        return JsonResponse(response_data)
