from enum import Enum

from django.core.validators import MinValueValidator
from django.db import models


class EstatusEmpresa(Enum):
    ACTIVA = "Activa"
    INACTIVA = "Inactiva"


class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[(tag, tag.value) for tag in EstatusEmpresa],
        default=EstatusEmpresa.ACTIVA.value,
    )
    fecha_creacion = models.DateField(auto_now_add=True)


class PeriodoContable(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cerrado = models.BooleanField(default=False)


class BalanceGeneral(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    efectivo_equivalentes = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    cuentas_por_cobrar = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    inventarios = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    otros_activos_circulantes = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )

    propiedades_plantas_equipos = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    activos_intangibles = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    otros_activos_no_circulantes = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )

    cuentas_por_pagar = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    pasivos_acumulados = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    deudas_a_corto_plazo = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )

    deuda_a_largo_plazo = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    otros_pasivos_a_largo_plazo = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )

    capital_social_y_utilidades_retenidas = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )

    @property
    def total_activo_circulante(self):
        return (
            self.efectivo_equivalentes
            + self.cuentas_por_cobrar
            + self.inventarios
            + self.otros_activos_circulantes
        )

    @property
    def total_activo_no_circulante(self):
        return (
            self.propiedades_plantas_equipos
            + self.activos_intangibles
            + self.otros_activos_no_circulantes
        )

    @property
    def total_activo(self):
        return self.total_activo_circulante + self.total_activo_no_circulante

    @property
    def total_pasivo_circulante(self):
        return (
            self.cuentas_por_pagar + self.pasivos_acumulados + self.deudas_a_corto_plazo
        )

    @property
    def total_pasivo_a_largo_plazo(self):
        return self.deuda_a_largo_plazo + self.otros_pasivos_a_largo_plazo

    @property
    def total_pasivo(self):
        return self.total_pasivo_circulante + self.total_pasivo_a_largo_plazo

    @property
    def total_pasivo_y_capital_contable(self):
        return self.total_pasivo + self.capital_social_y_utilidades_retenidas


class EstadoResultados(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    ventas_netas = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    costo_ventas = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    utilidad_bruta = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    gastos_operativos = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    utilidad_operativa = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    resultado_financiero = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    utilidad_ante_impuestos = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    impuesto_utilidad = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    utilidad_neta = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
