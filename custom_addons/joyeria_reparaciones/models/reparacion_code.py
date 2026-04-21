from odoo import models, fields, api
import secrets
from datetime import datetime

class ReparacionAuthorizationCode(models.Model):
    _name = 'joyeria.reparacion.code'
    _description = 'Códigos de autorización para reparaciones sin costo'
    _rec_name = 'codigo'

    codigo = fields.Char(string="Código de autorización", required=True, readonly=True)
    fecha_generado = fields.Datetime(default=lambda self: fields.Datetime.now(), readonly=True)
    used = fields.Boolean(string="Usado", default=False, readonly=True)
    reparacion_id = fields.Many2one("joyeria.reparacion", string="Reparación vinculada", readonly=True)

    @api.model
    def generar_codigo(self):
        """Genera un código aleatorio único"""
        code = secrets.token_hex(3).upper()  # ej: 9AF3C1
        return self.create({"codigo": code})
