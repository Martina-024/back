from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q # Para consultas complejas (OR)
import requests # Necesario para la API externa

# Importamos formularios y modelos
from .forms import UserRegisterForm, OfertaDeEmpleoForm
from .models import OfertaDeEmpleo, Perfil, Solicitud, Mensaje

# -----------------------------------------------------------------
# FUNCIONES AUXILIARES (APIs)
# -----------------------------------------------------------------

def obtener_indicadores_economicos():
    """
    Consume la API de mindicador.cl para obtener la UF y el Dólar.
    """
    try:
        url = 'https://mindicador.cl/api'
        response = requests.get(url)
        data = response.json()
        
        return {
            'uf': data['uf']['valor'],
            'dolar': data['dolar']['valor'],
            'euro': data['euro']['valor']
        }
    except:
        # En caso de que no haya internet o falle la API, retornamos None
        return None


# -----------------------------------------------------------------
# VISTA DE INICIO (HOME)
# -----------------------------------------------------------------
@login_required
def home_view(request):
    """
    Vista principal. Redirige o muestra el dashboard según el rol.
    """
    # 1. Llamada a la API externa (se ejecuta para todos)
    indicadores = obtener_indicadores_economicos()

    # 2. Admin / Staff
    if request.user.is_staff:
        context = {
            'mensaje': 'Bienvenido/a, Admin.',
            'indicadores': indicadores
        }
        return render(request, 'jobswipe/home.html', context)

    # 3. Usuarios normales
    try:
        perfil = request.user.perfil 
        
        # A) Perfil incompleto -> Forzar elección de rol
        if perfil.tipo == 'pendiente':
            messages.info(request, '¡Bienvenido/a! Por favor, completa tu perfil para continuar.')
            return redirect('elegir_rol')
        
        # B) Candidato
        elif perfil.tipo == 'candidato':
            # Obtener IDs de ofertas ya postuladas
            ofertas_postuladas_ids = Solicitud.objects.filter(
                User_candidato=request.user
            ).values_list('oferta_id', flat=True)

            # --- ALGORITMO DE FILTRO LEY 21.015 ---
            if perfil.es_pcd:
                # Si el filtro está activo: primero las inclusivas, luego fecha
                orden = ['-es_inclusion', '-fecha_publicacion']
            else:
                # Si no, solo por fecha
                orden = ['-fecha_publicacion']

            # Buscar ofertas activas que NO estén postuladas
            ofertas_activas = OfertaDeEmpleo.objects.filter(
                estado='activa'
            ).exclude(
                id__in=ofertas_postuladas_ids
            ).order_by(*orden)
            
            context = {
                'mensaje': 'Bienvenido, Candidato. ¡Desliza para tu próximo empleo!',
                'ofertas': ofertas_activas,
                'ofertas_postuladas_ids': list(ofertas_postuladas_ids),
                'indicadores': indicadores
            }
            
        # C) Empleador
        elif perfil.tipo == 'empleador':
            ofertas_propias = OfertaDeEmpleo.objects.filter(
                perfil_empleador=perfil
            ).order_by('-fecha_publicacion')
            
            context = {
                'mensaje': 'Bienvenido, Empleador. Aquí gestionarás tus ofertas.',
                'ofertas_propias': ofertas_propias,
                'indicadores': indicadores
            }
        
        return render(request, 'jobswipe/home.html', context)

    except Perfil.DoesNotExist:
        context = {
            'mensaje': 'Error: No se encontró tu perfil. Contacta a soporte.',
            'indicadores': indicadores
        }
        return render(request, 'jobswipe/home.html', context)


# -----------------------------------------------------------------
# REGISTRO, ROLES Y PERFIL
# -----------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            # Crear perfil vacío
            Perfil.objects.create(user=user)
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect('home')
        else:
            messages.error(request, 'Error en el registro. Revisa los datos.')
    else:
        user_form = UserRegisterForm()

    return render(request, 'jobswipe/register.html', {'user_form': user_form})


@login_required
def elegir_rol_view(request):
    perfil = request.user.perfil
    if perfil.tipo != 'pendiente':
        return redirect('home')
        
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        if tipo in ['candidato', 'empleador']:
            perfil.tipo = tipo
            perfil.save()
            messages.success(request, f'¡Perfil configurado como {tipo}!')
            return redirect('home')
    
    return render(request, 'jobswipe/elegir_rol.html')


@login_required
def toggle_pcd_view(request):
    """
    Activa o desactiva el filtro de inclusión (Ley 21.015).
    """
    perfil = request.user.perfil
    perfil.es_pcd = not perfil.es_pcd
    perfil.save()
    
    # --- AQUÍ ESTABA EL TEXTO ANTIGUO ---
    estado = "activado" if perfil.es_pcd else "desactivado"
    messages.success(request, f'Filtro {estado}.') # <--- ¡CORREGIDO!
    return redirect('home')


