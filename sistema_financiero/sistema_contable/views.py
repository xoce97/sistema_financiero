from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, ListView
from .models import Empresa,PeriodoContable, BalanceGeneral, EstadoResultados,CuentaContable,AnalisisVertical, AnalisisHorizontal,PeriodoContable
from .forms import ImportarCuentasForm, EmpresaForm,PeriodoContableForm, BalanceGeneralForm, EstadoResultadosForm, ImportarArchivoForm,CuentaContable
from .analisis import calcular_analisis_vertical, calcular_analisis_horizontal
import csv
import json
from xml.etree import ElementTree as ET
from django.contrib import messages
from django.http import JsonResponse
from django.forms import modelformset_factory

def dashboard_financiero(request):
    return render(request, 'dashboard_financiero.html')

def lista_cuentas(request):
    cuentas = CuentaContable.objects.all().order_by('codigo')
    return render(request, 'lista_cuentas.html', {'cuentas': cuentas})


def empresa_nueva(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            # Guarda el ID en sesión si lo necesitas
            request.session['empresa_id'] = empresa.id
            return redirect('periodos_nuevos', empresa_id=empresa.id)
    else:
        form = EmpresaForm()
    return render(request, 'empresa_form.html', {'form': form})

def periodos_nuevos(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    PeriodoFormSet = modelformset_factory(
        PeriodoContable,
        form=PeriodoContableForm,
        extra=3,
        can_delete=False
    )
    if request.method == 'POST':
        formset = PeriodoFormSet(request.POST, queryset=PeriodoContable.objects.none())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.empresa = empresa
                instance.save()
            messages.success(request, "Períodos contables agregados correctamente.")
            return redirect('dashboard_financiero')  # Cambia por la vista a la que quieras redirigir
    else:
        formset = PeriodoFormSet(queryset=PeriodoContable.objects.none())
    return render(request, 'periodos_form.html', {'formset': formset, 'empresa': empresa})

class BalanceGeneralCreateView(CreateView):
    model = BalanceGeneral,PeriodoContable
    form_class = BalanceGeneralForm
    template_name = 'balance_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa_id'] = self.request.session.get('empresa_id')
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Registro de Balance General guardado correctamente.')
        return super().form_valid(form)

class EstadoResultadosCreateView(CreateView):
    model = EstadoResultados
    form_class = EstadoResultadosForm
    template_name = 'sistema_contable/estado_resultados_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa_id'] = self.request.session.get('empresa_id')
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Registro de Estado de Resultados guardado correctamente.')
        return super().form_valid(form)

def importar_archivo(request):
    if request.method == 'POST':
        form = ImportarArchivoForm(request.POST, request.FILES, empresa_id=request.session.get('empresa_id'))
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            archivo = request.FILES['archivo']
            extension = archivo.name.split('.')[-1].lower()
            
            try:
                if extension == 'csv':
                    procesar_csv(archivo, periodo)
                elif extension == 'xml':
                    procesar_xml(archivo, periodo)
                else:
                    messages.error(request, 'Formato de archivo no soportado.')
                    return redirect('importar_archivo')
                
                messages.success(request, 'Datos importados correctamente.')
                return redirect('lista_balances')
            except Exception as e:
                messages.error(request, f'Error al procesar archivo: {str(e)}')
    else:
        form = ImportarArchivoForm(empresa_id=request.session.get('empresa_id'))
    return render(request, 'importar.html', {'form': form})

def procesar_csv(archivo, periodo):
    decoded_file = archivo.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    for row in reader:
        try:
            cuenta = CuentaContable.objects.get(codigo=row['codigo_cuenta'])
            
            if cuenta.tipo in ['ACTIVO', 'PASIVO', 'PATRIMONIO']:
                BalanceGeneral.objects.update_or_create(
                    periodo=periodo,
                    cuenta=cuenta,
                    defaults={'valor': row['valor'], 'nota': row.get('nota', '')}
                )
            elif cuenta.tipo in ['INGRESO', 'GASTO']:
                EstadoResultados.objects.update_or_create(
                    periodo=periodo,
                    cuenta=cuenta,
                    defaults={'valor': row['valor'], 'nota': row.get('nota', '')}
                )
        except CuentaContable.DoesNotExist:
            continue

def procesar_xml(archivo, periodo):
    tree = ET.parse(archivo)
    root = tree.getroot()
    
    for elem in root.findall('cuenta'):
        try:
            codigo = elem.find('codigo').text
            valor = elem.find('valor').text
            nota = elem.find('nota').text if elem.find('nota') is not None else ''
            
            cuenta = CuentaContable.objects.get(codigo=codigo)
            
            if cuenta.tipo in ['ACTIVO', 'PASIVO', 'PATRIMONIO']:
                BalanceGeneral.objects.update_or_create(
                    periodo=periodo,
                    cuenta=cuenta,
                    defaults={'valor': valor, 'nota': nota}
                )
            elif cuenta.tipo in ['INGRESO', 'GASTO']:
                EstadoResultados.objects.update_or_create(
                    periodo=periodo,
                    cuenta=cuenta,
                    defaults={'valor': valor, 'nota': nota}
                )
        except CuentaContable.DoesNotExist:
            continue

