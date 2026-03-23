from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    gramos = fields.Char(string="Gramos")
    descripcion_personalizada = fields.Char(string="Descripción Personalizada")

    gasto_nombre = fields.Char(string="Nombre Gasto")
    gasto_descripcion = fields.Char(string="Descripción Gasto")
    es_producto_gasto = fields.Boolean(string="Es Producto Gasto")
    precio_bloqueado = fields.Float(string="Precio Bloqueado")

    numero_rma = fields.Char(string="Número RMA")
    precio_original_rma = fields.Float(string="Precio Original RMA")
    subtotal_rma = fields.Float(string="Subtotal RMA")
    abono_rma = fields.Float(string="Abono RMA")
    saldo_rma = fields.Float(string="Saldo RMA")
    es_linea_rma_principal = fields.Boolean(string="Es línea RMA principal")
    es_linea_rma_aux = fields.Boolean(string="Es línea RMA auxiliar")
    tipo_linea_rma = fields.Char(string="Tipo línea RMA")

    @api.model
    def _order_line_fields(self, line, session_id=None):
        result = super()._order_line_fields(line, session_id)

        # En Odoo 17 result normalmente es [0, 0, {vals}]
        if isinstance(result, list) and len(result) >= 3:
            values = result[2]
            if isinstance(values, dict):

                if isinstance(line, (list, tuple)) and len(line) >= 3:
                    ui_values = line[2]
                    if isinstance(ui_values, dict):
                        values['gramos'] = ui_values.get('gramos')
                        values['descripcion_personalizada'] = ui_values.get('descripcion_personalizada')

                        values['gasto_nombre'] = ui_values.get('gasto_nombre')
                        values['gasto_descripcion'] = ui_values.get('gasto_descripcion')
                        values['es_producto_gasto'] = ui_values.get('es_producto_gasto', False)
                        values['precio_bloqueado'] = ui_values.get('precio_bloqueado', 0.0)

                        values['numero_rma'] = ui_values.get('numero_rma')
                        values['precio_original_rma'] = ui_values.get('precio_original_rma', 0.0)
                        values['subtotal_rma'] = ui_values.get('subtotal_rma', 0.0)
                        values['abono_rma'] = ui_values.get('abono_rma', 0.0)
                        values['saldo_rma'] = ui_values.get('saldo_rma', 0.0)
                        values['es_linea_rma_principal'] = ui_values.get('es_linea_rma_principal', False)
                        values['es_linea_rma_aux'] = ui_values.get('es_linea_rma_aux', False)
                        values['tipo_linea_rma'] = ui_values.get('tipo_linea_rma')

        return result