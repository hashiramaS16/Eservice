from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario,Postulacion, Mensaje, Servicio
from allauth.account.forms import SignupForm
from .models import PerfilColaborador

class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['profesion', 'foto']
        widgets = {
            'profesion': forms.TextInput(attrs={'placeholder': 'Ej. Plomero, Jardinero...'}),
        }

# Formulario para enviar mensajes
class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Escribe tu mensaje...'}),
        }

# ✅ Nuevo: Formulario para Servicio (evita error de importación)
class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        exclude = ['publicado_por']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del servicio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe tu servicio'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad o dirección'}),
            'fecha_servicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 150000'}),
        }

# ✅ Formulario personalizado para el registro (independiente de allauth)
class CustomSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    rol = forms.ChoiceField(choices=PerfilUsuario.ROLES, label='Rol')
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Crear el perfil del usuario
            perfil = PerfilUsuario.objects.create(
                user=user,
                rol=self.cleaned_data['rol']
            )
        
        return user

# ✅ Formulario original de allauth (mantener para compatibilidad)
class AllauthSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    rol = forms.ChoiceField(choices=PerfilUsuario.ROLES, label='Rol')

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # ✅ Ya existe: accede y modifica el perfil creado automáticamente por la señal
        perfil = user.perfilusuario
        perfil.rol = self.cleaned_data['rol']
        perfil.save()

        return user

from django import forms
from django.contrib.auth.models import User
from .models import Servicio, PerfilUsuario

class AsignarColaboradorForm(forms.ModelForm):
    colaborador_asignado = forms.ModelChoiceField(
        queryset=User.objects.filter(perfilusuario__rol='colaborador'),
        required=True,
        label="Selecciona un colaborador"
    )

    class Meta:
        model = Servicio
        fields = ['colaborador_asignado']


from .models import Calificacion

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe tu comentario (opcional)...'})
        }


class PostulacionForm(forms.ModelForm):
    class Meta:
        model = Postulacion
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe un mensaje para la empresa (opcional)...'
            })
        }


from django import forms
from .models import PerfilUsuario

class DocumentosForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['cv', 'certificado']


class PerfilColaboradorForm(forms.ModelForm):
    class Meta:
        model = PerfilColaborador
        fields = ['foto', 'cv', 'certificado']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Ocultar campos si el usuario tiene rol empresa
        if user and hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'empresa':
            for field in ['hoja_de_vida', 'certificado']:
                if field in self.fields:
                    self.fields.pop(field)

    def clean_hoja_de_vida(self):
        archivo = self.cleaned_data.get('hoja_de_vida')
        if archivo:
            if not archivo.name.endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError("El archivo de la hoja de vida debe ser .pdf, .doc o .docx")
        return archivo

    def clean_certificado(self):
        archivo = self.cleaned_data.get('certificado')
        if archivo:
            if not archivo.name.endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError("El certificado debe ser .pdf, .doc o .docx")
        return archivo