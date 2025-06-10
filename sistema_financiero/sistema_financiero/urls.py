"""
URL configuration for sistema_financiero project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# proyecto_finanzas/urls.py (archivo principal)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # Autenticación (si necesitas usuarios)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # App de contabilidad (donde están tus estados financieros)
    path('', include('sistema_contable.urls')),
    
    # Otras apps que puedas tener
    # path('otra-app/', include('otra_app.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Solo en desarrollo: servir archivos multimedia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
