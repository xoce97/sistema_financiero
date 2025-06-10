from django.urls import path
from . import views

urlpatterns = [
    path('empresa/nueva/', views.empresa_nueva, name='empresa_nueva'),
    path('periodos/nuevos/<int:empresa_id>/', views.periodos_nuevos, name='periodos_nuevos'),
    path('balance/nuevo/', views.BalanceGeneralCreateView.as_view(), name='nuevo_balance'),
    path('estado-resultados/nuevo/', views.EstadoResultadosCreateView.as_view(), name='nuevo_estado_resultados'),
    path('importar/', views.importar_archivo, name='importar_archivo'),
    path('cuentas/importar/', views.importar_cuentas, name='importar_cuentas'),
    path('cuentas/', views.lista_cuentas, name='lista_cuentas'),
    # otras URLs necesarias
    path('analisis/vertical/', views.analisis_vertical, name='analisis_vertical'),
    path('analisis/horizontal/', views.analisis_horizontal, name='analisis_horizontal'),
    path('dashboard/', views.dashboard_financiero, name='dashboard_financiero'),
]