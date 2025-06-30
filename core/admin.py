from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente
from django.contrib import admin
from .models import Producto, Recibo


admin.site.register(Cliente)

# core/admin.py


admin.site.register(Producto)

admin.site.register(Recibo)



# Register your models here.
