from django.contrib import admin
from .models import (
    PerfilUsuario, Servicio, Mensaje, Notificacion, Calificacion,
    Disponibilidad, HistorialServicio, TransaccionPago, Reporte,
    Favorito, DireccionGuardada, DocumentoColaborador
)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'profesion', 'rol')
    search_fields = ('user__username', 'profesion')
    list_filter = ('rol',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'publicado_por', 'fecha_servicio', 'estado')
    search_fields = ('titulo', 'descripcion', 'publicado_por__username')
    list_filter = ('categoria', 'estado')
    autocomplete_fields = ('publicado_por', 'colaborador_asignado')

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'autor', 'fecha_envio')
    search_fields = ('contenido', 'autor__username')
    list_filter = ('fecha_envio',)

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensaje', 'leida', 'fecha')
    list_filter = ('leida', 'fecha')

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'colaborador', 'empresa', 'puntuacion', 'fecha')
    list_filter = ('puntuacion', 'fecha')
    search_fields = ('servicio__titulo', 'colaborador__username', 'empresa__username', 'comentario')
    readonly_fields = ('fecha',)

@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ('colaborador', 'dia_semana', 'hora_inicio', 'hora_fin')
    list_filter = ('dia_semana',)

@admin.register(HistorialServicio)
class HistorialServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'accion', 'realizado_por', 'fecha')
    search_fields = ('accion',)

@admin.register(TransaccionPago)
class TransaccionPagoAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'pagado_por', 'recibido_por', 'monto', 'fecha_pago')
    search_fields = ('referencia',)

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'autor', 'motivo', 'resuelto', 'fecha')
    list_filter = ('resuelto',)

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'colaborador', 'fecha')

@admin.register(DireccionGuardada)
class DireccionGuardadaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'alias', 'ciudad', 'departamento')

@admin.register(DocumentoColaborador)
class DocumentoColaboradorAdmin(admin.ModelAdmin):
    list_display = ('colaborador', 'nombre', 'fecha_subida')
