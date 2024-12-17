import json
import logging
import uuid
from statistics import mean

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from main.views import TitleMixin
from store.forms import (
    AccountObjectForm,
    AccountsFilterForm,
    # AccountsImageForm,
    BoostOrderForms,
    QualificationForm,
    ReviewsSellerForm,
    RPorderForm,
    SkinsOrderForm,
)
from store.models import AccountObject, AccountOrder, AccountsImage, ChatRoom, ReviewSellerModel
from store.services import check_coupon
from user.tasks import send_email_task


logger = logging.getLogger('main')
# Create your views here.


class StoreView(TitleMixin, TemplateView):
    template_name = 'store/store.html'
    title = 'Магазин'


class StoreEloBoostView(TitleMixin, TemplateView):
    template_name = 'store/store_elo_boost.html'
    title = 'Эло-буст'


class StoreEloBoostChoiceView(TitleMixin, TemplateView):
    template_name = 'store/store_elo_boost_choice.html'
    login_url = '/login/'
    title = 'Эло-буст'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_form'] = BoostOrderForms()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning('Попытка оформления заказа без входа в аккаунт.')
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')
        # print('post', request.POST)
        form = BoostOrderForms(request.POST)
        form.request = self.request
        if form.is_valid():
            form.save()
            logger.info(f'Пользователь {request.user.username} успешно оформил заказ на Эло-буст.')
            messages.success(request, 'Покупка совершена успешно')
        else:
            logger.error(
                f'Ошибка оформления заказа для пользователя {request.user.username}. Ошибки формы: {form.errors}.'
            )
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'store_form': form})
        return redirect('store:store_elo_boost_choice')


class PlacementMatchesView(TitleMixin, TemplateView):
    template_name = 'store/placement_matches.html'
    title = 'Квалификация'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qualification_form'] = QualificationForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning('Попытка оформления заказа без входа в аккаунт.')
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')
        print('post', request.POST)
        form = QualificationForm(request.POST, request=request)
        # form.request = self.request
        if form.is_valid():
            form.save()
            logger.info(f'Пользователь {request.user.username} успешно оформил заказ на квалификацию.')
            messages.success(request, 'Покупка совершена успешно')
        else:
            logger.error(
                f'Ошибка оформления заказа для пользователя {request.user.username}. Ошибки формы: {form.errors}'
            )
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'qualification_form': form})

        return redirect('store:placement_matches')


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
            logger.warning('Попытка оформления заказа без входа в аккаунт.')
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
            logger.info(
                f'Пользователь {request.user.username} успешно оформил заказ на {purchase_type} {item_name}.'
            )
            messages.success(request, 'Покупка совершена, письмо отправлено на почту')
        else:
            logger.error(
                f'Ошибка оформления заказа для пользователя {request.user.username}. Ошибки формы: {form.errors}.'
            )
            # Отобразим ошибки формы, чтобы увидеть причину неудачи
            print('1', form.errors)
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'skinorder_form': form})
        print('Прошло')
        return redirect('store:store_skins')


class StoreRPView(TitleMixin, TemplateView):
    template_name = 'store/store_rp.html'
    title = 'RP'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rp_form'] = RPorderForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning('Попытка оформления заказа без входа в аккаунт.')
            messages.warning(request, 'Пожалуйста, войдите в аккаунт, чтобы оформить заказ')
            return redirect('user:login')

        form = RPorderForm(request.POST)
        form.request = self.request
        print('реквестПОСТ---', request.POST)
        print('реквест---', self.request)
        if form.is_valid():
            form.save(user=request.user)
            logger.info(f'Пользователь {request.user.username} успешно оформил заказ RP.')
            messages.success(request, 'Покупка совершена успешно')
        else:
            # Отобразим ошибки формы, чтобы увидеть причину неудачи
            logger.error(
                f'Ошибка оформления заказа RP для пользователя {request.user.username}. Ошибки формы: {form.errors}.'
            )
            errors = form.errors.values()
            for error in errors:
                for text in error:
                    messages.error(request, text)
            return render(request, self.template_name, {'rp_form': form})
        return redirect('store:store_rp')


