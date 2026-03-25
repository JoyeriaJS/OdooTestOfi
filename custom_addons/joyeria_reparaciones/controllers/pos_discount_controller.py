from odoo import http
from odoo.http import request

class PosDiscountController(http.Controller):

    @http.route('/pos/validar_descuento', type='json', auth='user')
    def validar_descuento(self, codigo):

        descuento = request.env['joyeria.pos.discount'].sudo().search([
            ('name', '=', codigo),
            ('activo', '=', True),
            ('usado', '=', False),
        ], limit=1)

        if not descuento:
            return False

        return {
            'id': descuento.id,
            'tipo_descuento': descuento.tipo_descuento,
            'porcentaje': descuento.porcentaje,
            'monto': descuento.monto,

            # 🔥 ESTO ES LO QUE TE FALTA
            'metodos_pago_nombres': descuento.metodos_pago_ids.mapped('name'),
        }