from django.test import TestCase
from .models import Product, Transaction, Purchase


class TransactionTestCase(TestCase):
    def setUp(self):
        p1 = Product.objects.create(code='BP01', description='Pen',
                                    quantity=25, cost=2.15)
        p2 = Product.objects.create(code='BP02', description='Pen 2',
                                    quantity=17, cost=3.10)
        p3 = Product.objects.create(code='NB01', description='Notebook',
                                    quantity=12, cost=4.45)
        p4 = Product.objects.create(code='NB02', description='Notebook',
                                    quantity=12, cost=4.45)
        t1 = Transaction.objects.create(account='CS0192', buyer_id='N0000000',
                                        buyer_name='John Doe')
        Purchase.objects.create(product=p1, transaction=t1, quantity=4)
        Purchase.objects.create(product=p2, transaction=t1, quantity=1)
        Purchase.objects.create(product=p3, transaction=t1, quantity=5)
        Purchase.objects.create(product=p4, transaction=t1, quantity=5, is_returned=True)

        Transaction.objects.create(account='ME0147', buyer_id='N0000001',
                                   buyer_name='Jane Doe')

    # Tests that the Transaction model calculates the total cost correctly
    def test_total_cost(self):
        t1 = Transaction.objects.get(pk=1)
        t2 = Transaction.objects.get(pk=2)

        self.assertEqual(t1.get_total_cost(), 33.95)
        self.assertEqual(t2.get_total_cost(), 0)

    # Tests that the Transaction model calculates the total cost correctly
    def test_products_count(self):
        t1 = Transaction.objects.get(pk=1)
        t2 = Transaction.objects.get(pk=2)

        self.assertEqual(t1.get_products_count(), 4)
        self.assertEqual(t2.get_products_count(), 0)


class PurchaseTestCase(TestCase):
    def setUp(self):
        p1 = Product.objects.create(code='BP01', description='Pen',
                                    quantity=25, cost=2.15)
        p2 = Product.objects.create(code='BP02', description='Pen 2',
                                    quantity=17, cost=3.10)
        p3 = Product.objects.create(code='NB01', description='Notebook',
                                    quantity=12, cost=4.45)
        t1 = Transaction.objects.create(account='CS0192', buyer_id='N0000000',
                                        buyer_name='John Doe')
        Purchase.objects.create(product=p1, transaction=t1, quantity=4)
        Purchase.objects.create(product=p2, transaction=t1, quantity=1)
        Purchase.objects.create(product=p3, transaction=t1, quantity=5)

    # Tests that the method Purchase.get_total_cost returns the correct value
    def test_get_total_cost(self):
        t = Transaction.objects.get(pk=1)
        p1 = t.products.get(pk=1).purchase_set.get()
        p2 = t.products.get(pk=2).purchase_set.get()
        p3 = t.products.get(pk=3).purchase_set.get()

        self.assertEqual(p1.get_total_cost(), 8.6)
        self.assertEqual(p2.get_total_cost(), 3.1)
        self.assertEqual(p3.get_total_cost(), 22.25)

    # Tests that when a purchase is added its quantity is subtracted from Product
    def test_purchase_create(self):
        p1 = Product.objects.get(pk=1)
        p2 = Product.objects.get(pk=2)
        p3 = Product.objects.get(pk=3)

        self.assertEqual(p1.quantity, 21)
        self.assertEqual(p2.quantity, 16)
        self.assertEqual(p3.quantity, 7)

    # Tests that when a purchase is return the Product quantity is updated accordingly
    def test_purchase_return(self):
        p_i = Product.objects.get(pk=1)

        pc = Purchase.objects.get(pk=1)
        pc.return_purchase()

        p_a = Product.objects.get(pk=1)

        self.assertEqual(p_i.quantity, 21)
        self.assertEqual(p_a.quantity, 25)

    # Tests that when a Purchase is deleted its quantity is added to Product
    def test_purchase_delete(self):
        p_i = Product.objects.get(pk=1)

        pc = Purchase.objects.get(pk=1)
        pc.delete();

        p_a = Product.objects.get(pk=1)

        self.assertEqual(p_i.quantity, 21)
        self.assertEqual(p_a.quantity, 25)
