from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<int:category_id>/', views.product_list, name='category'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('search/', views.search_view, name='search'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('profile/', views.profile_view, name='profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<str:order_number>/', views.order_success, name='order_success'),
    path('orders/', views.order_history, name='order_history'),
    path('payment/', views.payment_view, name='payment'),

    path('manage/products/', views.admin_product_list, name='admin_product_list'),
    path('manage/products/<int:product_id>/edit/', views.admin_edit_product, name='admin_edit_product'),
    path('manage/products/<int:product_id>/delete/', views.admin_delete_product, name='admin_delete_product'),
    path('manage/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin/category/add/', views.admin_add_category, name='admin_add_category'),
    path('add-category/', views.admin_add_category, name='admin_add_category'),  # หน้าสำหรับเพิ่มหมวดหมู่
    path('category-list/', views.admin_category_list, name='admin_category_list'),  # หน้าสำหรับแสดงรายการหมวดหมู่
    path('edit-category/<int:category_id>/', views.admin_edit_category, name='admin_edit_category'),  # แก้ไขหมวดหมู่
    path('delete-category/<int:category_id>/', views.admin_delete_category, name='admin_delete_category'),  # ลบหมวดหมู่
    path('delete_image/<int:image_id>/', views.delete_image, name='delete_image'),

    path('manage/user-list/', views.admin_user_list, name='admin_user_list'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),\
    
    path('add-user/', views.add_user, name='add_user'),
    path('manage/orders/', views.admin_order_list, name='admin_order_list'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
