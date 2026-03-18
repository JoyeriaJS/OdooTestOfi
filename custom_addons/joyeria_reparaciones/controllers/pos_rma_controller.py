from odoo import http
from odoo.http import request


class PosRMAController(http.Controller):

    @http.route('/pos/buscar_rma', type='json', auth='user')
    def buscar_rma(self, **kwargs):

        numero_rma = kwargs.get("numero_rma")

        if not numero_rma:
            return {"error": "Debe ingresar un número de RMA"}

        numero_rma = numero_rma.strip().upper()

        if not numero_rma.startswith("RMA/"):
            numero_rma = f"RMA/{numero_rma.zfill(5)}"

        reparacion = request.env['joyeria.reparacion'].sudo().search([
            ('name', '=', numero_rma)
        ], limit=1)

        if not reparacion:
            return {"error": f"El RMA {numero_rma} no existe"}

        subtotal = reparacion.subtotal or 0
        abono = reparacion.abono or 0
        saldo = subtotal - abono

        if saldo <= 0:
            return {
                "error": f"El RMA {numero_rma} no tiene saldo pendiente"
            }

        return {
            "success": True,
            "rma": reparacion.name,

            # 🔥 ESTO ES LO QUE TE FALTABA
            "subtotal": subtotal,
            "abono": abono,
            "saldo": saldo,

            # 🔥 precio del POS
            "precio": saldo,
        }