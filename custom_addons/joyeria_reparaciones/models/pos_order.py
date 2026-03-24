from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    vendedora_id = fields.Many2one(
        'joyeria.vendedora',
        string='Vendedora'
    )

    @api.model
    def _order_fields(self, ui_order):
        result = super()._order_fields(ui_order)
        result['vendedora_id'] = ui_order.get('vendedora_id')
        return result

    def export_for_ui(self):
        result = super().export_for_ui()

        for order in result:
            pos_order = self.browse(order['id'])
            order['vendedora_name'] = pos_order.vendedora_id.name if pos_order.vendedora_id else ""

        return result

    # ==========================================
    # CAMPOS PARA EXPORTAR MÉTODOS DE PAGO
    # ==========================================

    total_efectivo = fields.Float(
        string="Total Efectivo",
        compute="_compute_totales_pago",
        store=True
    )

    total_banco = fields.Float(
        string="Total Banco",
        compute="_compute_totales_pago",
        store=True
    )

    total_cuenta_cliente = fields.Float(
        string="Total Cuenta de Cliente",
        compute="_compute_totales_pago",
        store=True
    )

    total_venta_neto_efectivo = fields.Float(
        string="Total Venta Neto Efectivo",
        compute="_compute_totales_pago",
        store=True
    )

    total_venta_neto_transferencia = fields.Float(
        string="Total Venta Neto Transferencia",
        compute="_compute_totales_pago",
        store=True
    )

    total_venta_neto_credito = fields.Float(
        string="Total Venta Neto Tarjeta de Crédito",
        compute="_compute_totales_pago",
        store=True
    )

    total_venta_efectivo = fields.Float(
        string="Total Venta Efectivo",
        compute="_compute_totales_pago",
        store=True
    )

    total_venta_credito = fields.Float(
        string="Total Venta Tarjeta Credito",
        compute="_compute_totales_pago",
        store=True
    )

    total_venta_transferencia = fields.Float(
        string="Total Venta Transferencia",
        compute="_compute_totales_pago",
        store=True
    )

    @api.depends('payment_ids.amount', 'payment_ids.payment_method_id')
    def _compute_totales_pago(self):

        for order in self:

            efectivo = 0
            banco = 0
            cuenta_cliente = 0
            venta_neto_efectivo = 0
            venta_neto_transferencia = 0
            venta_neto_credito = 0
            venta_efectivo = 0
            venta_credito = 0
            venta_transferencia = 0

            for payment in order.payment_ids:

                metodo = payment.payment_method_id.name

                if metodo == "Efectivo":
                    efectivo += payment.amount

                elif metodo == "Banco":
                    banco += payment.amount

                elif metodo == "Cuenta de cliente":
                    cuenta_cliente += payment.amount

                elif metodo == "Venta Neto Efectivo":
                    venta_neto_efectivo += payment.amount

                elif metodo == "Venta Neto Transferencia":
                    venta_neto_transferencia += payment.amount

                elif metodo == "Venta Neto Tarjeta de Crédito":
                    venta_neto_credito += payment.amount

                elif metodo == "Venta Efectivo":
                    venta_efectivo += payment.amount

                elif metodo == "Venta Tarjeta Credito":
                    venta_credito += payment.amount

                elif metodo == "Venta Transferencia":
                    venta_transferencia += payment.amount

            order.total_efectivo = efectivo
            order.total_banco = banco
            order.total_cuenta_cliente = cuenta_cliente
            order.total_venta_neto_efectivo = venta_neto_efectivo
            order.total_venta_neto_transferencia = venta_neto_transferencia
            order.total_venta_neto_credito = venta_neto_credito
            order.total_venta_efectivo = venta_efectivo
            order.total_venta_credito = venta_credito
            order.total_venta_transferencia = venta_transferencia

    @api.model
    def create_from_ui(self, orders, draft=False):
        result = super().create_from_ui(orders, draft=draft)

        Reparacion = self.env['joyeria.reparacion']

        for order_data in orders:
            data = order_data.get('data', {})
            pos_reference = data.get('name')

            pos_order = self.search([('pos_reference', '=', pos_reference)], limit=1)
            if not pos_order:
                continue

            for line in pos_order.lines:
                if not line.es_linea_rma_principal:
                    continue

                if not line.numero_rma:
                    continue

                reparacion = Reparacion.search([('name', '=', line.numero_rma)], limit=1)
                if not reparacion:
                    continue

                saldo_pagado = float(line.saldo_rma or 0.0)
                if saldo_pagado <= 0:
                    continue

                nuevo_abono = float(reparacion.abono or 0.0) + saldo_pagado

                reparacion.write({
                    'abono': nuevo_abono,
                })

        return result