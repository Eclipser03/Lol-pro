import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from store.forms import BoostOrderForms, QualificationForm
from store.models import Coupon


# Create your views here.


class StoreView(TemplateView):
    template_name = 'store/store.html'


class StoreEloBoostView(TemplateView):
    template_name = 'store/store_elo_boost.html'


class StoreEloBoostChoiceView(TemplateView):
    template_name = 'store/store_elo_boost_choice.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_form'] = BoostOrderForms()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')
        # print('post', request.POST)
        form = BoostOrderForms(request.POST)
        form.request = self.request
        if form.is_valid():
            form.save()
        else:
            # Отобразим ошибки формы, чтобы увидеть причину неудачи
            print(form.errors)
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'store_form': form})
        return redirect('store:store_elo_boost_choice')


class PlacementMatchesView(TemplateView):
    template_name = 'store/placement_matches.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qualification_form'] = QualificationForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')
        # print('post', request.POST)
        form = QualificationForm(request.POST)
        form.request = self.request
        if form.is_valid():
            form.save()
        else:
            # Отобразим ошибки формы, чтобы увидеть причину неудачи
            print(form.errors)
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'qualification_form': form})
        return redirect('store:placement_matches')


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


class StoreSkinsView(TemplateView):
    template_name = 'store/store_skins.html'
