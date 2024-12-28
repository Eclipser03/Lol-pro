import django_filters

from store.models import AccountObject


class AccountsFilter(django_filters.FilterSet):
    champions = django_filters.RangeFilter()
    price = django_filters.RangeFilter()

    myaccount = django_filters.BooleanFilter(method='my_account_filter')

    def my_account_filter(self, queryset, name, value):
        if value:
            return queryset.filter(user=self.request.user)
        return queryset

    class Meta:
        model = AccountObject
        fields = ['server', 'rang', 'champions', 'price', 'myaccount']
