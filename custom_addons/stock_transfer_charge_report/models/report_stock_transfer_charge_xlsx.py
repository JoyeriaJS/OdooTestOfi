# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import AccessError

class ReportStockTransferChargeXlsx(models.AbstractModel):
    _name = 'report.stock_transfer_charge_report.stock_transfer_charge_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Cargos entre locales (Excel)'

    def generate_xlsx_report(self, workbook, data, pickings):
        # Verificar permisos
        if not self.env.user.has_group('base.group_system'):
            raise AccessError("Sólo los administradores pueden generar este reporte.")

        # Formatos
        bold  = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})

        # Crear hoja
        sheet = workbook.add_worksheet("Cargos Locales")

        # Encabezados con Origen y Destino
        headers = [
            'Picking', 'Origen', 'Destino', 'Producto', 'Cantidad',
            'UoM', 'Peso (g)', 'Precio Interno', 'Costo Interno'
        ]
        for col, title in enumerate(headers):
            sheet.write(0, col, title, bold)

        # Construir mapeo de precios internos
        pricelist = self.env['product.pricelist'].search(
            [('name', 'ilike', 'Interno (CLP)')], limit=1)
        precios_interno = {}
        if pricelist:
            items = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', pricelist.id),
                ('applied_on', 'in', ['0_product_variant', '1_product']),
            ])
            for item in items:
                price = item.fixed_price or 0.0
                if item.applied_on == '0_product_variant' and item.product_id:
                    precios_interno[item.product_id.id] = price
                elif item.applied_on == '1_product' and item.product_tmpl_id:
                    for var in item.product_tmpl_id.product_variant_ids:
                        precios_interno[var.id] = price

        # Filas y totales por traspaso
        row = 1
        for pick in pickings:
            total_cost = 0.0
            total_weight = 0.0
            for ml in pick.move_line_ids_without_package:
                qty = ml.quantity or 0.0
                weight = (ml.product_id.weight or 0.0) * qty
                unit_price = precios_interno.get(ml.product_id.id, 0.0)
                cost = qty * unit_price
                total_cost += cost
                total_weight += weight

                sheet.write(row, 0, pick.name)
                sheet.write(row, 1, pick.location_id.display_name)
                sheet.write(row, 2, pick.location_dest_id.display_name)
                sheet.write(row, 3, ml.product_id.display_name)
                sheet.write_number(row, 4, qty)
                sheet.write(row, 5, ml.product_uom_id.name)
                sheet.write_number(row, 6, weight)
                sheet.write_number(row, 7, unit_price, money)
                sheet.write_number(row, 8, cost, money)
                row += 1

            # Fila de totales del picking
            sheet.write(row, 0, f"Total {pick.name}", bold)
            sheet.write_number(row, 6, total_weight)
            sheet.write_number(row, 8, total_cost, money)
            row += 2  # espacio antes del siguiente traspaso

        # Ajustar ancho de columnas
        for idx in range(len(headers)):
            sheet.set_column(idx, idx, 18)