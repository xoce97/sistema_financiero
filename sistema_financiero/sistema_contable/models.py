from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=20)
    # otros campos necesarios

    def __str__(self):
        return self.nombre

class PeriodoContable(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"

class CuentaContable(models.Model):
    TIPOS_CUENTA = [
        ('ACTIVO', 'Activo'),
        ('PASIVO', 'Pasivo'),
        ('PATRIMONIO', 'Patrimonio Neto'),
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS_CUENTA)
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    nivel = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class BalanceGeneral(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    nota = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('periodo', 'cuenta')
    
    def clean(self):
        if self.cuenta.tipo not in ['ACTIVO', 'PASIVO', 'PATRIMONIO']:
            raise ValidationError("Esta cuenta no pertenece al Balance General")

class EstadoResultados(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    nota = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('periodo', 'cuenta')

    def clean(self):
        if self.cuenta.tipo not in ['INGRESO', 'GASTO']:
            raise ValidationError("Esta cuenta no pertenece al Estado de Resultados")
    

class AnalisisVertical(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    tipo_estado = models.CharField(max_length=20, choices=[('BALANCE', 'Balance General'), ('RESULTADOS', 'Estado de Resultados')])

    class Meta:
        unique_together = ('periodo', 'cuenta', 'tipo_estado')

class AnalisisHorizontal(models.Model):
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    periodo_base = models.ForeignKey(PeriodoContable, related_name='analisis_base', on_delete=models.CASCADE)
    periodo_comparacion = models.ForeignKey(PeriodoContable, related_name='analisis_comparacion', on_delete=models.CASCADE)
    variacion_absoluta = models.DecimalField(max_digits=15, decimal_places=2)
    variacion_relativa = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_estado = models.CharField(max_length=20, choices=[('BALANCE', 'Balance General'), ('RESULTADOS', 'Estado de Resultados')])

    class Meta:
        unique_together = ('cuenta', 'periodo_base', 'periodo_comparacion', 'tipo_estado')
    
    @property
    def get_valor_base(self):
        if self.tipo_estado == 'BALANCE':
            item = BalanceGeneral.objects.filter(
                periodo=self.periodo_base,
                cuenta=self.cuenta
            ).first()
        else:
            item = EstadoResultados.objects.filter(
                periodo=self.periodo_base,
                cuenta=self.cuenta
            ).first()
        return item.valor if item else 0
    
    @property
    def get_valor_comparacion(self):
        if self.tipo_estado == 'BALANCE':
            item = BalanceGeneral.objects.filter(
                periodo=self.periodo_comparacion,
                cuenta=self.cuenta
            ).first()
        else:
            item = EstadoResultados.objects.filter(
                periodo=self.periodo_comparacion,
                cuenta=self.cuenta
            ).first()
        return item.valor if item else 0