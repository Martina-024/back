from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, OfertaDeEmpleoForm
# --- ¡ACTUALIZADO! ---
# Importamos todos los modelos que necesitamos
from .models import OfertaDeEmpleo, Perfil, Solicitud, Mensaje
from django.contrib import messages 
from django.db import IntegrityError # Para manejar postulaciones duplicadas
# --- ¡NUEVO! ---
# Para consultas complejas (OR)
from django.db.models import Q 


# -----------------------------------------------------------------
# VISTA DE INICIO (HOME)
# -----------------------------------------------------------------
@login_required # ¡Protegemos la home!
def home_view(request):
    """
    Vista de inicio.
    - Redirige a elegir rol si el perfil está "pendiente".
    - Muestra el dashboard correcto según el tipo de perfil.
    """
    
    # 1. Comprobar si es admin/superuser (no tienen perfil)
    if request.user.is_staff:
        context = {'mensaje': 'Bienvenido/a, Admin.'}
        return render(request, 'jobswipe/home.html', context)

    # 2. Si no es admin, es un usuario normal. Comprobar su perfil.
    try:
        perfil = request.user.perfil 
        
        # --- NUEVA LÓGICA DE ONBOARDING ---
        # 3. Si el perfil está "pendiente", forzar elección de rol.
        if perfil.tipo == 'pendiente':
            messages.info(request, '¡Bienvenido/a! Por favor, completa tu perfil para continuar.')
            return redirect('elegir_rol')
        
        # 4. Si el perfil ya está completo (candidato o empleador)
        elif perfil.tipo == 'candidato':
            # --- LÓGICA DEL CANDIDATO ---
            
            # Obtener IDs de ofertas a las que ya postuló
            ofertas_postuladas_ids = Solicitud.objects.filter(
                User_candidato=request.user
            ).values_list('oferta_id', flat=True)

            # Buscamos ofertas activas, EXCLUYENDO las que ya postuló
            ofertas_activas = OfertaDeEmpleo.objects.filter(
                estado='activa'
            ).exclude(
                id__in=ofertas_postuladas_ids
            ).order_by('-fecha_publicacion')
            
            context = {
                'mensaje': 'Bienvenido, Candidato. ¡Desliza para tu próximo empleo!',
                'ofertas': ofertas_activas,
                'ofertas_postuladas_ids': list(ofertas_postuladas_ids) # Pasamos los IDs a la plantilla
            }
            
        elif perfil.tipo == 'empleador':
            # --- LÓGICA DEL EMPLEADOR ---
            ofertas_propias = OfertaDeEmpleo.objects.filter(
                perfil_empleador=perfil
            ).order_by('-fecha_publicacion')
            
            context = {
                'mensaje': 'Bienvenido, Empleador. Aquí gestionarás tus ofertas.',
                'ofertas_propias': ofertas_propias
            }
        
        # Renderizar el dashboard correcto
        return render(request, 'jobswipe/home.html', context)

    # CORREGIDO: Usamos el error específico
    except Perfil.DoesNotExist:
        # Esto pasa si es un usuario (ej. superusuario) sin Perfil
        # (Aunque ya lo manejamos con is_staff, es una buena protección)
        context = {'mensaje': 'Error: No se encontró tu perfil. Por favor, contacta a soporte.'}
        return render(request, 'jobswipe/home.html', context)


# -----------------------------------------------------------------
# VISTAS DE FLUJO DE USUARIO
# -----------------------------------------------------------------

def register_view(request):
    """
    Vista de registro simplificada (Solo User).
    Crea un User y un Perfil vacío con tipo 'pendiente'.
    """
    if request.user.is_authenticated:
        messages.info(request, 'Ya tienes una sesión activa.')
        return redirect('home')

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        
        if user_form.is_valid():
            user = user_form.save()
            
            # Creamos un Perfil por defecto, el 'default' en models.py
            # lo pondrá como 'pendiente' automáticamente.
            Perfil.objects.create(user=user) 
            
            login(request, user)
            messages.success(request, '¡Te has registrado exitosamente!')
            # Redirigimos a 'home', que detectará 'pendiente' y forzará la elección de rol
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    else:
        user_form = UserRegisterForm()

    context = {
        'user_form': user_form
    }
    return render(request, 'jobswipe/register.html', context)


