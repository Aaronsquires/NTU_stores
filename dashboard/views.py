import csv
from datetime import timedelta

from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import Group, User
from django.db.models import Count, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import UserChangeForm, UserCreationForm
from .models import Order, Product, Purchase, Transaction
from .utils import string_to_date_interval


class HomeView(generic.TemplateView):
    template_name = 'dashboard/home.html'


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dashboard/index.html'


class InventoryView(PermissionRequiredMixin, generic.ListView):
    model = Product
    template_name = 'dashboard/inventory.html'
    ordering = ['code']
    permission_required = 'dashboard.view_product'
    permission_denied_message = 'You do not have permission to view products'

    def get_queryset(self):
        query_set = super().get_queryset()

        if self.request.GET.get('filter_date'):
            start, end = string_to_date_interval(self.request.GET.get('filter_date'))

            if start and end:
                if start == end:
                    query_set = query_set.filter(created__year=start.year,
                                                 created__month=start.month,
                                                 created__day=start.day)
                else:
                    query_set = query_set.filter(created__range=[start, end])

        return query_set

    def get_context_data(self):
        context = super().get_context_data()

        if self.request.GET.get('filter_date'):
            context['filter_date'] = self.request.GET.get('filter_date').replace("_", " ")

        return context


class AddProductView(PermissionRequiredMixin, generic.CreateView):
    model = Product
    fields = ['code', 'description', 'quantity', 'out_of_stock_threshold', 'cost']
    success_url = reverse_lazy('dashboard:inventory')
    permission_required = 'dashboard.add_product'
    permission_denied_message = 'You do not have permission to add products'


class EditProductView(PermissionRequiredMixin, generic.UpdateView):
    model = Product
    fields = ['code', 'description', 'quantity', 'out_of_stock_threshold', 'cost', 'is_disabled']
    success_url = reverse_lazy('dashboard:inventory')
    permission_required = 'dashboard.change_product'
    permission_denied_message = 'You do not have permission to edit products'


class OutOfStockProductsJsonView(PermissionRequiredMixin, generic.base.View):
    permission_required = 'dashboard.view_product'
    permission_denied_message = 'You do not have permission to view products'

    def get(self, request):
        products = []
        for product in Product.objects.filter(quantity__lte=F('out_of_stock_threshold')):
            products.append({
                'pk': product.pk,
                'code': product.code,
                'description': product.description,
                'quantity': product.quantity,
                'out_of_stock_threshold': product.out_of_stock_threshold,
            })

        return JsonResponse({'products': products})


class FiveBestSellerProductsJson(PermissionRequiredMixin, generic.base.View):
    permission_required = 'dashboard.view_product'
    permission_denied_message = 'You do not have permission to view products'

    def get(self, request):
        products = []
        for product in Purchase.objects\
                               .values('product__pk', 'product__code')\
                               .annotate(purchases_count=Count('product__code'))\
                               .order_by('-purchases_count')[:5]:
            products.append({
                'pk': product['product__pk'],
                'code': product['product__code'],
                'purchases_count': product['purchases_count'],
            })

        return JsonResponse({'products': products})


def export_products_as_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    
    products = Product.objects.all()
    writer = csv.writer(response)
    writer.writerow(['code', 'description', 'quantity', 'cost'])
    for product in products:
        writer.writerow([
            product.code,
            product.description,
            product.quantity,
            product.cost
        ])
    
    return response


class TransactionsView(PermissionRequiredMixin, generic.ListView):
    model = Transaction
    template_name = 'dashboard/transactions.html'
    permission_required = 'dashboard.view_transaction'
    permission_denied_message = 'You do not have permission to view transactions'

    def get_queryset(self):
        query_set = super().get_queryset()

        if self.request.GET.get('filter_date'):
            start, end = string_to_date_interval(self.request.GET.get('filter_date'))

            if start and end:
                if start == end:
                    query_set = query_set.filter(created__year=start.year,
                                                 created__month=start.month,
                                                 created__day=start.day)
                else:
                    query_set = query_set.filter(created__range=[start, end])

        return query_set

    def get_context_data(self):
        context = super().get_context_data()

        if self.request.GET.get('filter_date'):
            context['filter_date'] = self.request.GET.get('filter_date').replace("_", " ")

        return context


class ShowTransactionView(PermissionRequiredMixin, generic.DetailView):
    model = Transaction
    permission_required = 'dashboard.view_transaction'
    permission_denied_message = 'You do not have permission to view transactions'


class TodayTransactionsJson(PermissionRequiredMixin, generic.base.View):
    model = Transaction
    permission_required = 'dashboard.view_transaction'
    permission_denied_message = 'You do not have permission to view transactions'

    def get(self, request):
        transactions = []
        today = timezone.now()
        for transaction in Transaction.objects.filter(
                created__year=today.year,
                created__month=today.month,
                created__day=today.day):
            transactions.append({
                'pk': transaction.pk,
                'account': transaction.account,
                'buyer_id': transaction.buyer_id,
                'buyer_name': transaction.buyer_name,
                'products_count': transaction.get_products_count(),
                'total_cost': transaction.get_total_cost(),
            })

        return JsonResponse({'transactions': transactions})


