from django.db import models
from django.core.validators import MinValueValidator

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=20)
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
        ('Capital', 'Capital Contable'),
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS_CUENTA)
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class BalanceGeneral(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    nota = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('periodo', 'cuenta')

class EstadoResultados(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    nota = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('periodo', 'cuenta')