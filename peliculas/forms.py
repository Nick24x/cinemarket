from django import forms
from .models import Pelicula

class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ['titulo','genero','anio','precio_arriendo','calificacion','disponible','imagen','descripcion']
        widgets = {
            # ...
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