class StoreAccountsView(TitleMixin, TemplateView):
    template_name = 'store/store_accounts.html'
    title = 'Аккаунты'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        acounts = AccountObject.objects.filter(is_active=True).order_by('-created_at')
        myaccount = self.request.GET.get('myaccount', None)
        user = self.request.user
        user_list = acounts.values_list('user', flat=True)
        filter_form = AccountsFilterForm(self.request.GET)

        if filter_form.is_valid():
            server = filter_form.cleaned_data.get('server')
            rank = filter_form.cleaned_data.get('rank')
            champions_min = filter_form.cleaned_data.get('champions_min')
            champions_max = filter_form.cleaned_data.get('champions_max')
            price_min = filter_form.cleaned_data.get('price_min')
            price_max = filter_form.cleaned_data.get('price_max')

            logger.info(
                f'Фильтрация аккаунтов: server={server}, rank={rank}, champions_min={champions_min}, '
                f'champions_max={champions_max}, price_min={price_min}, price_max={price_max}'
            )

        # Фильтрация
        if server and server != 'all':
            acounts = acounts.filter(server=server)

        if rank:
            acounts = acounts.filter(rang=rank)

        if champions_min is not None and champions_max is not None:
            acounts = acounts.filter(champions__range=(champions_min, champions_max))
        if champions_min and champions_max is None:
            acounts = acounts.filter(champions__gte=champions_min)
        if champions_min is None and champions_max:
            acounts = acounts.filter(champions__lte=champions_max)

        if price_min and price_max:
            acounts = acounts.filter(price__gte=price_min, price__lte=price_max)
        if price_min and price_max is None:
            acounts = acounts.filter(price__gte=price_min)
        if price_min is None and price_max:
            acounts = acounts.filter(price__lte=price_max)

        if myaccount:
            acounts = acounts.filter(user=user)
            logger.info(f"Фильтрация по моим аккаунтам для пользователя {user.username}")

        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(acounts, 10)
        current_page = paginator.page(page_number)

        context['accounts'] = list(current_page)
        context['paginator'] = paginator
        context['current_page'] = current_page
        context['user'] = user
        context['user_list'] = user_list
        context['account_form'] = AccountObjectForm()
        context['filter_form'] = filter_form
        logger.debug(f"Контекст для отображения: {context}")
        return context

    def post(self, request, *args, **kwargs):
        account_form = AccountObjectForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        context = self.get_context_data(**kwargs)

        if len(images) > 10:
            account_form.add_error(None, 'Можно загрузить не более 10 изображений.')
            logger.warning(f"Попытка загрузить больше 10 изображений. Количество: {len(images)}")

        if account_form.is_valid() and len(images) < 11:
            account = account_form.save(user=request.user)
            logger.info(f"Пользователь {request.user.username} добавил новый аккаунт: {account.id}")

            for image in images:
                AccountsImage.objects.create(account=account, image=image)
                logger.info(f"Изображение для аккаунта {account.id} успешно загружено.")

            messages.success(request, 'Успешно! После проверки, покупатели смогут купить ваш аккаунт')

            return redirect('store:store_accounts')

        logger.error(f"Ошибка при добавлении аккаунта для пользователя {request.user.username}. Ошибки формы: {account_form.errors}")

        errors = account_form.errors.values()
        for error in errors:
            for text in error:
                messages.error(request, text)
        return render(
            request, self.template_name, {'account_form': account_form, 'accounts': context['accounts']}
        )


