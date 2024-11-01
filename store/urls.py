from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from store.views import (
    PlacementMatchesView,
    StoreEloBoostChoiceView,
    StoreEloBoostView,
    StoreSkinsView,
    StoreView,
    check_coupon,
)


app_name = 'store'

urlpatterns = [
    path('store/', StoreView.as_view(), name='store'),
    path('store-elo-boost/', StoreEloBoostView.as_view(), name='store_elo_boost'),
    path('store-elo-boost-choice/', StoreEloBoostChoiceView.as_view(), name='store_elo_boost_choice'),
    path('placement-matches/', PlacementMatchesView.as_view(), name='placement_matches'),
    path('check-coupon/', check_coupon),
    path('store-skins/', StoreSkinsView.as_view(), name='store_skins'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
