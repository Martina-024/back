from django.urls import path
from . import views

urlpatterns = [
    # --- Vistas de Autenticación y Flujo ---
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('elegir-rol/', views.elegir_rol_view, name='elegir_rol'),
    
    # --- ¡NUEVO! Interruptor de Modo Inclusivo ---
    path('perfil/toggle-pcd/', views.toggle_pcd_view, name='toggle_pcd'),
    
    # --- Vistas de Empleador ---
    path('oferta/crear/', views.crear_oferta_view, name='crear_oferta'),
    
    # Editar oferta (CRUD)
    path(
        'oferta/editar/<int:id_oferta>/', 
        views.editar_oferta_view, 
        name='editar_oferta'
    ),

    # Eliminar oferta
    path(
        'oferta/eliminar/<int:id_oferta>/', 
        views.eliminar_oferta_view, 
        name='eliminar_oferta'
    ),
    
    # Revisar candidatos (Tinder)
    path(
        'oferta/revisar/<int:id_oferta>/', 
        views.revisar_candidatos_view, 
        name='revisar_candidatos'
    ),
    
    # Aceptar solicitud
    path(
        'solicitud/aceptar/<int:id_solicitud>/', 
        views.aceptar_solicitud_view, 
        name='aceptar_solicitud'
    ),
    
    # Rechazar solicitud
    path(
        'solicitud/rechazar/<int:id_solicitud>/', 
        views.rechazar_solicitud_view, 
        name='rechazar_solicitud'
    ),
    
    # --- Vistas de Candidato ---
    path(
        'oferta/postular/<int:id_oferta>/',
        views.postular_oferta_view,
        name='postular_oferta'
    ),
    
    # --- Vistas de Chat y Matches ---
    
    # Bandeja de entrada
    path(
        'matches/',
        views.matches_view,
        name='matches'
    ),
    
    # Sala de chat
    path(
        'chat/<int:solicitud_id>/',
        views.chat_view,
        name='chat'
    ),
]