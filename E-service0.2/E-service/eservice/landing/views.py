from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseForbidden
from django.db.models import Q 
from .models import Servicio, PerfilUsuario, Mensaje
from .forms import PerfilForm, MensajeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Servicio
from .decorators import solo_rol_empresa
from django.contrib.auth.models import User
from .models import Servicio, Calificacion
from .forms import CalificacionForm
from django.core.exceptions import ObjectDoesNotExist
from .models import Notificacion
from django.db.models import Avg
from django.http import JsonResponse
from .models import Notificacion
from django.contrib.auth.decorators import login_required
from .models import Postulacion
from .forms import PostulacionForm
from .forms import DocumentosForm
from .models import ChatMensaje
from .models import PerfilColaborador
from .forms import PerfilColaboradorForm
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
import tempfile
import openpyxl
from xhtml2pdf import pisa
from io import BytesIO
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Vista para mostrar perfil del usuario (solo usuario logueado)
@login_required
def perfil_usuario(request):
    perfil, creado = PerfilUsuario.objects.get_or_create(user=request.user)
    return render(request, 'landing/perfil.html', {'perfil': perfil})

# Vista pública de inicio (landing page)
def inicio(request):
    return render(request, 'landing/index.html')

# Vista de login personalizado
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            perfil = PerfilUsuario.objects.get(user=user)
            if perfil.rol == 'empresa':
                messages.success(request, '🎉 ¡Bienvenido de vuelta! Has iniciado sesión como empresa.')
            else:
                messages.success(request, '🎉 ¡Bienvenido de vuelta! Has iniciado sesión como colaborador.')
            return redirect('home')  # Dashboard tras login exitoso
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos. Por favor, verifica tus credenciales.')

    return render(request, 'landing/login.html')

# Vista de logout personalizado
def logout_view(request):
    logout(request)
    messages.success(request, '👋 ¡Has cerrado sesión correctamente! Gracias por usar E-Services.')
    return redirect('inicio')

# Vista de signup personalizado
def signup_view(request):
    from .forms import CustomSignupForm
    
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                rol = form.cleaned_data['rol']
                
                if rol == 'empresa':
                    messages.success(request, '🎉 ¡Registro exitoso! Bienvenido a E-Services como empresa. Ya puedes publicar servicios y encontrar colaboradores.')
                else:
                    messages.success(request, '🎉 ¡Registro exitoso! Bienvenido a E-Services como colaborador. Ya puedes buscar servicios y postularte.')
                
                return redirect('home')
            except Exception as e:
                messages.error(request, f'❌ Error durante el registro: {str(e)}')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    if 'email' in field.lower():
                        messages.error(request, f'📧 Error en correo electrónico: {error}')
                    elif 'username' in field.lower():
                        messages.error(request, f'👤 Error en nombre de usuario: {error}')
                    elif 'password' in field.lower():
                        messages.error(request, f'🔒 Error en contraseña: {error}')
                    else:
                        messages.error(request, f'⚠️ Error en {field}: {error}')
    else:
        form = CustomSignupForm()
    
    return render(request, 'account/signup.html', {'form': form})

# Vista protegida: dashboard principal
@login_required
def home(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    
    # Calcular estadísticas según el rol del usuario
    if perfil.rol == 'empresa':
        # Estadísticas para empresas
        servicios_activos = Servicio.objects.filter(
            publicado_por=request.user,
            colaborador_asignado__isnull=True
        ).count()
        
        servicios_completados = Servicio.objects.filter(
            publicado_por=request.user,
            estado='completado'
        ).count()
        
        colaboradores_activos = User.objects.filter(
            perfilusuario__rol='colaborador'
        ).count()
        
        # Calificación promedio de los servicios de la empresa (si tiene calificaciones)
        calificacion_promedio = 0
        try:
            calificaciones = Calificacion.objects.filter(
                servicio__publicado_por=request.user
            )
            if calificaciones.exists():
                calificacion_promedio = calificaciones.aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
        except Exception as e:
            print(f"Error al obtener calificaciones de empresa: {e}")
    
    else:  # colaborador
        # Estadísticas para colaboradores
        servicios_activos = Servicio.objects.filter(
            colaborador_asignado=request.user,
            estado='en_progreso'
        ).count()
        
        servicios_completados = Servicio.objects.filter(
            colaborador_asignado=request.user,
            estado='completado'
        ).count()
        
        colaboradores_activos = User.objects.filter(
            perfilusuario__rol='colaborador'
        ).count()
        
        # Calificación promedio del colaborador (igual que en dashboard)
        calificacion_promedio = 0
        try:
            calificaciones = Calificacion.objects.filter(colaborador=request.user)
            if calificaciones.exists():
                calificacion_promedio = calificaciones.aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
        except Exception as e:
            print(f"Error al obtener calificaciones de colaborador: {e}")
    
    return render(request, 'landing/home.html', {
        'servicios_activos': servicios_activos,
        'servicios_completados': servicios_completados,
        'colaboradores_activos': colaboradores_activos,
        'calificacion_promedio': calificacion_promedio,
    })

def lista_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'landing/lista_servicios.html', {'servicios': servicios})

