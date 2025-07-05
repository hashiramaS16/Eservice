from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario,Postulacion, Mensaje, Servicio
from allauth.account.forms import SignupForm
from .models import PerfilColaborador
from datetime import date, datetime
from django.core.exceptions import ValidationError

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

# ✅ Formulario mejorado para Servicio
class ServicioForm(forms.ModelForm):
    # Campo de valor con formato de dinero
    valor = forms.DecimalField(
        max_digits=10, 
        decimal_places=0,
        min_value=1000,
        label='Valor del servicio (COP)',
        help_text='Ingresa el valor en pesos colombianos (mínimo $1,000)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. 150000',
            'min': '1000',
            'step': '1000',
            'style': 'font-size: 16px;'
        })
    )
    
    # Campo de fecha con calendario desplegable
    fecha_servicio = forms.DateField(
        label='Fecha del servicio',
        help_text='Selecciona una fecha futura para el servicio',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-lg',
            'min': date.today().isoformat(),
            'style': 'font-size: 16px; cursor: pointer;'
        })
    )
    
    # Campo de título mejorado
    titulo = forms.CharField(
        max_length=100,
        label='Título del servicio',
        help_text='Describe brevemente el servicio que necesitas',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. Reparación de tubería en cocina',
            'style': 'font-size: 16px;'
        })
    )
    
    # Campo de descripción mejorado
    descripcion = forms.CharField(
        label='Descripción detallada',
        help_text='Describe en detalle el servicio que necesitas',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Describe el problema específico, materiales necesarios, tiempo estimado, etc.',
            'style': 'font-size: 16px; resize: vertical;'
        })
    )
    
    # Campo de ubicación mejorado
    ubicacion = forms.CharField(
        max_length=200,
        label='Ubicación del servicio',
        help_text='Dirección exacta donde se realizará el servicio',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. Calle 123 #45-67, Barrio Centro, Bogotá',
            'style': 'font-size: 16px;'
        })
    )
    
    # Campo de categoría con más opciones
    categoria = forms.ChoiceField(
        choices=[
            ('Plomería', '🔧 Plomería'),
            ('Electricidad', '⚡ Electricidad'),
            ('Jardinería', '🌱 Jardinería'),
            ('Limpieza', '🧹 Limpieza'),
            ('Carpintería', '🔨 Carpintería'),
            ('Pintura', '🎨 Pintura'),
            ('Albañilería', '🧱 Albañilería'),
            ('Mecánica', '🔧 Mecánica'),
            ('Tecnología', '💻 Tecnología'),
            ('Otro', '📋 Otro'),
        ],
        label='Categoría del servicio',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'style': 'font-size: 16px; cursor: pointer;'
        })
    )
    
    # Campo de tipo de pago mejorado
    tipo_pago = forms.ChoiceField(
        choices=[
            ('Efectivo', '💵 Efectivo'),
            ('Transferencia', '🏦 Transferencia bancaria'),
            ('Nequi', '📱 Nequi'),
            ('Daviplata', '📱 Daviplata'),
            ('Otro', '💳 Otro método'),
        ],
        label='Método de pago',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'style': 'font-size: 16px; cursor: pointer;'
        })
    )
    
    # Nuevo campo: urgencia del servicio
    urgencia = forms.ChoiceField(
        choices=[
            ('baja', '🟢 Baja - Puede esperar'),
            ('media', '🟡 Media - En los próximos días'),
            ('alta', '🔴 Alta - Lo antes posible'),
        ],
        label='Nivel de urgencia',
        initial='media',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'style': 'font-size: 16px; cursor: pointer;'
        })
    )
    
    # Nuevo campo: horario preferido
    horario_preferido = forms.ChoiceField(
        choices=[
            ('manana', '🌅 Mañana (8:00 AM - 12:00 PM)'),
            ('tarde', '☀️ Tarde (1:00 PM - 6:00 PM)'),
            ('noche', '🌙 Noche (6:00 PM - 9:00 PM)'),
            ('flexible', '🕐 Horario flexible'),
        ],
        label='Horario preferido',
        initial='tarde',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'style': 'font-size: 16px; cursor: pointer;'
        })
    )

    class Meta:
        model = Servicio
        exclude = ['publicado_por', 'colaborador_asignado', 'estado']
        fields = ['titulo', 'descripcion', 'categoria', 'ubicacion', 'fecha_servicio', 'tipo_pago', 'valor', 'urgencia', 'horario_preferido']

    def clean_fecha_servicio(self):
        fecha = self.cleaned_data.get('fecha_servicio')
        if fecha:
            if fecha < date.today():
                raise ValidationError('❌ La fecha del servicio no puede ser anterior a hoy.')
            if fecha > date.today().replace(year=date.today().year + 1):
                raise ValidationError('❌ La fecha del servicio no puede ser más de un año en el futuro.')
        return fecha

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor:
            if valor < 1000:
                raise ValidationError('❌ El valor mínimo del servicio es $1,000 COP.')
            if valor > 10000000:
                raise ValidationError('❌ El valor máximo del servicio es $10,000,000 COP.')
        return valor

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo:
            if len(titulo.strip()) < 10:
                raise ValidationError('❌ El título debe tener al menos 10 caracteres.')
            if len(titulo) > 100:
                raise ValidationError('❌ El título no puede exceder 100 caracteres.')
        return titulo.strip()

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion:
            if len(descripcion.strip()) < 20:
                raise ValidationError('❌ La descripción debe tener al menos 20 caracteres.')
            if len(descripcion) > 1000:
                raise ValidationError('❌ La descripción no puede exceder 1000 caracteres.')
        return descripcion.strip()

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get('ubicacion')
        if ubicacion:
            if len(ubicacion.strip()) < 10:
                raise ValidationError('❌ La ubicación debe tener al menos 10 caracteres.')
        return ubicacion.strip()

    def format_valor(self):
        """Formatea el valor para mostrar con separadores de miles"""
        valor = self.cleaned_data.get('valor')
        if valor:
            return f"${valor:,.0f} COP"
        return ""

# ✅ Formulario personalizado para el registro (independiente de allauth)
class CustomSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='Nombre', required=True)
    last_name = forms.CharField(max_length=30, label='Apellido', required=True)
    rol = forms.ChoiceField(choices=PerfilUsuario.ROLES, label='Rol', required=True)
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Crear el perfil del usuario directamente
            PerfilUsuario.objects.create(
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