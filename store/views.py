import json
import time
import uuid

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import TemplateView

from store.forms import BoostOrderForms, QualificationForm, RPorderForm, SkinsOrderForm
from store.models import Coupon
from user.tasks import send_email_task


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
            messages.success(request, 'Покупка совершена успешно')
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
        print('post', request.POST)
        form = QualificationForm(request.POST, request=request)
        # form.request = self.request
        if form.is_valid():
            form.save()
            messages.success(request, 'Покупка совершена успешно')
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
            return JsonResponse({'success': False, 'message': 'Купон не найден'})

        coupon = coupon.last()

        user_coupons = request.user.qualification_orders.all().values('coupon_code')
        if any(coupon.id == next(iter(i.values())) for i in user_coupons):
            return JsonResponse({'success': False, 'message': 'Купон уже был использован'})

        user_coupons1 = request.user.boost_orders.all().values('coupon_code')
        if any(coupon.id == next(iter(i.values())) for i in user_coupons1):
            return JsonResponse({'success': False, 'message': 'Купон уже был использован'})

        if coupon.is_active and coupon.count > 0 and coupon.end_date > timezone.now():
            response_data = {
                'success': True,
                'discount': coupon.sale,
                'message': 'Купон успешно применен',
            }

        else:
            response_data = {'success': False, 'message': 'Купон недействителен или закончился'}
        return JsonResponse(response_data)


class StoreSkinsView(TemplateView):
    template_name = 'store/store_skins.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skinorder_form'] = SkinsOrderForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')

        form = SkinsOrderForm(request.POST)
        print('Принт реквест', request.POST)
        form.request = self.request
        mail_subject = 'Покупка с сайта Lol-Pay'
        key = str(uuid.uuid4())

        purchase_type = 'образа' if 'skin_name' in request.POST else 'персонажа'
        item_name = request.POST.get('skin_name') or request.POST.get('char_name')

        html_message = render_to_string(
        'store/store_skins_email.html',
        {
            'mail_subject': mail_subject,
            'username': request.user.username,
            'purchase_type': purchase_type,
            'item_name': item_name,
            'key': key
        }
    )

        if form.is_valid():
            form.save()
            send_email_task.delay(mail_subject, html_message, [self.request.user.email])
            messages.success(request, 'Покупка совершена, письмо отправлено на почту')
        else:
            # Отобразим ошибки формы, чтобы увидеть причину неудачи
            print(form.errors)
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'skinorder_form': form})
        return redirect('store:store_skins')

class StoreRPView(TemplateView):
    template_name = 'store/store_rp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rp_form'] = RPorderForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')

        form = RPorderForm(request.POST)
        print('реквестПОСТ---',request.POST)
        print('реквест---',self.request)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Покупка совершена успешно')
        else:
            # Отобразим ошибки формы, чтобы увидеть причину неудачи
            print(form.errors)
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'rp_form': form})
        return redirect('store:store_rp')



