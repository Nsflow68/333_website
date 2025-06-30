from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroForm, LoginForm
from .models import Usuario, Producto
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.urls import reverse
from .webpay_config import configurar_webpay
from .models import Recibo
from django.utils import timezone
from django.views.decorators.http import require_POST
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP



# ------------------- VISTAS PRINCIPALES -------------------

def index(request):
    productos = Producto.objects.all()
    return render(request, 'index.html', {'productos': productos})

def catalog(request):
    productos = Producto.objects.all()
    return render(request, 'catalog.html', {'productos': productos})

def comunity(request):
    return render(request, 'comunity.html')

# ------------------- CARRITO -------------------

def cart(request):
    carrito = request.session.get('carrito', {})
    total = 0
    carrito_actualizado = {}

    for producto_id, item in carrito.items():
        item['subtotal'] = round(item['precio'] * item['cantidad'], 2)
        item['id'] = producto_id  # para botones
        total += item['subtotal']
        carrito_actualizado[producto_id] = item

    return render(request, 'cart.html', {
        'carrito': carrito_actualizado,
        'total': total
    })

@login_required(login_url='login')
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': 1,
            'imagen': producto.imagen.url if producto.imagen else ''
        }

    request.session['carrito'] = carrito
    return redirect('cart')

@login_required(login_url='login')
def disminuir_cantidad(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] -= 1
        if carrito[str(producto_id)]['cantidad'] <= 0:
            del carrito[str(producto_id)]

    request.session['carrito'] = carrito
    return redirect('cart')

@login_required(login_url='login')
def aumentar_cantidad(request, producto_id):
    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1

    request.session['carrito'] = carrito
    return redirect('cart')

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito

    return redirect('cart')

def vaciar_carrito(request):
    request.session['carrito'] = {}
    return redirect('cart')

# ------------------- DETALLE PRODUCTO -------------------

def detalleprod(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'detalleprod.html', {'producto': producto})

# ------------------- AUTH -------------------

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.rol == 'cliente':
            return redirect('index')

    mensaje_error = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = Usuario.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('/admin/')
                    elif user.rol == 'cliente':
                        return redirect('index')
                    else:
                        mensaje_error = 'Rol no reconocido.'
                else:
                    mensaje_error = 'Contraseña incorrecta.'
            except Usuario.DoesNotExist:
                mensaje_error = 'Correo no registrado.'
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'mensaje_error': mensaje_error})

def register(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

class RegistroView(CreateView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

#----------------------TRANSBANK--------------------------


from django.http import HttpResponseServerError

@require_POST
@login_required(login_url='login')
def iniciar_pago_webpay(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        return HttpResponseServerError("El carrito está vacío.")

    total = int(sum(item['precio'] * item['cantidad'] for item in carrito.values()))
    buy_order = f"orden-{request.user.id}-{request.user.username}"
    session_id = f"session-{request.user.id}"
    return_url = request.build_absolute_uri('/retorno-webpay/')

    try:
        transaccion = configurar_webpay()
        response = transaccion.create(buy_order, session_id, total, return_url)
        return redirect(f"{response['url']}?token_ws={response['token']}")
    except Exception as e:
        return HttpResponseServerError(f"Error al iniciar transacción: {str(e)}")
    
from django.shortcuts import render, redirect
from django.urls import reverse

def retorno_webpay(request):
    token = request.GET.get('token_ws')
    if not token:
        return HttpResponseServerError("Token de Webpay no encontrado.")

    try:
        transaccion = configurar_webpay()
        response = transaccion.commit(token)

        estado = 'autorizado' if response['status'] == 'AUTHORIZED' else 'rechazado'

        if estado == 'autorizado':
            carrito = request.session.get('carrito', {})
            total = sum(item['precio'] * item['cantidad'] for item in carrito.values())

            Recibo.objects.create(
                usuario=request.user,
                fecha_emision=timezone.now(),
                total=total,
                detalles=carrito,
                token_webpay=token,
                estado=estado
            )

            request.session['carrito'] = {}

            # Redirige a la página de orden completa
            return redirect('ordencompleta')

        return render(request, 'webpay_respuesta.html', {
            'respuesta': response,
            'mensaje': '❌ Pago rechazado'
        })

    except Exception as e:
        return HttpResponseServerError(f"Error al procesar el pago: {str(e)}")

def orden_completa(request):
    recibo = Recibo.objects.filter(usuario=request.user).order_by('-fecha_emision').first()

    if not recibo:
        return HttpResponseServerError("No se encontró el recibo.")

    total = Decimal(recibo.total)
    subtotal = (total / Decimal("1.19")).quantize(Decimal("1."), rounding=ROUND_HALF_UP)
    iva = (total - subtotal).quantize(Decimal("1."), rounding=ROUND_HALF_UP)

    return render(request, 'ordencompleta.html', {
        'recibo': recibo,
        'subtotal': subtotal,
        'iva': iva,
        'total_con_iva': total
    })
