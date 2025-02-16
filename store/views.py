import json
import logging
import uuid
from statistics import mean

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView, TemplateView

from main.views import TitleMixin
from store.filters import AccountsFilter
from store.forms import (
    AccountObjectForm,
    AccountsFilterForm,
    BoostOrderForms,
    QualificationForm,
    ReviewsSellerForm,
    RPorderForm,
    SkinsOrderForm,
)
from store.models import AccountObject, AccountOrder, AccountsImage, ChatRoom, ReviewSellerModel
from store.services import check_coupon
from user.tasks import send_email_task
from utils.services import authenticated_logger, handle_form_errors


logger = logging.getLogger('main')


class StoreView(TitleMixin, TemplateView):
    template_name = 'store/store.html'
    title = 'Магазин'


class StoreEloBoostView(TitleMixin, TemplateView):
    template_name = 'store/store_elo_boost.html'
    title = 'Эло-буст'


class StoreEloBoostChoiceView(TitleMixin, TemplateView):
    template_name = 'store/store_elo_boost_choice.html'
    title = 'Эло-буст'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_form'] = BoostOrderForms()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            authenticated_logger(request)
            return redirect('user:login')

        form = BoostOrderForms(request.POST)
        form.request = self.request
        if form.is_valid():
            form.save()
            logger.info(f'Пользователь {request.user.username} успешно оформил заказ на Эло-буст.')
            messages.success(request, 'Покупка совершена успешно')
        else:
            handle_form_errors(request, form)
            return render(request, self.template_name, {'store_form': form})
        return redirect('main:home')


class PlacementMatchesView(TitleMixin, TemplateView):
    template_name = 'store/placement_matches.html'
    title = 'Квалификация'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qualification_form'] = QualificationForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            authenticated_logger(request)
            return redirect('user:login')

        form = QualificationForm(request.POST, request=request)

        if form.is_valid():
            form.save()
            logger.info(f'Пользователь {request.user.username} успешно оформил заказ на квалификацию.')
            messages.success(request, 'Покупка совершена успешно')
        else:
            handle_form_errors(request, form)
            return render(request, self.template_name, {'qualification_form': form})

        return redirect('main:home')


# ТЫК
def check_coupon_views(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon_code = data.get('coupon')

        status, message, sale = check_coupon(coupon_code, request.user)

        return JsonResponse({'success': status, 'message': message, 'discount': sale})


class StoreSkinsView(TitleMixin, TemplateView):
    template_name = 'store/store_skins.html'
    title = 'Скины'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skinorder_form'] = SkinsOrderForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            authenticated_logger(request)
            return redirect('user:login')

        form = SkinsOrderForm(request.POST)
        form.request = self.request

        if form.is_valid():
            key = str(uuid.uuid4())
            purchase_type = 'образа' if 'skin_name' in request.POST else 'персонажа'
            item_name = request.POST.get('skin_name') or request.POST.get('char_name')
            mail_subject = 'Покупка с сайта Lol-Pay'
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

            form.save()
            send_email_task.delay(mail_subject, html_message, [self.request.user.email])

            logger.info(
                f'Пользователь {request.user.username} успешно оформил заказ\
                    на {purchase_type} {item_name}.'
            )
            messages.success(request, 'Покупка совершена, письмо отправлено на почту')
        else:
            handle_form_errors(request, form)
            return render(request, self.template_name, {'skinorder_form': form})

        return redirect('main:home')


class StoreRPView(TitleMixin, TemplateView):
    template_name = 'store/store_rp.html'
    title = 'Покупка RP'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rp_form'] = RPorderForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            authenticated_logger(request)
            return redirect('user:login')

        form = RPorderForm(request.POST)
        form.request = self.request

        if form.is_valid():
            form.save(user=request.user)
            logger.info(f'Пользователь {request.user.username} успешно оформил заказ RP.')
            messages.success(request, 'Покупка совершена успешно')
        else:
            handle_form_errors(request, form)
            return render(request, self.template_name, {'rp_form': form})
        return redirect('main:home')


class StoreAccountsView(TitleMixin, ListView):
    template_name = 'store/store_accounts.html'
    title = 'Аккаунты'
    paginate_by = 10
    model = AccountObject
    context_object_name = 'accounts'

    def get_queryset(self):
        # ТЫК
        qureset = (
            self.model.objects.filter(is_active=True).select_related('user').order_by('-created_at')
        )
        filter_form = AccountsFilterForm(self.request.GET)

        if filter_form.is_valid():
            qureset = AccountsFilter(self.request.GET, queryset=qureset, request=self.request).qs

        return qureset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_list'] = self.get_queryset().values_list('user', flat=True)
        context['account_form'] = AccountObjectForm()
        context['filter_form'] = AccountsFilterForm(self.request.GET)
        return context

    def post(self, request, *args, **kwargs):
        account_form = AccountObjectForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)
        if len(images) > 10:
            account_form.add_error(None, 'Можно загрузить не более 10 изображений.')
            logger.warning(f'Попытка загрузить больше 10 изображений. Количество: {len(images)}')

        if account_form.is_valid() and len(images) < 11:
            account = account_form.save(user=request.user)
            logger.info(f'Пользователь {request.user.username} добавил новый аккаунт: {account.id}')

            for image in images:
                AccountsImage.objects.create(account=account, image=image)
                logger.info(f'Изображение для аккаунта {account.id} успешно загружено.')

            messages.success(request, 'Успешно! После проверки, покупатели смогут купить ваш аккаунт')

            return redirect('store:store_accounts')

        handle_form_errors(request, account_form)
        return render(request, self.template_name, {'account_form': account_form, **context})