def analisis_vertical(request):
    periodo_id = request.GET.get('periodo')
    tipo = request.GET.get('tipo', 'BALANCE')  # BALANCE o RESULTADOS
    
    if periodo_id:
        calcular_analisis_vertical(periodo_id)
        resultados = AnalisisVertical.objects.filter(
            periodo_id=periodo_id,
            tipo_estado=tipo
        ).select_related('cuenta').order_by('cuenta__codigo')
        
        # Agrupar por tipo de cuenta para mejor visualización
        grupos = {}
        for item in resultados:
            if item.cuenta.tipo not in grupos:
                grupos[item.cuenta.tipo] = []
            grupos[item.cuenta.tipo].append(item)
    else:
        resultados = None
        grupos = None
    
    periodos = PeriodoContable.objects.filter(empresa_id=request.session.get('empresa_id'))
    
    return render(request, 'analisis_vertical.html', {
        'resultados': resultados,
        'grupos': grupos,
        'periodos': periodos,
        'tipo_seleccionado': tipo,
        'periodo_seleccionado': int(periodo_id) if periodo_id else None
    })

def analisis_horizontal(request):
    periodo_base_id = request.GET.get('periodo_base')
    periodo_comparacion_id = request.GET.get('periodo_comparacion')
    tipo = request.GET.get('tipo', 'BALANCE')
    
    if periodo_base_id and periodo_comparacion_id:
        calcular_analisis_horizontal(periodo_base_id, periodo_comparacion_id)
        resultados = AnalisisHorizontal.objects.filter(
            periodo_base_id=periodo_base_id,
            periodo_comparacion_id=periodo_comparacion_id,
            tipo_estado=tipo
        ).select_related('cuenta', 'periodo_base', 'periodo_comparacion').order_by('cuenta__codigo')
        
        # Agrupar por tipo de cuenta
        grupos = {}
        for item in resultados:
            if item.cuenta.tipo not in grupos:
                grupos[item.cuenta.tipo] = []
            grupos[item.cuenta.tipo].append(item)
    else:
        resultados = None
        grupos = None
    
    periodos = PeriodoContable.objects.filter(empresa_id=request.session.get('empresa_id'))
    
    return render(request, 'analisis_horizontal.html', {
        'resultados': resultados,
        'grupos': grupos,
        'periodos': periodos,
        'tipo_seleccionado': tipo,
        'periodo_base_seleccionado': int(periodo_base_id) if periodo_base_id else None,
        'periodo_comparacion_seleccionado': int(periodo_comparacion_id) if periodo_comparacion_id else None
    })

def importar_cuentas(request):
    if request.method == 'POST':
        form = ImportarCuentasForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_csv']
            sobrescribir = form.cleaned_data['sobrescribir']
            
            try:
                resultado = procesar_archivo_cuentas(archivo, sobrescribir)
                messages.success(
                    request,
                    f"¡Importación completada!<br>"
                    f"Cuentas creadas: {resultado['creadas']}<br>"
                    f"Cuentas actualizadas: {resultado['actualizadas']}"
                )
                return redirect('lista_cuentas')
            except Exception as e:
                messages.error(request, f"Error al procesar archivo: {str(e)}")
    else:
        form = ImportarCuentasForm()
    
    return render(request, 'importar_cuentas.html', {'form': form})

def procesar_archivo_cuentas(archivo, sobrescribir):
    decoded_file = archivo.read().decode('utf-8-sig').splitlines()
    sample = decoded_file[0]
    delimiter = ';' if ';' in sample else ','
    reader = csv.DictReader(decoded_file, delimiter=delimiter)
    
    creadas = 0
    actualizadas = 0

    for row in reader:
        # Usar los nombres de columna reales del CSV
        codigo = row.get('código', '').strip()
        nombre = row.get('nombre', '').strip()
        nivel = int(row.get('nivel', 1)) if row.get('nivel') else 1

        if not codigo or not nombre:
            continue

        # Asignar tipo automáticamente según el código agrupador
        if codigo.startswith('1'):
            tipo = 'ACTIVO'
        elif codigo.startswith('2'):
            tipo = 'PASIVO'
        elif codigo.startswith('3'):
            tipo = 'PATRIMONIO'
        elif codigo.startswith('4'):
            tipo = 'INGRESO'
        elif codigo.startswith('5') or codigo.startswith('6'):
            tipo = 'GASTO'
        else:
            tipo = 'ACTIVO'

        datos_cuenta = {
            'codigo': codigo,
            'nombre': nombre,
            'tipo': tipo,
            'nivel': nivel
        }

        # Buscar padre por código si es subcuenta
        padre_codigo = None
        if '.' in codigo:
            padre_codigo = codigo.rsplit('.', 1)[0]
        if padre_codigo:
            try:
                padre = CuentaContable.objects.get(codigo=padre_codigo)
                datos_cuenta['padre'] = padre
            except CuentaContable.DoesNotExist:
                pass

        if sobrescribir:
            cuenta, created = CuentaContable.objects.update_or_create(
                codigo=datos_cuenta['codigo'],
                defaults=datos_cuenta
            )
            if created:
                creadas += 1
            else:
                actualizadas += 1
        else:
            if not CuentaContable.objects.filter(codigo=datos_cuenta['codigo']).exists():
                CuentaContable.objects.create(**datos_cuenta)
                creadas += 1

    return {'creadas': creadas, 'actualizadas': actualizadas}

def lista_cuentas(request):
    cuentas = CuentaContable.objects.all().order_by('codigo')
    return render(request, 'lista_cuentas.html', {'cuentas': cuentas})