# -----------------------------------------------------------------
# GESTIÓN DE OFERTAS (EMPLEADOR)
# -----------------------------------------------------------------

@login_required
def crear_oferta_view(request):
    if request.user.perfil.tipo != 'empleador':
        return redirect('home')

    if request.method == 'POST':
        form = OfertaDeEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.perfil_empleador = request.user.perfil
            oferta.save()
            messages.success(request, 'Oferta publicada correctamente.')
            return redirect('home')
    else:
        form = OfertaDeEmpleoForm()

    return render(request, 'jobswipe/crear_oferta.html', {'form': form})


@login_required
def eliminar_oferta_view(request, id_oferta):
    oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
    if request.user.perfil == oferta.perfil_empleador:
        oferta.delete()
        messages.success(request, 'Oferta eliminada.')
    return redirect('home')


@login_required
def editar_oferta_view(request, id_oferta):
    oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
    
    if request.user.perfil != oferta.perfil_empleador:
        messages.error(request, 'No tienes permiso para editar esta oferta.')
        return redirect('home')

    if request.method == 'POST':
        form = OfertaDeEmpleoForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Oferta actualizada correctamente.')
            return redirect('home')
    else:
        form = OfertaDeEmpleoForm(instance=oferta)

    return render(request, 'jobswipe/editar_oferta.html', {'form': form, 'oferta': oferta})


@login_required
def revisar_candidatos_view(request, id_oferta):
    oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
    
    if request.user.perfil != oferta.perfil_empleador:
        return redirect('home')
    
    proxima_solicitud = Solicitud.objects.filter(
        oferta=oferta, 
        estado='pendiente'
    ).first()
    
    return render(request, 'jobswipe/revisar_candidatos.html', {
        'oferta': oferta,
        'solicitud': proxima_solicitud
    })


@login_required
def aceptar_solicitud_view(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)
    if request.user.perfil == solicitud.oferta.perfil_empleador:
        solicitud.estado = 'aceptada'
        solicitud.save()
        messages.success(request, f'¡Match con {solicitud.User_candidato.first_name}!')
        return redirect('revisar_candidatos', id_oferta=solicitud.oferta.id)
    return redirect('home')


@login_required
def rechazar_solicitud_view(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud, id=id_solicitud)
    if request.user.perfil == solicitud.oferta.perfil_empleador:
        solicitud.estado = 'rechazada'
        solicitud.save()
        messages.warning(request, 'Candidato descartado.')
        return redirect('revisar_candidatos', id_oferta=solicitud.oferta.id)
    return redirect('home')


# -----------------------------------------------------------------
# ACCIONES DEL CANDIDATO
# -----------------------------------------------------------------

@login_required
def postular_oferta_view(request, id_oferta):
    if request.user.perfil.tipo != 'candidato':
        return redirect('home')
        
    oferta = get_object_or_404(OfertaDeEmpleo, id=id_oferta)
    try:
        Solicitud.objects.create(
            oferta=oferta,
            User_candidato=request.user,
            estado='pendiente'
        )
        messages.success(request, f'Postulaste a "{oferta.titulo}"')
    except IntegrityError:
        messages.warning(request, 'Ya habías postulado a esta oferta.')
            
    return redirect('home')


# -----------------------------------------------------------------
# CHAT Y MATCHES
# -----------------------------------------------------------------

@login_required
def matches_view(request):
    matches = Solicitud.objects.filter(
        Q(estado='aceptada'),
        Q(User_candidato=request.user) | 
        Q(oferta__perfil_empleador=request.user.perfil)
    ).order_by('-fecha_postulacion')
    
    return render(request, 'jobswipe/matches.html', {'matches': matches})


@login_required
def chat_view(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id, estado='aceptada')
    
    es_candidato = (request.user == solicitud.User_candidato)
    es_empleador = (request.user.perfil == solicitud.oferta.perfil_empleador)
    
    if not (es_candidato or es_empleador):
        messages.error(request, 'No tienes permiso para ver este chat.')
        return redirect('matches')

    if es_candidato:
        otro_usuario = solicitud.oferta.perfil_empleador.user
    else:
        otro_usuario = solicitud.User_candidato

    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            Mensaje.objects.create(
                solicitud=solicitud,
                User_origen=request.user, 
                User_destino=otro_usuario,
                contenido=contenido
            )
            return redirect('chat', solicitud_id=solicitud_id)

    mensajes = Mensaje.objects.filter(solicitud=solicitud).order_by('fecha')

    context = {
        'solicitud': solicitud,
        'mensajes': mensajes,
        'otro_usuario_nombre': otro_usuario.first_name
    }
    return render(request, 'jobswipe/chat.html', context)