from odoo import models, fields
import random
import string


class PosDiscount(models.Model):
    _name = 'joyeria.pos.discount'
    _description = 'Descuento autorizado POS'

    name = fields.Char("Código", required=True, copy=False, default="Nuevo")
    
    tipo_descuento = fields.Selection([
        ('porcentaje', 'Porcentaje'),
        ('monto', 'Monto fijo')
    ], string="Tipo descuento", required=True)

    porcentaje = fields.Selection([
        ('5', '5%'),
        ('10', '10%'),
        ('15', '15%'),
        ('20', '20%'),
        ('25', '25%'),
        ('30', '30%'),
        ('35', '35%'),
        ('40', '40%'),
        ('45', '45%'),
        ('50', '50%')
    ], string="Porcentaje")

    monto = fields.Float("Monto")

    activo = fields.Boolean("Activo", default=True)

    usado = fields.Boolean("Usado", default=False)

    fecha_creacion = fields.Datetime(
        "Fecha creación",
        default=fields.Datetime.now
    )

    def generar_codigo(self):
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return codigo

    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.generar_codigo()
        return super().create(vals)