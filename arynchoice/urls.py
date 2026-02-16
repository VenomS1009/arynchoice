from django.urls import path
from . import views, admin_views  # ← ДОБАВЬТЕ admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.category_list, name='categories'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('activity/<int:activity_id>/select/', views.select_activity, name='select_activity'),
    path('profile/', views.user_profile, name='profile'),
    path('my-selections/', views.my_selections, name='my_selections'),
    

    path('admin/manage-coins/', admin_views.manage_coins, name='manage_coins'),
    path('admin/add-coins-bulk/', admin_views.add_coins_bulk, name='add_coins_bulk'),

    path('earn/', views.earn_page, name='earn_page'),
    path('earn/<int:method_id>/submit/', views.submit_earn_request, name='submit_earn_request'),
    path('my-earnings/', views.my_earnings, name='my_earnings'),
]