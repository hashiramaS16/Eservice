from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Landing page
    path('login/', views.login_view, name='login'),  # Vista personalizada de login
    path('logout/', views.logout_view, name='logout'),  # Vista personalizada de logout
    path('signup/', views.signup_view, name='signup'),  # Vista personalizada de signup
    path('home/', views.home, name='home'),  # Dashboard protegido
    path('publicar/', views.publicar_servicio, name='publicar_servicio'),  # Publicar servicio
    path('buscar/', views.buscar_servicios, name='buscar_servicios'),  # Buscar servicios
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('servicio/<int:servicio_id>/', views.detalle_servicio, name='detalle_servicio'),
    path('dashboard/empresa/', views.dashboard_empresa, name='dashboard_empresa'),
    path('dashboard/colaborador/', views.dashboard_colaborador, name='dashboard_colaborador'),
    path('servicio/<int:servicio_id>/editar/', views.editar_servicio, name='editar_servicio'),
    path('servicio/<int:servicio_id>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
    path('empresa/servicio/<int:servicio_id>/', views.detalle_servicio_empresa, name='detalle_servicio_empresa'),
    path('empresa/servicio/<int:servicio_id>/asignar/', views.asignar_colaborador, name='asignar_colaborador'),
    path('servicio/<int:servicio_id>/completar/', views.marcar_completado, name='marcar_completado'),
    path('servicio/<int:servicio_id>/calificar/', views.calificar_servicio, name='calificar_servicio'),
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    path('ajax_notificaciones/', views.ajax_notificaciones, name='ajax_notificaciones'),
    path('servicio/<int:servicio_id>/postularse/', views.postularse_servicio, name='postularse_servicio'),
    path('postulacion/<int:postulacion_id>/aceptar/', views.aceptar_postulacion, name='aceptar_postulacion'),
    path('calificar/<int:postulacion_id>/', views.calificar_colaborador, name='calificar_colaborador'),
    path('dashboard/colaborador/historial/', views.historial_colaborador, name='historial_colaborador'),
    path('dashboard/empresa/historial/', views.historial_empresa, name='historial_empresa'),
    path('dashboard/colaborador/historial/pdf/', views.exportar_historial_colaborador_pdf, name='exportar_historial_colaborador_pdf'),
    path('dashboard/colaborador/historial/excel/', views.exportar_historial_colaborador_excel, name='exportar_historial_colaborador_excel'),
    path('dashboard/empresa/historial/pdf/', views.exportar_historial_empresa_pdf, name='exportar_historial_empresa_pdf'),
    path('dashboard/empresa/historial/excel/', views.exportar_historial_empresa_excel, name='exportar_historial_empresa_excel'),
    path('servicio/<int:servicio_id>/chat/', views.chat_servicio, name='chat_servicio'),
]
