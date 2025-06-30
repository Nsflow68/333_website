# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    rol = models.CharField(max_length=30, choices=[('cliente', 'Cliente'), ('admin', 'Administrador')])

    def __str__(self):
        return f"{self.username} ({self.rol})"

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_cliente')
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} ({self.usuario.username})"

from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    categoria = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Recibo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    detalles = models.JSONField()  # Aquí se guarda el contenido del carrito como JSON
    token_webpay = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=[('autorizado', 'Autorizado'), ('rechazado', 'Rechazado')])

    def __str__(self):
        return f"Recibo #{self.id} - {self.usuario.username} - {self.estado}"

