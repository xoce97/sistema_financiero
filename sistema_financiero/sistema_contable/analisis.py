from .models import BalanceGeneral, EstadoResultados, AnalisisVertical, AnalisisHorizontal
from django.db import models

def calcular_analisis_vertical(periodo_id):
    # Limpiar análisis previos para este período
    AnalisisVertical.objects.filter(periodo_id=periodo_id).delete()
    
    # Análisis Vertical para Balance General
    total_activos = BalanceGeneral.objects.filter(
        periodo_id=periodo_id, 
        cuenta__tipo='ACTIVO'
    ).aggregate(total=models.Sum('valor'))['total'] or 0
    
    items_balance = BalanceGeneral.objects.filter(periodo_id=periodo_id)
    for item in items_balance:
        if item.cuenta.tipo == 'ACTIVO':
            base = total_activos
        elif item.cuenta.tipo in ['PASIVO', 'PATRIMONIO']:
            base = BalanceGeneral.objects.filter(
                periodo_id=periodo_id,
                cuenta__tipo__in=['PASIVO', 'PATRIMONIO']
            ).aggregate(total=models.Sum('valor'))['total'] or 0
        else:
            continue
            
        if base != 0:
            porcentaje = (item.valor / base) * 100
            AnalisisVertical.objects.create(
                periodo=item.periodo,
                cuenta=item.cuenta,
                porcentaje=porcentaje,
                tipo_estado='BALANCE'
            )
    
    # Análisis Vertical para Estado de Resultados
    total_ingresos = EstadoResultados.objects.filter(
        periodo_id=periodo_id,
        cuenta__tipo='INGRESO'
    ).aggregate(total=models.Sum('valor'))['total'] or 0
    
    items_er = EstadoResultados.objects.filter(periodo_id=periodo_id)
    for item in items_er:
        if item.cuenta.tipo == 'INGRESO':
            base = total_ingresos
        elif item.cuenta.tipo == 'GASTO':
            base = total_ingresos  # Los gastos se comparan contra ingresos
        else:
            continue
            
        if base != 0:
            porcentaje = (item.valor / base) * 100
            AnalisisVertical.objects.create(
                periodo=item.periodo,
                cuenta=item.cuenta,
                porcentaje=porcentaje,
                tipo_estado='RESULTADOS'
            )

def calcular_analisis_horizontal(periodo_base_id, periodo_comparacion_id):
    # Limpiar análisis previos para esta combinación
    AnalisisHorizontal.objects.filter(
        periodo_base_id=periodo_base_id,
        periodo_comparacion_id=periodo_comparacion_id
    ).delete()
    
    # Análisis Horizontal para Balance General
    items_base_balance = BalanceGeneral.objects.filter(periodo_id=periodo_base_id)
    for item_base in items_base_balance:
        item_comparacion = BalanceGeneral.objects.filter(
            periodo_id=periodo_comparacion_id,
            cuenta=item_base.cuenta
        ).first()
        
        if item_comparacion:
            variacion_abs = item_comparacion.valor - item_base.valor
            variacion_rel = (variacion_abs / item_base.valor) * 100 if item_base.valor != 0 else 0
            
            AnalisisHorizontal.objects.create(
                cuenta=item_base.cuenta,
                periodo_base_id=periodo_base_id,
                periodo_comparacion_id=periodo_comparacion_id,
                variacion_absoluta=variacion_abs,
                variacion_relativa=variacion_rel,
                tipo_estado='BALANCE'
            )
    
    # Análisis Horizontal para Estado de Resultados
    items_base_er = EstadoResultados.objects.filter(periodo_id=periodo_base_id)
    for item_base in items_base_er:
        item_comparacion = EstadoResultados.objects.filter(
            periodo_id=periodo_comparacion_id,
            cuenta=item_base.cuenta
        ).first()
        
        if item_comparacion:
            variacion_abs = item_comparacion.valor - item_base.valor
            variacion_rel = (variacion_abs / item_base.valor) * 100 if item_base.valor != 0 else 0
            
            AnalisisHorizontal.objects.create(
                cuenta=item_base.cuenta,
                periodo_base_id=periodo_base_id,
                periodo_comparacion_id=periodo_comparacion_id,
                variacion_absoluta=variacion_abs,
                variacion_relativa=variacion_rel,
                tipo_estado='RESULTADOS'
            )