def crear_notificacion(usuario, mensaje, url=None):
    from .models import Notificacion
    Notificacion.objects.create(usuario=usuario, mensaje=mensaje, url=url)

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    # Redirigir a la url relacionada si existe, o a dashboard
    if notificacion.url:
        return redirect(notificacion.url)
    return redirect('dashboard_empresa' if PerfilUsuario.objects.get(user=request.user).rol == 'empresa' else 'dashboard_colaborador')

# Formulario para publicar servicio
class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['titulo', 'descripcion', 'categoria', 'ubicacion', 'fecha_servicio', 'tipo_pago', 'valor']

# Vista para publicar servicio: SOLO empresas pueden publicar
@login_required
def publicar_servicio(request):
    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != 'empresa':
        return HttpResponseForbidden("")  # Solo empresas

    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.publicado_por = request.user
            servicio.save()
            messages.success(request, '🚀 ¡Servicio publicado exitosamente! Los colaboradores ya pueden ver tu oferta.')
            return redirect('buscar_servicios')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario.')
    else:
        form = ServicioForm()

    return render(request, 'landing/publicar.html', {'form': form})

# Vista para buscar servicios (pública)
def buscar_servicios(request):
    query = request.GET.get('q', '')
    if query:
        servicios = Servicio.objects.filter(
            Q(titulo__icontains=query) |
            Q(categoria__icontains=query) |
            Q(ubicacion__icontains=query),
            colaborador_asignado__isnull=True  # Solo mostrar servicios sin colaborador asignado
        )
    else:
        servicios = Servicio.objects.filter(colaborador_asignado__isnull=True)  # Solo mostrar servicios sin colaborador asignado

    return render(request, 'landing/buscar.html', {'servicios': servicios, 'query': query})

