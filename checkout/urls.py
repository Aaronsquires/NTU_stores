from django.urls import path

from . import views


app_name = 'checkout'
urlpatterns = [
    path('', views.CheckoutView.as_view(), name='index'),
    path('create_transaction/', views.CreateTransactionView.as_view(), name='create_transaction'),
    path('confirm_transaction/', views.confirm_transaction, name='confirm_transaction'),
    path('products/', views.ProductsJsonView.as_view(), name='products'),
]
