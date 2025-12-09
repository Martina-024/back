from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# Importamos los modelos que SÍ usamos en los formularios
from .models import OfertaDeEmpleo 

# Formulario de Registro (Simplificado)
# Pide User, email, password. El perfil se crea en la vista.
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Usaremos este email para el login.")
    first_name = forms.CharField(max_length=100, required=True, label="Nombre")
    last_name = forms.CharField(max_length=100, required=True, label="Apellido")

    class Meta(UserCreationForm.Meta):
        model = User
        # ¡CORREGIDO! Quitamos password1 y password2 de esta lista.
        fields = ('username', 'email', 'first_name', 'last_name')
        help_texts = {
            'username': 'Requerido. Puedes usar un nombre de usuario único.',
        }

# Formulario para Ofertas de Empleo
# (El PerfilRegisterForm ya no se usa, lo cual está bien)
class OfertaDeEmpleoForm(forms.ModelForm):
    """
    Formulario para que los empleadores creen o editen ofertas de empleo.
    """
    class Meta:
        model = OfertaDeEmpleo
        # --- ¡CORRECCIÓN AQUÍ! ---
        # Añadimos el nuevo campo de inclusión
        fields = ['titulo', 'descripcion', 'categoria', 'es_inclusion', 'moneda', 'sueldo']        # --------------------------
        
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'titulo': 'Título del Puesto',
            'descripcion': 'Descripción del Puesto',
            'categoria': 'Categoría del Puesto',
            'sueldo': 'Sueldo (Opcional)',
            'moneda': 'Tipo de Moneda'
            # NOTA: No necesitamos 'es_inclusion' aquí.
            # El ModelForm tomará el 'verbose_name' y 'help_text' del modelo.
        }