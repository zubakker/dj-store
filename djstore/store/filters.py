from django_filters import rest_framework

from store.models import Product



class ProductFilterSet(rest_framework.FilterSet):
    min_price = rest_framework.NumberFilter(field_name='price', lookup_expr='gt')
    max_price = rest_framework.NumberFilter(field_name='price', lookup_expr='lt')

    stock = rest_framework.NumberFilter(field_name='stock', lookup_expr='gte')
    class Meta:
        model = Product
        fields = ['name']

class ProductTagsFilterSet(ProductFilterSet):
    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        tags_list = self.request.GET.getlist('tags')
        for tag in tags_list:
            queryset = queryset.filter(tags=int(tag))
        return queryset
        
    class Meta:
        model = Product
        fields = ['tags']

