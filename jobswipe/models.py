from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Modelo de Perfil de User ---
# Extiende el modelo User nativo de Django
class Perfil(models.Model):
    # Relación uno-a-uno con el User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')

    # Tipos de User (¡ESTOS CAMPOS ESTÁN AQUÍ AHORA!)
    TIPO_User_CHOICES = [
        ('pendiente', 'Pendiente'), # Default para el nuevo flujo de onboarding
        ('candidato', 'Candidato'),
        ('empleador', 'Empleador'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_User_CHOICES, default='pendiente')
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    # Campos adicionales
    descripcion_profesional = models.TextField(blank=True, null=True)
    habilidades = models.TextField(blank=True, null=True, help_text="Separadas por comas")
    experiencia = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return self.user.username

# --- Categorías de Empleo ---
class CategoriaDeServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Categorías de Servicio"

# --- Ofertas de Empleo ---
class OfertaDeEmpleo(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('cerrada', 'Cerrada'),
    ]
    
    # Perfil del empleador que crea la oferta (Coincide con tu views.py)
    perfil_empleador = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='ofertas_publicadas')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(CategoriaDeServicio, on_delete=models.SET_NULL, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')

    # --- ¡NUEVO CAMPO DE INCLUSIÓN! ---
    es_inclusion = models.BooleanField(
        default=False,
        verbose_name="Oferta bajo Ley 21.015 (Inclusión)",
        help_text="Marcar si esta vacante se acoge a la Ley de Inclusión Laboral."
    )
    # ----------------------------------

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Ofertas de Empleo"

# --- Solicitudes de Empleo (Swipes/Matches) ---
class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'), # Match
        ('rechazada', 'Rechazada'),
    ]
    
    oferta = models.ForeignKey(OfertaDeEmpleo, on_delete=models.CASCADE, related_name='solicitudes')
    # User candidato que postula (Tu nombre de campo original)
    User_candidato = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_enviadas')
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')

    class Meta:
        # Asegura que un candidato solo puede postular una vez a la misma oferta
        unique_together = ('oferta', 'User_candidato')
        verbose_name_plural = "Solicitudes"

    def __str__(self):
        return f'{self.User_candidato.username} a {self.oferta.titulo}'

# --- Mensajería ---
class Mensaje(models.Model):
    # Tu nombre de campo original
    User_origen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    User_destino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    
    # --- ¡CAMBIO CRÍTICO AQUÍ! ---
    # Vinculamos el mensaje a la Solicitud (el "match")
    # en lugar de a la Oferta general.
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='mensajes')
    # ------------------------------
    
    fecha = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField()
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f'De {self.User_origen} a {self.User_destino} ({self.fecha.strftime("%Y-%m-%d %H:%M")})'

    class Meta:
        ordering = ['fecha']