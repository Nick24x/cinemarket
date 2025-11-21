from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from peliculas.models import Pelicula
from .forms import RegistroForm


def home(request):
    # trae SOLO disponibles; si quieres probar, usa .all()
    peliculas = Pelicula.objects.filter(disponible=True).order_by('-anio', 'titulo')
    return render(request, 'home.html', {'peliculas': peliculas})

# Registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})

# Iniciar sesión
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # redirige a la página principal
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

# Cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('home')