@login_required
def elegir_rol_view(request):
    """
    Vista para el "onboarding".
    Maneja la elección de rol ('candidato' o 'empleador').
    """
    perfil = request.user.perfil
    
    # Si ya no está pendiente, no debería estar aquí
    if perfil.tipo != 'pendiente':
        return redirect('home')
        
    if request.method == 'POST':
        tipo_elegido = request.POST.get('tipo')
        
        if tipo_elegido in ['candidato', 'empleador']:
            perfil.tipo = tipo_elegido
            perfil.save()
            messages.success(request, f'¡Tu perfil ha sido configurado como {tipo_elegido}!')
            return redirect('home') # Ahora 'home' le mostrará el dashboard correcto
        else:
            messages.error(request, 'Por favor, selecciona un rol válido.')

    # Si es GET, muestra la plantilla
    return render(request, 'jobswipe/elegir_rol.html')


# -----------------------------------------------------------------
# VISTAS DE EMPLEADOR
# -----------------------------------------------------------------

@login_required
def crear_oferta_view(request):
    """
    Vista para que los empleadores creen una nueva oferta de empleo.
    """
    # 1. Verificar que el User sea un empleador
    try:
        if request.user.perfil.tipo != 'empleador':
            messages.error(request, 'Solo los empleadores pueden publicar ofertas.')
            return redirect('home')
    except Perfil.DoesNotExist:
        messages.error(request, 'No tienes permiso para acceder a esta página.')
        return redirect('home')

    # 2. Procesar el formulario
    if request.method == 'POST':
        form = OfertaDeEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.perfil_empleador = request.user.perfil
            oferta.save() 
            
            messages.success(request, '¡Tu oferta de empleo ha sido publicada exitosamente!')
            return redirect('home')
        else:
            messages.error(request, 'Hubo un error en el formulario. Por favor, revisa los campos.')
    else:
        form = OfertaDeEmpleoForm()

    context = {
        'form': form
    }
    return render(request, 'jobswipe/crear_oferta.html', context)


@login_required
def eliminar_oferta_view(request, id_oferta):
    """
    Vista para eliminar una oferta.
    Solo el dueño de la oferta puede eliminarla.
    """
    # Usamos get_object_or_404 para más seguridad
    oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
    
    # Verificar que el usuario logueado sea el dueño
    if request.user.perfil == oferta.perfil_empleador:
        if request.method == 'POST':
            oferta.delete()
            messages.success(request, 'Oferta eliminada exitosamente.')
            return redirect('home')
    else:
        messages.error(request, 'No tienes permiso para eliminar esta oferta.')
        return redirect('home')
    
    # Si es GET (no debería pasar, pero por si acaso)
    return redirect('home')


@login_required
def revisar_candidatos_view(request, id_oferta):
    """
    Vista "Tinder" para aceptar o rechazar candidatos.
    """
    oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
    
    # Seguridad: solo el empleador dueño de la oferta puede revisar
    if request.user.perfil != oferta.perfil_empleador:
        messages.error(request, 'No tienes permiso para revisar esta oferta.')
        return redirect('home')
    
    # Buscamos la próxima solicitud PENDIENTE para esta oferta
    # .first() nos da el primer objeto o None
    proxima_solicitud = Solicitud.objects.filter(
        oferta=oferta, 
        estado='pendiente'
    ).first() 
    
    context = {
        'oferta': oferta,
        'solicitud': proxima_solicitud # Será None si no hay más pendientes
    }
    return render(request, 'jobswipe/revisar_candidatos.html', context)


@login_required
def aceptar_solicitud_view(request, id_solicitud):
    """
    Acción para marcar una solicitud como 'aceptada' (Match).
    """
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)
    
    # Seguridad: solo el empleador dueño de la oferta puede aceptar
    if request.user.perfil == solicitud.oferta.perfil_empleador:
        if request.method == 'POST':
            solicitud.estado = 'aceptada'
            solicitud.save()
            messages.success(request, f'¡Match! Has aceptado a {solicitud.User_candidato.first_name}.')
            # Lo mandamos de vuelta a la página de revisión para ver al siguiente
            return redirect('revisar_candidatos', id_oferta=solicitud.oferta.id)
    else:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('home')
    
    return redirect('home')


