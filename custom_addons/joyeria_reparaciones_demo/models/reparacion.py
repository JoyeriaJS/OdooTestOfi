from odoo import models, fields

class JoyeriaReparacion(models.Model):
    _name = 'joyeria.reparacion'
    _description = 'Orden de Reparacion Demo'

    name = fields.Char('RMA', required=True, default='Nuevo')
    peso_valor = fields.Float('Peso')
    metales_extra = fields.Float('Metales Extra')
    metal_utilizado = fields.Selection([
        ('oro 18k rosado', 'Oro 18k Rosado'),
        ('oro 18k amarillo', 'Oro 18k Amarillo'),
    ], string='Metal Utilizado')
