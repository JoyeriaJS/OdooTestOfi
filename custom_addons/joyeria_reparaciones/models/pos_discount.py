from odoo import models, fields, api
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
    metodos_pago_ids = fields.Many2many(
    'pos.payment.method',
    string="Métodos de pago permitidos"
    )

    def generar_codigo(self):
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return codigo

    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.generar_codigo()
        return super().create(vals)
    
    @api.model
    def validar_descuento(self, codigo):
        descuento = self.search([
            ('name', '=', codigo),
            ('activo', '=', True),
            ('usado', '=', False)
        ], limit=1)

        if not descuento:
            return False

        return {
            'id': descuento.id,  # 🔥 IMPORTANTE
            'tipo_descuento': descuento.tipo_descuento,
            'porcentaje': descuento.porcentaje,
            'monto': descuento.monto,
            'metodos_pago_ids': descuento.metodos_pago_ids.ids,
        }
    
    @api.model
    def usar_descuento(self, descuento_id):
        descuento = self.browse(descuento_id)
        if descuento and not descuento.usado:
            descuento.usado = True