@login_required
def rechazar_solicitud_view(request, id_solicitud):
    """
    Acción para marcar una solicitud como 'rechazada'.
    """
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)
    
    # Seguridad: solo el empleador dueño de la oferta puede rechazar
    if request.user.perfil == solicitud.oferta.perfil_empleador:
        if request.method == 'POST':
            solicitud.estado = 'rechazada'
            solicitud.save()
            messages.warning(request, f'Has rechazado a {solicitud.User_candidato.first_name}.')
            # Lo mandamos de vuelta a la página de revisión para ver al siguiente
            return redirect('revisar_candidatos', id_oferta=solicitud.oferta.id)
    else:
        messages.error(request, 'No tienes permiso para esta acción.')
        return redirect('home')

    return redirect('home')


# -----------------------------------------------------------------
# VISTAS DE CANDIDATO
# -----------------------------------------------------------------

@login_required
def postular_oferta_view(request, id_oferta):
    """
    Acción para que un candidato postule a una oferta.
    """
    # 1. Verificar que el usuario sea un candidato
    if request.user.perfil.tipo != 'candidato':
        messages.error(request, 'Solo los candidatos pueden postular a ofertas.')
        return redirect('home')
        
    if request.method == 'POST':
        oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
        
        # 2. Intentar crear la solicitud
        try:
            Solicitud.objects.create(
                oferta=oferta,
                User_candidato=request.user,
                estado='pendiente' # El empleador deberá revisarla
            )
            messages.success(request, f'¡Has postulado exitosamente a "{oferta.titulo}"!')
        
        # 3. Manejar error si ya postuló
        except IntegrityError:
            # Esto pasa si la 'unique_together' en models.py falla
            messages.warning(request, 'Ya has postulado a esta oferta.')
            
    return redirect('home')


# -----------------------------------------------------------------
# VISTAS DE CHAT Y MATCHES (¡NUEVAS!)
# -----------------------------------------------------------------

@login_required
def matches_view(request):
    """
    Muestra la lista de "matches" (solicitudes aceptadas)
    donde el usuario actual está involucrado (sea como candidato o empleador).
    """
    
    # Usamos Q() para una consulta OR
    # Un "match" es una solicitud 'aceptada' donde:
    # 1. Yo soy el candidato (User_candidato)
    # O
    # 2. Yo soy el empleador (oferta__perfil_empleador)
    
    matches = Solicitud.objects.filter(
        Q(estado='aceptada'), # Siempre debe estar aceptada
        Q(User_candidato=request.user) | # Yo soy el candidato
        Q(oferta__perfil_empleador=request.user.perfil) # Yo soy el empleador
    ).select_related(
        'User_candidato', 
        'User_candidato__perfil', 
        'oferta', 
        'oferta__perfil_empleador',
        'oferta__perfil_empleador__user'
    ).order_by('-fecha_postulacion') # Mostrar matches más recientes primero
    
    context = {
        'matches': matches
    }
    return render(request, 'jobswipe/matches.html', context)


@login_required
def chat_view(request, solicitud_id):
    """
    Muestra la sala de chat para una solicitud (match) específica.
    """
    # 1. Obtener la solicitud (el match)
    solicitud = get_object_or_404(Solicitud, id=solicitud_id, estado='aceptada')
    
    # 2. Seguridad: Asegurarse de que el usuario actual sea parte de este chat
    es_candidato = (request.user == solicitud.User_candidato)
    es_empleador = (request.user.perfil == solicitud.oferta.perfil_empleador)
    
    if not (es_candidato or es_empleador):
        messages.error(request, 'No tienes permiso para ver este chat.')
        return redirect('matches')
        
    # 3. Determinar quién es el "otro" usuario en el chat
    if es_candidato:
        otro_usuario = solicitud.oferta.perfil_empleador.user
        otro_usuario_nombre = otro_usuario.first_name
    else:
        otro_usuario = solicitud.User_candidato
        otro_usuario_nombre = otro_usuario.first_name

    # 4. Manejar el envío de un nuevo mensaje
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            Mensaje.objects.create(
                solicitud=solicitud,
                User_origen=request.user,
                User_destino=otro_usuario,
                contenido=contenido
            )
            # Redirigir (POST-Redirect-GET) para evitar re-envío
            return redirect('chat', solicitud_id=solicitud_id)

    # 5. Obtener todos los mensajes de esta solicitud (match)
    mensajes = Mensaje.objects.filter(solicitud=solicitud).order_by('fecha')

    # (Opcional: Marcar mensajes como leídos)
    # ... (lógica más avanzada)

    context = {
        'solicitud': solicitud,
        'mensajes': mensajes,
        'otro_usuario_nombre': otro_usuario_nombre
    }
    return render(request, 'jobswipe/chat.html', context)