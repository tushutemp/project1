from django.contrib import admin
from django.urls import path,include
from.views import*
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('',home),
    path('index',views.home,name='home'),
    path('contact',views.contact,name='contact'),
    # path('forms',forms),
    path('fetch',fetch),
    path('shop/', views.shop, name='shop'),
    path('update/<int:id>',update),
    path('signup',views.signup,name='signup'),
    path('about',views.about,name='about'),
    path('cart', views.cart, name='cart'),
    path('services',views.services,name='services'),
    path('blog',views.blog,name='blog'),
    path('login',views.logins,name='login'),
    path('add_review/<int:id>/', views.add_review, name='add_review'),
    path('logout',views.logout_view,name='logout'),
    path('orders', views.orders_view, name='orders'),
    path('product_detail/<int:id>/', views.product_detail, name='product_detail'),
    path('remove_from_cart/<int:id>',remove_from_cart),
    path('checkouts/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('apply-coupon/<int:id>/', views.apply_coupon_by_id, name='apply_coupon_by_id'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('track/<str:tracking_number>/', views.track_order, name='track_order'),
    path('admin/update-status/<str:tracking_number>/', views.update_order_status, name='update_order_status'),
     path('admin/update-status/<str:tracking_number>/', views.admin_update_status, name='admin_update_status'),
]

# urlpatterns = [
#     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
#     path('product/<int:product_id>/', views.product_detail, name='product_detail'),
#     # other paths...
# ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)