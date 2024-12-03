from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from store.views import (
    FaqView,
    PlacementMatchesView,
    StoreAccountPageView,
    StoreAccountsView,
    StoreEloBoostChoiceView,
    StoreEloBoostView,
    StoreRPView,
    StoreSkinsView,
    StoreView,
    check_coupon,
    delete_image,
)


app_name = 'store'

urlpatterns = [
    path('store/', StoreView.as_view(), name='store'),
    path('store-elo-boost/', StoreEloBoostView.as_view(), name='store_elo_boost'),
    path('store-elo-boost-choice/', StoreEloBoostChoiceView.as_view(), name='store_elo_boost_choice'),
    path('placement-matches/', PlacementMatchesView.as_view(), name='placement_matches'),
    path('check-coupon/', check_coupon),
    path('store-skins/', StoreSkinsView.as_view(), name='store_skins'),
    path('store-rp/', StoreRPView.as_view(), name='store_rp'),
    path('store-accounts/', StoreAccountsView.as_view(), name='store_accounts'),
    path('store-account-page/<int:id>/', StoreAccountPageView.as_view(), name='store_account_page'),
    path('faq', FaqView.as_view(), name='faq'),
    path('delete-image/<int:image_id>/', delete_image, name='delete-image'),
]

