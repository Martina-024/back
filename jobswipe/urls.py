from django.urls import path
from . import views

urlpatterns = [
    # --- Vistas de Autenticación y Flujo ---
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('elegir-rol/', views.elegir_rol_view, name='elegir_rol'),
    
    # --- Vistas de Empleador ---
    path('oferta/crear/', views.crear_oferta_view, name='crear_oferta'),
    
    # --- ¡NUEVAS RUTAS! ---
    
    # Ruta para eliminar una oferta.
    # ej: /oferta/eliminar/5/
    path(
        'oferta/eliminar/<int:id_oferta>/', 
        views.eliminar_oferta_view, 
        name='eliminar_oferta'
    ),
    
    # Ruta para la página de "Tinder" (revisar candidatos)
    # ej: /oferta/revisar/5/
    path(
        'oferta/revisar/<int:id_oferta>/', 
        views.revisar_candidatos_view, 
        name='revisar_candidatos'
    ),
    
    # Ruta para la acción de "Aceptar"
    # ej: /solicitud/aceptar/12/
    path(
        'solicitud/aceptar/<int:id_solicitud>/', 
        views.aceptar_solicitud_view, 
        name='aceptar_solicitud'
    ),
    
    # Ruta para la acción de "Rechazar"
    # ej: /solicitud/rechazar/12/
    path(
        'solicitud/rechazar/<int:id_solicitud>/', 
        views.rechazar_solicitud_view, 
        name='rechazar_solicitud'
    ),
    path(
        'oferta/postular/<int:id_oferta>/',
        views.postular_oferta_view,
        name='postular_oferta'
    ),
    # --- ¡NUEVAS RUTAS PARA CHAT Y MATCHES! ---
    
    # Página de "Mis Matches" (bandeja de entrada)
    path(
        'matches/',
        views.matches_view,
        name='matches'
    ),
    
    # Sala de chat individual para un match (solicitud)
    path(
        'chat/<int:solicitud_id>/',
        views.chat_view,
        name='chat'
    ),
]