# views.py
@login_required
def editar_perfil(request):
    perfil = PerfilUsuario.objects.get(user=request.user)

    if request.method == 'POST':
        form = PerfilColaboradorForm(request.POST, request.FILES, instance=perfil, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ ¡Perfil actualizado correctamente! Los cambios se han guardado.")
            return redirect('editar_perfil')
        else:
            messages.error(request, "❌ Por favor corrige los errores en el formulario.")
    else:
        form = PerfilColaboradorForm(instance=perfil, user=request.user)

    return render(request, 'landing/editar_perfil.html', {
        'form': form,
        'perfil': perfil
    })

# Vista detalle de un servicio: SOLO colaboradores pueden comentar
@login_required
def detalle_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    mensajes = Mensaje.objects.filter(servicio=servicio).order_by('-fecha_envio')

    if request.method == 'POST' and 'contenido' in request.POST:
        form = MensajeForm(request.POST)
        if form.is_valid():
            nuevo_mensaje = form.save(commit=False)
            nuevo_mensaje.servicio = servicio
            nuevo_mensaje.autor = request.user
            nuevo_mensaje.save()
    else:
        form = MensajeForm()

    postulaciones = Postulacion.objects.filter(servicio=servicio)

    # Obtener o crear el perfil del usuario
    perfil, creado = PerfilUsuario.objects.get_or_create(user=request.user)
    
    # Determinar si el usuario ya se postuló (solo si es colaborador)
    ya_postulado = False
    if perfil.rol == 'colaborador':
        ya_postulado = Postulacion.objects.filter(servicio=servicio, colaborador=request.user).exists()

    return render(request, 'landing/detalle_servicio.html', {
        'servicio': servicio,
        'mensajes': mensajes,
        'form': form,
        'postulaciones': postulaciones,
        'ya_postulado': ya_postulado,
        'perfil': perfil,  # Pasar el perfil al template
    })

@login_required
def dashboard_empresa(request):
    perfil = get_object_or_404(PerfilUsuario, user=request.user)
    if perfil.rol != 'empresa':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    servicios = Servicio.objects.filter(publicado_por=request.user).order_by('-fecha_servicio')
    colaboradores = User.objects.filter(perfilusuario__rol='colaborador')
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha')

    # Agregar postulaciones agrupadas por servicio
    postulaciones_por_servicio = {
        servicio.id: Postulacion.objects.filter(servicio=servicio, estado='pendiente')
        for servicio in servicios
    }

    # Calcular estadísticas
    servicios_activos = servicios.filter(colaborador_asignado__isnull=True).count()
    servicios_en_progreso = servicios.filter(estado='en_progreso').count()
    servicios_completados = servicios.filter(estado='completado').count()
    
    # Calcular calificación promedio de los servicios de la empresa
    calificacion_promedio = 0
    try:
        calificaciones = Calificacion.objects.filter(servicio__publicado_por=request.user)
        if calificaciones.exists():
            calificacion_promedio = calificaciones.aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
    except Exception as e:
        print(f"Error al obtener calificaciones de empresa: {e}")

    return render(request, 'landing/dashboard_empresa.html', {
        'servicios': servicios,
        'colaboradores': colaboradores,
        'notificaciones': notificaciones,
        'postulaciones_por_servicio': postulaciones_por_servicio,
        'servicios_activos': servicios_activos,
        'servicios_en_progreso': servicios_en_progreso,
        'servicios_completados': servicios_completados,
        'calificacion_promedio': calificacion_promedio,
    })

@login_required
def dashboard_colaborador(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'colaborador':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    # Servicios asignados al colaborador
    servicios_asignados = Servicio.objects.filter(colaborador_asignado=request.user).order_by('-fecha_servicio')

    # Notificaciones no leídas
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha')

    # Inicializar promedio
    promedio = 0
    calificaciones = []

    try:
        # Intentar obtener las calificaciones
        calificaciones = Calificacion.objects.filter(colaborador=request.user).order_by('-fecha')
        
        if calificaciones.exists():
            # Calcular el promedio de todas las calificaciones
            promedio = calificaciones.aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
    except Exception as e:
        print(f"Error al obtener calificaciones: {e}")

    return render(request, 'landing/dashboard_colaborador.html', {
        'servicios_asignados': servicios_asignados,
        'notificaciones': notificaciones,
        'calificaciones': calificaciones,
        'promedio': promedio,
        'calificacion_promedio': promedio  # Agregar para consistencia con home
    })
@login_required
def editar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id, publicado_por=request.user)
    
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('dashboard_empresa')
    else:
        form = ServicioForm(instance=servicio)
    
    return render(request, 'landing/editar_servicio.html', {'form': form})

@login_required
def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id, publicado_por=request.user)
    
    if request.method == 'POST':
        servicio.delete()
        return redirect('dashboard_empresa')
    
    return render(request, 'landing/confirmar_eliminar_servicio.html', {'servicio': servicio})

