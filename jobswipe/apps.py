from django.apps import AppConfig

# 1. Renombramos la clase de 'AppjobswipeConfig' a 'JobswipeConfig'
class JobswipeConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    # 2. Renombramos el 'name' para que coincida con la carpeta
    name = 'jobswipe'