from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Formulario de registro de usuario
class RegistroForm(UserCreationForm):

    username = forms.CharField(
        max_length=10,
        label="Nombre de usuario",
        help_text="Máximo 10 caracteres",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    password1 = forms.CharField(
        max_length=15,
        label="Contraseña",
        help_text="Máximo 15 caracteres",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    password2 = forms.CharField(
        max_length=15,
        label="Confirmar contraseña",
        help_text="Máximo 15 caracteres",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(required=True, label="Correo electrónico")

    rut = forms.CharField(
        required=True,
        label="RUT",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "rut", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if len(username) > 10:
            raise forms.ValidationError("El nombre de usuario no puede tener más de 10 caracteres.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password and len(password) > 15:
            raise forms.ValidationError("La contraseña no puede tener más de 15 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.rut = self.cleaned_data["rut"]   # ← AQUÍ se guarda el rut
        if commit:
            user.save()
        return user
    
# Formulario para actualizar el perfil de usuario
class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }
    # Agregar clases CSS a los campos del formulario
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # estilos bonitos Bootstrap
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
