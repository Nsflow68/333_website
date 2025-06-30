from django.urls import path
from . import views
from .views import login_view, logout_view
from .views import iniciar_pago_webpay, retorno_webpay

urlpatterns = [
    path('', views.index, name='index'),        # http://localhost:8000/
    path('index/', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('comunity/', views.comunity, name='comunity'),
    path('cart/', views.cart, name='cart'),
    path('login/', login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('catalog/', views.catalog, name='catalog'),  # ✅ Esta es la vista correcta
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('producto/<int:producto_id>/', views.detalleprod, name='detalleprod'),
    path('aumentar/<int:producto_id>/', views.aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir/<int:producto_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    path('pago-webpay/', views.iniciar_pago_webpay, name='iniciar_pago_webpay'),
    path('retorno-webpay/', views.retorno_webpay, name='retorno_webpay'),
    path('ordencompleta/', views.orden_completa, name='ordencompleta'),

    



]

