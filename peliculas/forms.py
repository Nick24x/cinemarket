from django import forms
from .models import Pelicula

class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = [
            "titulo",
            "genero",
            "anio",
            "precio_arriendo",
            "precio_compra",
            "disponible",
            "calificacion",
            "imagen",
            "descripcion",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "genero": forms.TextInput(attrs={"class": "form-control"}),
            "anio": forms.NumberInput(attrs={"class": "form-control", "min": 1900, "max": 2100}),
            "precio_arriendo": forms.NumberInput(
                attrs={"class": "form-control text-end", "step": "10", "min": "0"}
            ),
            "precio_compra": forms.NumberInput(
                attrs={"class": "form-control text-end", "step": "10", "min": "0"}
            ),
            "disponible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "calificacion": forms.NumberInput(
                attrs={"class": "form-control text-end", "step": "0.1", "min": "0", "max": "5"}
            ),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }