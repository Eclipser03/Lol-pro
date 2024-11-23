import json
import uuid

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import TemplateView

from store.forms import (
    AccountObjectForm,
    # AccountsImageForm,
    BoostOrderForms,
    QualificationForm,
    RPorderForm,
    SkinsOrderForm,
)
from store.models import AccountObject, AccountsImage, ChatRoom, Coupon
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
            # user = self.request.user
            # user.balance -= 100
            # user.save()
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
                'key': key,
            },
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
        print('реквестПОСТ---', request.POST)
        print('реквест---', self.request)
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


class StoreAccountsView(TemplateView):
    template_name = 'store/store_accounts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        acounts = AccountObject.objects.filter(is_active=True)
        server = self.request.GET.get('server')
        rank = self.request.GET.get('rank', None)
        champions_min = self.request.GET.get('champions_min', None)
        champions_max = self.request.GET.get('champions_max', None)
        price_min = self.request.GET.get('price_min', None)
        price_max = self.request.GET.get('price_max', None)
        print('rank=', server)

        if champions_min is not None:
            try:
                champions_min = int(champions_min)
            except ValueError:
                champions_min = None

        if champions_max is not None:
            try:
                champions_max = int(champions_max)
            except ValueError:
                champions_max = None
        if price_min is not None:
            try:
                price_min = int(price_min)
            except ValueError:
                price_min = None

        if price_max is not None:
            try:
                price_max = int(price_max)
            except ValueError:
                price_max = None

        # Фильтрация
        if server and server != 'all':
            acounts = acounts.filter(server=server)

        if rank:
            acounts = acounts.filter(rang=rank)

        if champions_min and champions_max:
            acounts = acounts.filter(champions__range=(champions_min, champions_max))
        if champions_min and champions_max is None:
            acounts = acounts.filter(champions__gte=champions_min)
        if champions_min is None and champions_max:
            acounts = acounts.filter(champions__lte=champions_max)

        if price_min and price_max:
            acounts = acounts.filter(price__gte=price_min, price__lte=price_max)
        if price_min and champions_max is None:
            acounts = acounts.filter(price__gte=price_min)
        if price_min is None and champions_max:
            acounts = acounts.filter(price__lte=price_max)

        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(acounts, 10)
        current_page = paginator.page(page_number)

        context['accounts'] = list(current_page)[::-1]
        context['paginator'] = paginator
        context['current_page'] = current_page

        context['account_form'] = AccountObjectForm()
        print('CONTEXT', context)
        return context

    def post(self, request, *args, **kwargs):
        account_form = AccountObjectForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        context = self.get_context_data(**kwargs)

        if len(images) > 10:
            account_form.add_error(None, 'Можно загрузить не более 10 изображений.')

        if account_form.is_valid() and len(images) < 11:
            account = account_form.save(user=request.user)
            messages.success(request, 'Успешно! После проверки, покупатели смогут купить ваш аккаунт')

            for image in images:
                AccountsImage.objects.create(account=account, image=image)

            return redirect('store:store_accounts')

        errors = account_form.errors.values()
        for error in errors:
            for text in error:
                messages.error(request, text)
        return render(
            request, self.template_name, {'account_form': account_form, 'accounts': context['accounts']}
        )


class StoreAccountPageView(TemplateView):
    template_name = 'store/store_account_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = get_object_or_404(AccountObject, id=self.kwargs.get('id'))
        context['account'] = account

        if self.request.user == account.user:
            return context

        if not self.request.user.is_anonymous:
            chat_room, created = ChatRoom.objects.get_or_create(
                buyer=self.request.user, seller=account.user, account=account
            )
            context['chat_room'] = chat_room
        return context


class FaqView(TemplateView):
    template_name = 'store/faq.html'
