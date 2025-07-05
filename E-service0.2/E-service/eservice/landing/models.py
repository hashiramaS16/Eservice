from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ---------------------------
# PERFIL DE USUARIO
# ---------------------------
class PerfilUsuario(models.Model):
    ROLES = (
        ('empresa', 'Empresa'),
        ('colaborador', 'Colaborador'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profesion = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='colaborador')
    cv = models.FileField(upload_to='documentos/hojas_de_vida/', null=True, blank=True)
    certificado = models.FileField(upload_to='documentos/certificados/', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.rol}'
    

class PerfilColaborador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    cv = models.FileField(upload_to='documentos/hojas_de_vida/', null=True, blank=True)
    certificado = models.FileField(upload_to='documentos/certificados/', null=True, blank=True)

    def __str__(self):
        return self.user.username



# ---------------------------
# SERVICIOS PUBLICADOS
# ---------------------------
class Servicio(models.Model):
    CATEGORIAS = [
        ('Plomería', 'Plomería'),
        ('Electricidad', 'Electricidad'),
        ('Jardinería', 'Jardinería'),
        ('Limpieza', 'Limpieza'),
        ('Carpintería', 'Carpintería'),
        ('Pintura', 'Pintura'),
        ('Albañilería', 'Albañilería'),
        ('Mecánica', 'Mecánica'),
        ('Tecnología', 'Tecnología'),
        ('Otro', 'Otro'),
    ]

    TIPOS_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia bancaria'),
        ('Nequi', 'Nequi'),
        ('Daviplata', 'Daviplata'),
        ('Otro', 'Otro método'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('completado', 'Completado'),
    ]

    URGENCIAS = [
        ('baja', 'Baja - Puede esperar'),
        ('media', 'Media - En los próximos días'),
        ('alta', 'Alta - Lo antes posible'),
    ]

    HORARIOS = [
        ('manana', 'Mañana (8:00 AM - 12:00 PM)'),
        ('tarde', 'Tarde (1:00 PM - 6:00 PM)'),
        ('noche', 'Noche (6:00 PM - 9:00 PM)'),
        ('flexible', 'Horario flexible'),
    ]

    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    publicado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='servicios_publicados')
    fecha_servicio = models.DateField()
    colaborador_asignado = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='servicios_asignados')
    tipo_pago = models.CharField(max_length=20, choices=TIPOS_PAGO)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    ubicacion = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    urgencia = models.CharField(max_length=20, choices=URGENCIAS, default='media')
    horario_preferido = models.CharField(max_length=20, choices=HORARIOS, default='tarde')
    fecha_publicacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titulo

    def get_valor_formateado(self):
        """Retorna el valor formateado con separadores de miles"""
        return f"${self.valor:,.0f} COP"

    def get_urgencia_icon(self):
        """Retorna el icono de urgencia"""
        icons = {
            'baja': '🟢',
            'media': '🟡',
            'alta': '🔴'
        }
        return icons.get(self.urgencia, '⚪')

    def get_horario_icon(self):
        """Retorna el icono de horario"""
        icons = {
            'manana': '🌅',
            'tarde': '☀️',
            'noche': '🌙',
            'flexible': '🕐'
        }
        return icons.get(self.horario_preferido, '🕐')


# ---------------------------
# MENSAJES EN SERVICIOS
# ---------------------------
class Mensaje(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Mensaje de {self.autor.username} para {self.servicio.titulo}"


# ---------------------------
# NOTIFICACIONES
# ---------------------------
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notificación para {self.usuario.username}: {self.mensaje}'


# ---------------------------
# CALIFICACIÓN DE SERVICIO
# ---------------------------
class Calificacion(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calificaciones_recibidas')
    empresa = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calificaciones_dadas')
    puntuacion = models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=5)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calificación de {self.empresa.username} a {self.colaborador.username}: {self.puntuacion} estrellas"


# ---------------------------
# DISPONIBILIDAD DE COLABORADORES
# ---------------------------
class Disponibilidad(models.Model):
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.CharField(max_length=10, choices=[
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado'), ('Domingo', 'Domingo')
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.colaborador.username} - {self.dia_semana}: {self.hora_inicio} a {self.hora_fin}"


# ---------------------------
# HISTORIAL DE CAMBIOS EN SERVICIOS
# ---------------------------
class HistorialServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='historial')
    accion = models.CharField(max_length=100)
    realizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.servicio.titulo} - {self.accion} en {self.fecha}"


# ---------------------------
# TRANSACCIONES DE PAGO
# ---------------------------
class TransaccionPago(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    pagado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos_realizados')
    recibido_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos_recibidos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=100)

    def __str__(self):
        return f"Pago de {self.pagado_por.username} a {self.recibido_por.username} - ${self.monto}"


# ---------------------------
# REPORTES O RECLAMOS
# ---------------------------
class Reporte(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    resuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"Reporte de {self.autor.username} sobre {self.servicio.titulo}"


# ---------------------------
# FAVORITOS (COLABORADORES PREFERIDOS)
# ---------------------------
class Favorito(models.Model):
    empresa = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marcado_como_favorito')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empresa.username} ❤️ {self.colaborador.username}"


# ---------------------------
# DIRECCIONES GUARDADAS
# ---------------------------
class DireccionGuardada(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=50)
    departamento = models.CharField(max_length=50)
    coordenadas = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.alias} - {self.usuario.username}"


# ---------------------------
# DOCUMENTOS ADJUNTOS
# ---------------------------
class DocumentoColaborador(models.Model):
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='documentos_colaboradores/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.colaborador.username} - {self.nombre}"

class Postulacion(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='postulaciones')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postulaciones')
    mensaje = models.TextField(blank=True, null=True)  # opcional: mensaje del colaborador al postularse
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ], default='pendiente')

    class Meta:
        unique_together = ('servicio', 'colaborador')  # Evita postulaciones duplicadas

    def __str__(self):
        return f"{self.colaborador.username} postuló a {self.servicio.titulo}"


class ChatMensaje(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    remitente = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
