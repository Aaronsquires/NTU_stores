from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    out_of_stock_threshold = models.PositiveIntegerField(default=1)
    cost = models.FloatField()
    is_disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ('add', 'change', 'view')

    def is_out_of_stock(self):
        return self.quantity <= self.out_of_stock_threshold

    def __str__(self):
        return "{} - {}".format(self.code, self.description)


class Transaction(models.Model):
    products = models.ManyToManyField(Product, through='Purchase')
    account = models.CharField(max_length=50)
    buyer_id = models.CharField(max_length=50)
    buyer_name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ('add', 'view')

    def get_total_cost(self):
        total_cost = 0
        for purchase in self.purchase_set.all():
            if not purchase.is_returned:
                total_cost += purchase.product.cost * purchase.quantity

        return total_cost

    def get_products_count(self):
        return len(self.products.all())


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_returned = models.BooleanField(default=False)

    class Meta:
        default_permissions = ('add', 'change', 'view')

    def clean(self):
        super().clean()

        if self._state.adding:
            errors = {}

            if self.product.is_disabled:
                errors['product'] = _('The specified product is disabled')

            if self.quantity > self.product.quantity:
                errors['quantity'] = _('Purchase quantity exceeds available stock')

            if errors:
                raise ValidationError(errors)

    def get_total_cost(self):
        return self.product.cost * self.quantity

    def return_purchase(self):
        if self.is_returned:
            return

        self.is_returned = True
        self.product.quantity += self.quantity
        self.product.save()
        self.save()


class Order(models.Model):
    products = models.ManyToManyField(Product)
    supplier_name = models.CharField(max_length=50, null=True)
    supplier_site_name = models.CharField(max_length=50, null=True)
    supplier_remit_to_address = models.CharField(max_length=50, null=True)
    promised_date = models.DateTimeField(default=timezone.now)
    goods_and_services_total = models.FloatField(default=0.0)
    vat = models.FloatField(default=0.0)
    invoice_total = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
