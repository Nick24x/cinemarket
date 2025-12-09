from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Formulario de registro de usuario
class RegistroForm(UserCreationForm):
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
