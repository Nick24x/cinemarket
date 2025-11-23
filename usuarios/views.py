from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from peliculas.models import Pelicula
from .forms import RegistroForm
from .forms import PerfilForm
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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

@login_required
def mi_perfil(request):
    """
    Ver y editar datos básicos del usuario (username, email, etc.).
    """
    user = request.user

    if request.method == "POST":
        form = PerfilForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("mi_perfil")
    else:
        form = PerfilForm(instance=user)

    # URL interna para el botón "Cambiar contraseña"
    url_password_change = reverse("cambiar_password")

    return render(request, "usuarios/mi_perfil.html", {
        "form": form,
        "user": user,
        "url_password_change": url_password_change,
    })

@login_required
def cambiar_password(request):
    """
    Permite al usuario cambiar su contraseña.
    Al guardar, se actualiza en la BD y se mantiene la sesión.
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # 🔹 AQUÍ se guarda la nueva contraseña en la BD
            update_session_auth_hash(request, user)  # mantiene la sesión
            messages.success(request, "Tu contraseña se actualizó correctamente.")
            return redirect("mi_perfil")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "usuarios/cambiar_password.html", {
        "form": form
    })