class DailyRevenueJson(PermissionRequiredMixin, generic.base.View):
    model = Transaction
    permission_required = 'dashboard.view_transaction'
    permission_denied_message = 'You do not have permission to view transactions'

    def get(self, request):
        days = []
        today = timezone.now().date()

        for i in range(0,7):
            date = today - timedelta(days=i)

            transactions = Transaction.objects.filter(created__year=date.year,
                                                 created__month=date.month,
                                                 created__day=date.day)
            revenue = 0
            for transaction in transactions:
                revenue += transaction.get_total_cost()

            days.append({'date': date, 'revenue': revenue})

        return JsonResponse({'days': days})


def export_transactions_as_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    transactions = Transaction.objects.all()
    writer = csv.writer(response)
    writer.writerow(['Account', 'Buyer ID', 'Buyer Name', 'Created', 'Modified', 'Total Cost', 'Count'])
    for transaction in transactions:
        writer.writerow([
            transaction.account,
            transaction.buyer_id,
            transaction.buyer_name,
            transaction.created.strftime("%d/%m/%Y %H:%M"),
            transaction.modified.strftime("%d/%m/%Y %H:%M"),
            transaction.get_total_cost(),
            transaction.get_products_count()
        ])
    
    return response


class ReturnPurchaseView(PermissionRequiredMixin, generic.base.View):
    permission_required = 'dashboard.change_purchase'
    permission_denied_message = 'You do not have permission to edit purchases'

    def get(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk, is_returned=False)

        return render(request, 'dashboard/purchase_return.html',
                      {'purchase': purchase})

    def post(self, request, pk):
        purchase = get_object_or_404(Purchase, pk=pk, is_returned=False)
        purchase.return_purchase()

        return redirect('dashboard:show_transaction', pk=purchase.transaction.pk)


class OrderView(generic.ListView):
    model = Order
    template_name = 'dashboard/orders.html'
    ordering = ['modified']


class AddOrderView(PermissionRequiredMixin, generic.CreateView):
    model = Order
    fields = [
        'supplier_name',
        'supplier_site_name',
        'supplier_remit_to_address',
        'promised_date',
        'goods_and_services_total',
        'vat',
        'invoice_total',
        'products',
    ]
    success_url = reverse_lazy('dashboard:orders')
    permission_required = 'dashboard.add_order'
    raise_exception = True
    permission_denied_message = 'You do not have permission to add orders'


class EditOrderView(generic.UpdateView):
    model = Order
    fields = [
        'supplier_name',
        'supplier_site_name',
        'supplier_remit_to_address',
        'promised_date',
        'goods_and_services_total',
        'vat',
        'invoice_total',
        'products',
    ]
    success_url = reverse_lazy('dashboard:orders')
    permission_required = 'dashboard.edit_order'
    raise_exception = True
    permission_denied_message = 'You do not have permission to edit orders'


class DeleteOrderView(generic.DeleteView):
    model = Order
    success_url = reverse_lazy('dashboard:orders')


class UsersView(PermissionRequiredMixin, generic.ListView):
    model = User
    template_name = 'dashboard/users.html'
    permission_required = 'users.view_user'
    permission_denied_message = 'You do not have permission to view users'


class AddUserView(PermissionRequiredMixin, generic.CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'dashboard/user_create_form.html'
    success_url = reverse_lazy('dashboard:users')
    permission_required = 'users.add_user'
    permission_denied_message = 'You do not have permission to add users'


class EditUserView(PermissionRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'dashboard/user_edit_form.html'
    success_url = reverse_lazy('dashboard:users')
    permission_required = 'users.change_user'
    permission_denied_message = 'You do not have permission to edit users'


class GroupsView(PermissionRequiredMixin, generic.ListView):
    model = Group
    template_name = 'dashboard/groups.html'
    permission_required = 'users.view_group'
    permission_denied_message = 'You do not have permission to view groups'


class AddGroupView(PermissionRequiredMixin, generic.CreateView):
    model = Group
    fields = ['name', 'permissions']
    template_name = 'dashboard/group_form.html'
    success_url = reverse_lazy('dashboard:groups')
    permission_required = 'users.add_group'
    permission_denied_message = 'You do not have permission to add groups'


class EditGroupView(PermissionRequiredMixin, generic.UpdateView):
    model = Group
    fields = ['name', 'permissions']
    template_name = 'dashboard/group_form.html'
    success_url = reverse_lazy('dashboard:groups')
    permission_required = 'users.change_group'
    permission_denied_message = 'You do not have permission to edit groups'
