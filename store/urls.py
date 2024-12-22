from turtle import home
from django.contrib import admin
from django.urls import path
from store import views
from .views import plus_cart

# from .views import home,signup,login


urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('product_details/<int:pk>', views.productdetails, name='product_details'),
    path('logout', views.logout, name='logout'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('Show_cart', views.show_cart, name='Show_cart'),
    path('plus_cart/', views.plus_cart, name='plus_cart'),
    path('minus_cart/', views.minus_cart, name='minus_cart'),
    path('remove_cart/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/', views.order, name='order'),
    path('search/', views.search, name='search'),
    path('initiate/', views.initkhalti, name="initiate"),
    path('verify/', views.verifyKhalti, name="verify")
]