@login_required
def detalle_servicio_empresa(request, servicio_id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'empresa':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    servicio = get_object_or_404(Servicio, id=servicio_id, publicado_por=request.user)
    mensajes = Mensaje.objects.filter(servicio=servicio).order_by('-fecha_envio')

    return render(request, 'landing/detalle_servicio_empresa.html', {
        'servicio': servicio,
        'mensajes': mensajes
    })
    

@login_required
def asignar_colaborador(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        colaborador_id = request.POST.get('colaborador')
        if colaborador_id:
            colaborador = User.objects.get(id=colaborador_id)
            servicio.colaborador_asignado = colaborador
            servicio.save()

    return redirect('dashboard_empresa')  # O la url que corresponda

@login_required
def marcar_completado(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    perfil = PerfilUsuario.objects.get(user=request.user)

    # Verificar que el usuario es la empresa que publicó o el colaborador asignado
    if request.user != servicio.publicado_por and request.user != servicio.colaborador_asignado:
        messages.error(request, "No tienes permiso para completar este servicio.")
        return redirect('dashboard_empresa' if perfil.rol == 'empresa' else 'dashboard_colaborador')

    # Verificar que el servicio está en progreso
    if servicio.estado != 'en_progreso':
        messages.error(request, "Solo se pueden completar servicios en progreso.")
        return redirect('dashboard_empresa' if perfil.rol == 'empresa' else 'dashboard_colaborador')

    if request.method == 'POST':
        servicio.estado = 'completado'
        servicio.save()

        # Crear notificación para el otro usuario
        if perfil.rol == 'empresa':
            Notificacion.objects.create(
                usuario=servicio.colaborador_asignado,
                mensaje=f'El servicio "{servicio.titulo}" ha sido marcado como completado por la empresa.',
                url=f'/servicio/{servicio.id}/'
            )
        else:
            Notificacion.objects.create(
                usuario=servicio.publicado_por,
                mensaje=f'El servicio "{servicio.titulo}" ha sido marcado como completado por el colaborador.',
                url=f'/servicio/{servicio.id}/'
            )

        messages.success(request, "Servicio marcado como completado correctamente.")
        return redirect('dashboard_empresa' if perfil.rol == 'empresa' else 'dashboard_colaborador')

    return render(request, 'landing/confirmar_completar_servicio.html', {
        'servicio': servicio,
        'es_empresa': perfil.rol == 'empresa'
    })

@login_required
def calificar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    perfil = PerfilUsuario.objects.get(user=request.user)

    if perfil.rol != 'empresa' or servicio.estado != 'completado' or servicio.publicado_por != request.user:
        return HttpResponseForbidden("No tienes permiso para calificar este servicio.")

    # Verificar si ya existe calificación
    if Calificacion.objects.filter(servicio=servicio).exists():
        messages.info(request, "Este servicio ya fue calificado.")
        return redirect('dashboard_empresa')

    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.servicio = servicio
            calificacion.empresa = request.user
            calificacion.colaborador = servicio.colaborador_asignado
            calificacion.save()
            
            # Crear notificación para el colaborador
            Notificacion.objects.create(
                usuario=servicio.colaborador_asignado,
                mensaje=f'Has recibido una calificación de {calificacion.puntuacion} estrellas por tu servicio en {servicio.titulo}',
                url=f'/dashboard/colaborador/'
            )
            
            messages.success(request, "Calificación enviada correctamente.")
            return redirect('dashboard_empresa')
    else:
        form = CalificacionForm()

    return render(request, 'landing/calificar_servicio.html', {'form': form, 'servicio': servicio})


@login_required
def ajax_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha')
    data = []

    for noti in notificaciones:
        data.append({
            'id': noti.id,
            'mensaje': noti.mensaje,
            'url': noti.url or '',
        })

        # Marca como leída para no volver a mostrarla
        noti.leida = True
        noti.save()

    return JsonResponse({'notificaciones': data})


@login_required
def postularse_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    perfil = PerfilUsuario.objects.get(user=request.user)
    
    # Verifica que sea colaborador
    if perfil.rol != 'colaborador':
        messages.error(request, '❌ Solo colaboradores pueden postularse a servicios.')
        return redirect('detalle_servicio', servicio_id=servicio_id)

    # Verifica que no esté ya postulado
    if Postulacion.objects.filter(servicio=servicio, colaborador=request.user).exists():
        messages.info(request, 'ℹ️ Ya te has postulado a este servicio. Espera la respuesta de la empresa.')
        return redirect('detalle_servicio', servicio_id=servicio_id)

    if request.method == 'POST':
        form = PostulacionForm(request.POST)
        if form.is_valid():
            postulacion = form.save(commit=False)
            postulacion.servicio = servicio
            postulacion.colaborador = request.user
            postulacion.save()
            
            # Crear notificación para la empresa
            crear_notificacion(
                usuario=servicio.publicado_por,
                mensaje=f'Nueva postulación de {request.user.username} para el servicio: {servicio.titulo}',
                url=f'/ver-postulaciones/{servicio.id}/'
            )
            
            messages.success(request, '🎯 ¡Postulación enviada exitosamente! La empresa revisará tu solicitud.')
            return redirect('detalle_servicio', servicio_id=servicio_id)
    else:
        form = PostulacionForm()

    return render(request, 'landing/postular_servicio.html', {
        'form': form,
        'servicio': servicio
    })

@login_required
def aceptar_postulacion(request, postulacion_id):
    postulacion = get_object_or_404(Postulacion, id=postulacion_id)
    servicio = postulacion.servicio
    
    # Verificar que el usuario sea la empresa que publicó el servicio
    if request.user != servicio.publicado_por:
        messages.error(request, '❌ No tienes permiso para realizar esta acción.')
        return redirect('dashboard_empresa')

    # Verificar que el servicio no tenga ya un colaborador asignado
    if servicio.colaborador_asignado:
        messages.error(request, '❌ Este servicio ya tiene un colaborador asignado.')
        return redirect('dashboard_empresa')

    # Actualizar el estado de la postulación
    postulacion.estado = 'aceptada'
    postulacion.save()

    # Actualizar el servicio
    servicio.estado = 'en_progreso'
    servicio.colaborador_asignado = postulacion.colaborador
    servicio.save()

    # Crear notificación para el colaborador
    Notificacion.objects.create(
        usuario=postulacion.colaborador,
        mensaje=f'Tu postulación para el servicio "{servicio.titulo}" ha sido aceptada.',
        url=f'/servicio/{servicio.id}/'
    )

    # Rechazar otras postulaciones pendientes
    Postulacion.objects.filter(
        servicio=servicio,
        estado='pendiente'
    ).exclude(id=postulacion.id).update(estado='rechazada')

    messages.success(request, f'✅ ¡Has aceptado la postulación de {postulacion.colaborador.get_full_name()}! El servicio está en progreso.')
    return redirect('dashboard_empresa')

@login_required
def subir_documentos(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if request.method == 'POST':
        form = DocumentosForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, '📄 ¡Documentos actualizados correctamente! Tu perfil está más completo.')
            return redirect('perfil')
        else:
            messages.error(request, '❌ Error al subir los documentos. Verifica el formato de los archivos.')
    else:
        form = DocumentosForm(instance=perfil)
    return render(request, 'subir_documentos.html', {'form': form})

@login_required
def ver_postulaciones(request, servicio_id):
    servicio = Servicio.objects.get(id=servicio_id)
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil != servicio.empresa:
        messages.error(request, '❌ No tienes autorización para ver estas postulaciones.')
        return redirect('dashboard_empresa')
    postulaciones = Postulacion.objects.filter(servicio=servicio, estado='pendiente')
    return render(request, 'ver_postulaciones.html', {'postulaciones': postulaciones, 'servicio': servicio})


@login_required
def chat_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    perfil = PerfilUsuario.objects.get(user=request.user)
    if not (servicio.colaborador_asignado == request.user or servicio.publicado_por == request.user):
        return HttpResponseForbidden("No tienes permiso para acceder a este chat.")
    if not servicio.colaborador_asignado:
        return HttpResponseForbidden("El chat solo está disponible cuando hay un colaborador asignado.")
    mensajes = Mensaje.objects.filter(servicio=servicio).order_by('fecha_envio')
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.servicio = servicio
            mensaje.autor = request.user
            mensaje.save()
            # Notificación en tiempo real (desactivada temporalmente)
            # channel_layer = get_channel_layer()
            # destinatario = servicio.publicado_por if request.user == servicio.colaborador_asignado else servicio.colaborador_asignado
            # async_to_sync(channel_layer.group_send)(
            #     f'notificaciones_{destinatario.id}',
            #     {
            #         'type': 'send_notificacion',
            #         'data': {
            #             'mensaje': f'Nuevo mensaje en el chat del servicio "{servicio.titulo}"',
            #             'servicio_id': servicio.id,
            #             'remitente': request.user.get_full_name() or request.user.username
            #         }
            #     }
            # )
            return redirect('chat_servicio', servicio_id=servicio.id)
    else:
        form = MensajeForm()
    return render(request, 'landing/chat_servicio.html', {
        'servicio': servicio,
        'mensajes': mensajes,
        'form': form
    })

@login_required
def calificar_colaborador(request, postulacion_id):
    postulacion = get_object_or_404(Postulacion, id=postulacion_id)
    
    # Verificar que el usuario es la empresa que contrató al colaborador
    if request.user != postulacion.servicio.empresa:
        messages.error(request, '❌ No tienes permiso para calificar este servicio.')
        return redirect('dashboard_empresa')
    
    # Verificar que el servicio está completado
    if postulacion.estado != 'completado':
        messages.error(request, '❌ Solo puedes calificar servicios completados.')
        return redirect('dashboard_empresa')
    
    # Verificar si ya existe una calificación
    if Calificacion.objects.filter(servicio=postulacion.servicio, colaborador=postulacion.colaborador).exists():
        messages.error(request, '❌ Ya has calificado este servicio.')
        return redirect('dashboard_empresa')
    
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.servicio = postulacion.servicio
            calificacion.colaborador = postulacion.colaborador
            calificacion.empresa = request.user
            calificacion.fecha = timezone.now()
            calificacion.save()
            
            # Crear notificación para el colaborador
            Notificacion.objects.create(
                usuario=postulacion.colaborador,
                mensaje=f'Has recibido una calificación de {calificacion.promedio} estrellas por tu servicio en {postulacion.servicio.titulo}',
                tipo='calificacion'
            )
            
            messages.success(request, '⭐ ¡Calificación enviada con éxito! Gracias por tu feedback.')
            return redirect('dashboard_empresa')
        else:
            messages.error(request, '❌ Error al enviar la calificación. Por favor, intenta de nuevo.')
    else:
        form = CalificacionForm()
    
    return render(request, 'landing/calificar_servicio.html', {
        'form': form,
        'postulacion': postulacion,
        'servicio': postulacion.servicio,
        'colaborador': postulacion.colaborador
    })

@login_required
def historial_colaborador(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'colaborador':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    servicios = Servicio.objects.filter(colaborador_asignado=request.user).order_by('-fecha_servicio')
    return render(request, 'landing/historial_colaborador.html', {
        'servicios': servicios
    })

@login_required
def historial_empresa(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'empresa':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    servicios = Servicio.objects.filter(publicado_por=request.user).order_by('-fecha_servicio')
    return render(request, 'landing/historial_empresa.html', {
        'servicios': servicios
    })

@login_required
def exportar_historial_colaborador_pdf(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'colaborador':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    servicios = Servicio.objects.filter(colaborador_asignado=request.user).order_by('-fecha_servicio')
    html_string = render_to_string('landing/historial_colaborador_pdf.html', {'servicios': servicios, 'user': request.user})
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode('utf-8')), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="historial_servicios_colaborador.pdf"'
        return response
    return HttpResponse('Error al generar el PDF', status=500)

@login_required
def exportar_historial_colaborador_excel(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'colaborador':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    servicios = Servicio.objects.filter(colaborador_asignado=request.user).order_by('-fecha_servicio')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Servicios"
    ws.append(["Título", "Empresa", "Fecha", "Ubicación", "Estado", "Calificación", "Comentario"])
    for servicio in servicios:
        calificacion = servicio.calificacion_set.first()
        ws.append([
            servicio.titulo,
            servicio.publicado_por.get_full_name() or servicio.publicado_por.username,
            servicio.fecha_servicio.strftime('%d/%m/%Y'),
            servicio.ubicacion,
            servicio.get_estado_display(),
            calificacion.puntuacion if calificacion else '',
            calificacion.comentario if calificacion else ''
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="historial_servicios_colaborador.xlsx"'
    wb.save(response)
    return response

@login_required
def exportar_historial_empresa_pdf(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'empresa':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    servicios = Servicio.objects.filter(publicado_por=request.user).order_by('-fecha_servicio')
    html_string = render_to_string('landing/historial_empresa_pdf.html', {'servicios': servicios, 'user': request.user})
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode('utf-8')), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="historial_servicios_empresa.pdf"'
        return response
    return HttpResponse('Error al generar el PDF', status=500)

@login_required
def exportar_historial_empresa_excel(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != 'empresa':
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    servicios = Servicio.objects.filter(publicado_por=request.user).order_by('-fecha_servicio')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Servicios"
    ws.append(["Título", "Colaborador", "Fecha", "Ubicación", "Estado", "Calificación", "Comentario"])
    for servicio in servicios:
        calificacion = servicio.calificacion_set.first()
        colaborador = servicio.colaborador_asignado.get_full_name() if servicio.colaborador_asignado else 'Sin asignar'
        ws.append([
            servicio.titulo,
            colaborador,
            servicio.fecha_servicio.strftime('%d/%m/%Y'),
            servicio.ubicacion,
            servicio.get_estado_display(),
            calificacion.puntuacion if calificacion else '',
            calificacion.comentario if calificacion else ''
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="historial_servicios_empresa.xlsx"'
    wb.save(response)
    return response