class StoreAccountPageView(TitleMixin, TemplateView):
    template_name = 'store/store_account_page.html'
    title = 'Обзор аккаунта'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = get_object_or_404(AccountObject, id=self.kwargs.get('id'))
        context['account'] = account
        context['form'] = ReviewsSellerForm()
        context['set_form'] = AccountObjectForm(instance=account)
        reviews = ReviewSellerModel.objects.filter(parent__isnull=True, seller=account.user)
        user_list = reviews.values_list('buyer', flat=True)
        user = self.request.user
        average_stars = mean(map(int, reviews.values_list('stars', flat=True) or [0]))
        if user.is_authenticated:
            context['can_reviews'] = AccountOrder.objects.filter(
                user=user, account__user=account.user
            ).exists()
        else:
            context['can_reviews'] = False

        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(reviews, 10)
        current_page = paginator.page(page_number)

        context['reviews'] = current_page
        context['paginator'] = paginator
        context['current_page'] = current_page
        context['user_list'] = user_list
        context['user'] = user
        context['average_stars'] = average_stars

        if self.request.user == account.user:
            return context

        if not self.request.user.is_anonymous:
            chat_room, created = ChatRoom.objects.get_or_create(
                buyer=self.request.user, seller=account.user, account=account
            )
            context['chat_room'] = chat_room
        return context

    def post(self, request, *args, **kwargs):
        account = get_object_or_404(AccountObject, id=self.kwargs.get('id'))
        logger.debug(f"POST запрос для аккаунта с ID {account.id}, данные: {request.POST}")

        if 'delete_account' in request.POST and account.is_active:
            account.is_archive = True
            account.save()
            messages.success(request, 'Аккаунт успешно удалён')
            logger.info(f"Аккаунт с ID {account.id} был удалён пользователем {request.user.username}")
            return redirect('store:store_accounts')

        if 'setting' in request.POST and account.is_active:
            set_form = AccountObjectForm(request.POST, request.FILES, instance=account)
            print('FILES:', request.FILES)
            images = request.FILES.getlist('images')
            logger.debug(f"Загруженные изображения для аккаунта {account.id}: {images}")
            if len(images) > 10:
                set_form.add_error(None, 'Можно загрузить не более 10 изображений.')
                logger.warning(f"Попытка загрузить больше 10 изображений для аккаунта {account.id}")

            if set_form.is_valid() and len(images) < 11:
                set_form.save()

                for image in images:
                    print('NU CHTO')
                    AccountsImage.objects.create(account=account, image=image)
                    logger.info(f"Изображение для аккаунта {account.id} успешно загружено.")
            else:
                errors = set_form.errors.values()
                print(set_form.errors)
                for error in errors:
                    for text in error:
                        messages.error(request, text)
                return render(request, self.template_name, {'set_form': set_form})
            logger.error(f"Ошибка при обновлении аккаунта {account.id}, ошибки формы: {set_form.errors}")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if 'reviewsbt' in request.POST:
            form = ReviewsSellerForm(request.POST)
            form.request = self.request
            form.product = get_object_or_404(AccountObject, id=self.kwargs.get('id'))
            if form.is_valid():
                form.save()
                logger.info(f"Пользователь {request.user.username} оставил отзыв для аккаунта {account.id}")
            else:
                errors = form.errors.values()
                print(form.errors)
                for error in errors:
                    for text in error:
                        messages.error(request, text)
                logger.error(f"Ошибка при добавлении отзыва для аккаунта {account.id}, ошибки формы: {form.errors}")
                return render(request, self.template_name, {'form': form})
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return redirect(request.META.get('HTTP_REFERER', '/'))


# Удаление изображений
def delete_image(request, image_id):
    if request.method == 'DELETE':
        image = AccountsImage.objects.get(id=image_id)
        image.delete()
        logger.info(f"Изображение с ID {image_id} успешно удалено.")
        return JsonResponse({'message': 'Изображение удалено'}, status=200)

    logger.error(f"Изображение с ID {image_id} не найдено для удаления.")
    return JsonResponse({'error': 'Изображение не найдено'}, status=200)


class FaqView(TitleMixin, TemplateView):
    template_name = 'store/faq.html'
    title = 'FAQ'