class StoreAccountPageView(TitleMixin, ListView):
    template_name = 'store/store_account_page.html'
    title = 'Обзор аккаунта'
    model = ReviewSellerModel
    paginate_by = 10
    context_object_name = 'reviews'

    # ТЫК
    def get_queryset(self):
        self.account = get_object_or_404(
            AccountObject.objects.select_related('user', 'buyer').prefetch_related('images'), id=self.kwargs.get('id')
        )
        return (
            ReviewSellerModel.objects.filter(parent__isnull=True, seller=self.account.user)
            .select_related('buyer', 'seller', 'parent', 'product')
            .prefetch_related('children')
        )

    def get_context_data(self, **kwargs):
        queryset= self.object_list

        context = super().get_context_data(**kwargs)
        context['account'] = self.account
        context['form'] = ReviewsSellerForm()
        context['set_form'] = AccountObjectForm(instance=self.account)
        context['average_stars'] = mean(
            map(int, queryset.values_list('stars', flat=True) or [0])
        )
        context['can_reviews'] = (
            self.request.user.is_authenticated
            and AccountOrder.objects.select_related('account')
            .filter(user=self.request.user, account__user=self.account.user)
            .exists()
            and self.request.user.id not in queryset.values_list('buyer', flat=True)
            and self.account.user != self.request.user
        )

        if self.request.user == self.account.user:
            return context

        if not self.request.user.is_anonymous:
            context['chat_room'], _ = (
                ChatRoom.objects.select_related('seller', 'buyer')
                .prefetch_related('messages', 'messages__author')
                .get_or_create(buyer=self.request.user, seller=self.account.user, account=self.account)
            )
        return context

    def post(self, request, *args, **kwargs):
        self.account = get_object_or_404(AccountObject, id=self.kwargs.get('id'))
        logger.debug(f'POST запрос для аккаунта с ID {self.account.id}, данные: {request.POST}')

        if 'delete_account' in request.POST:
            return self.handle_delete_account(request)

        if 'setting' in request.POST:
            return self.handle_update_settings(request)

        if 'reviewsbt' in request.POST:
            return self.handle_reviews(request)

        return redirect(request.META.get('HTTP_REFERER', '/'))

    def handle_delete_account(self, request):
        if self.account.is_active:
            self.account.is_active = False
            self.account.is_archive = True
            self.account.save()
            messages.success(request, 'Аккаунт успешно удалён')
            logger.info(
                f'Аккаунт с ID {self.account.id} был удалён пользователем {request.user.username}'
            )
        return redirect('store:store_accounts')

    def handle_update_settings(self, request):
        if not self.account.is_active:
            messages.error(request, 'Этот аккаунт больше не активен.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        set_form = AccountObjectForm(request.POST, request.FILES, instance=self.account)
        images = request.FILES.getlist('images')
        logger.debug(f'Загруженные изображения для аккаунта {self.account.id}: {images}')

        if len(images) > 10:
            set_form.add_error(None, 'Можно загрузить не более 10 изображений.')
            logger.warning(f'Попытка загрузить больше 10 изображений для аккаунта {self.account.id}')

        if set_form.is_valid() and len(images) < 11:
            set_form.save()

            for image in images:
                AccountsImage.objects.create(account=self.account, image=image)
                logger.info(f'Изображение для аккаунта {self.account.id} успешно загружено.')

            messages.success(request, 'Настройки успешно обновлены.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        handle_form_errors(request, set_form)
        return render(request, self.template_name, {'set_form': set_form})

    def handle_reviews(self, request):
        form = ReviewsSellerForm(request.POST)
        form.request = self.request
        form.product = get_object_or_404(AccountObject, id=self.kwargs.get('id'))

        if form.is_valid():
            form.save()
            logger.info(
                f'Пользователь {request.user.username} оставил отзыв\
                        для пользователя {self.account.user.username}'
            )
        else:
            handle_form_errors(request, form)
            return render(request, self.template_name, {'form': form})

        return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_image(request, image_id):
    if request.method == 'DELETE':
        image = AccountsImage.objects.get(id=image_id)
        image.delete()
        logger.info(f'Изображение с ID {image_id} успешно удалено.')
        return JsonResponse({'message': 'Изображение удалено'}, status=200)

    logger.error(f'Изображение с ID {image_id} не найдено для удаления.')
    return JsonResponse({'error': 'Изображение не найдено'}, status=200)


class FaqView(TitleMixin, TemplateView):
    template_name = 'store/faq.html'
    title = 'FAQ'
