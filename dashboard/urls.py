from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),

    # Inventory
    path('inventory/', views.InventoryView.as_view(), name='inventory'),
    path('inventory/add/', views.AddProductView.as_view(), name='add_product'),
    path('inventory/edit/<int:pk>/', views.EditProductView.as_view(), name='edit_product'),
    path('inventory/export/', views.export_products_as_csv, name='export_products'),
    path('inventory/out_of_stock_json/', views.OutOfStockProductsJsonView.as_view(), name='out_of_stock_products_json'),
    path('inventory/five_best_sellers_json/', views.FiveBestSellerProductsJson.as_view(), name='five_best_seller_products_json'),

    # Transactions
    path('transactions/', views.TransactionsView.as_view(), name='transactions'),
    path('transactions/show/<int:pk>/', views.ShowTransactionView.as_view(), name='show_transaction'),
    path('transactions/purchase/return/<int:pk>/', views.ReturnPurchaseView.as_view(), name='return_purchase'),
    path('transactions/export/', views.export_transactions_as_csv, name='export_transactions'),
    path('transactions/today_json/', views.TodayTransactionsJson.as_view(), name='today_transactions_json'),
    path('transactions/daily_revenue_json/', views.DailyRevenueJson.as_view(), name='daily_revenue_json'),

    # Accounts
    path('accounts/login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='dashboard/logout.html'), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='dashboard/password_change.html', success_url=reverse_lazy('dashboard:password_change_done')), name='password_change'),
    path('accounts/password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='dashboard/password_change_done.html'), name='password_change_done'),
    path('accounts/users/', views.UsersView.as_view(), name='users'),
    path('accounts/users/add', views.AddUserView.as_view(), name='add_user'),
    path('accounts/users/edit/<int:pk>', views.EditUserView.as_view(), name='edit_user'),
    path('accounts/groups/', views.GroupsView.as_view(), name='groups'),
    path('accounts/groups/add', views.AddGroupView.as_view(), name='add_group'),
    path('accounts/groups/edit/<int:pk>', views.EditGroupView.as_view(), name='edit_group'),

    # Orders
    path('orders/', views.OrderView.as_view(), name='orders'),
    path('orders/add/', views.AddOrderView.as_view(), name='add_order'),
    path('orders/edit/<int:pk>/', views.EditOrderView.as_view(), name='edit_order'),
    path('orders/delete/<int:pk>/', views.DeleteOrderView.as_view(), name='delete_order')
]
