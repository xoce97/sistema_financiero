from django import forms
from .models import Empresa, BalanceGeneral, EstadoResultados, PeriodoContable, CuentaContable

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'rfc']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'RFC': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PeriodoContableForm(forms.ModelForm):
    class Meta:
        model = PeriodoContable
        fields = ['empresa', 'nombre', 'fecha_inicio', 'fecha_fin', 'cerrado']
        widgets = {
            'empresa': forms.HiddenInput(),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cerrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BalanceGeneralForm(forms.ModelForm):
    class Meta:
        model = BalanceGeneral
        fields = ['periodo', 'cuenta', 'valor', 'nota']
        
    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super().__init__(*args, **kwargs)
        if empresa_id:
            self.fields['periodo'].queryset = PeriodoContable.objects.filter(empresa_id=empresa_id)
            self.fields['cuenta'].queryset = CuentaContable.objects.filter(
                tipo__in=['ACTIVO', 'PASIVO', 'PATRIMONIO']
            )

class EstadoResultadosForm(forms.ModelForm):
    class Meta:
        model = EstadoResultados
        fields = ['periodo', 'cuenta', 'valor', 'nota']
        
    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super().__init__(*args, **kwargs)
        if empresa_id:
            self.fields['periodo'].queryset = PeriodoContable.objects.filter(empresa_id=empresa_id)
            self.fields['cuenta'].queryset = CuentaContable.objects.filter(
                tipo__in=['INGRESO', 'GASTO']
            )

class ImportarArchivoForm(forms.Form):
    archivo = forms.FileField(label='Seleccione archivo CSV o XML')
    periodo = forms.ModelChoiceField(queryset=PeriodoContable.objects.none())
    
    def __init__(self, *args, **kwargs):
        empresa_id = kwargs.pop('empresa_id', None)
        super().__init__(*args, **kwargs)
        if empresa_id:
            self.fields['periodo'].queryset = PeriodoContable.objects.filter(empresa_id=empresa_id)

class ImportarCuentasForm(forms.Form):
    archivo_csv = forms.FileField(label='Seleccione archivo CSV')
    sobrescribir = forms.BooleanField(
        label='Sobrescribir cuentas existentes',
        required=False,
        help_text='Marcar para actualizar cuentas con el mismo código'
    )