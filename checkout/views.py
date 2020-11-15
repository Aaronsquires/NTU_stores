import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, JsonResponse
from django.views import generic
from django.core.exceptions import ValidationError
from django.shortcuts import render

from dashboard.models import Product, Purchase, Transaction


class CheckoutView(PermissionRequiredMixin, generic.base.TemplateView):
    template_name = 'checkout/index.html'
    permission_required = [
        'dashboard.add_transaction',
        'dashboard.add_purchase',
        'dashboard.view_product'
        'dashboard.change_product'
        ]
    permission_denied_message = 'You do not have permission to process checkouts'


class CreateTransactionView(PermissionRequiredMixin, generic.base.View):
    permission_required = [
        'dashboard.add_transaction',
        'dashboard.add_purchase',
        'dashboard.change_product'
        ]
    permission_denied_message = 'You do not have permission to process checkouts'

    def post(self, request):
        if not request.POST.get('account') or\
           not request.POST.get('buyer_id') or\
           not request.POST.get('buyer_name') or\
           not request.POST.get('items'):
            return JsonResponse({'errors': ['Invalid data'], 'data': request.POST}, status=400)

        account = request.POST.get('account')
        buyer_id = request.POST.get('buyer_id')
        buyer_name = request.POST.get('buyer_name')
        items = json.loads(request.POST.get('items'))

        try:
            transaction = Transaction(
                account=account,
                buyer_id=buyer_id,
                buyer_name=buyer_name
            )
            transaction.full_clean()
            transaction.save()

            products = []
            purchases = []
            for item in items:
                product = Product.objects.get(pk=item['productId'])
                products.append(product)

                purchase = Purchase(
                    transaction=transaction,
                    product=product,
                    quantity=item['quantity']
                )
                purchase.full_clean()
                purchases.append(purchase)

            for purchase in purchases:
                purchase.save()
        except ValidationError as e:
            transaction.delete()
            return JsonResponse({'errors': e.message_dict}, status=400)
        except:
            transaction.delete()
            return JsonResponse({'errors': ['Invalid data']}, status=400)

        return JsonResponse({'success': 'Transaction Created'}, status=201)

    def get(self, request):
        raise Http404()


class ProductsJsonView(PermissionRequiredMixin, generic.base.View):
    permission_required = 'dashboard.view_product'
    permission_denied_message = 'You do not have permission to view products'

    def get(self, request):
        products = []
        for product in Product.objects.filter(is_disabled=False).filter(quantity__gt=0):
            products.append({
                'pk': product.pk,
                'code': product.code,
                'description': product.description,
                'quantity': product.quantity
            })

        return JsonResponse({'products': products})


def confirm_transaction(request):
    return render(request, "checkout/confirm.html")