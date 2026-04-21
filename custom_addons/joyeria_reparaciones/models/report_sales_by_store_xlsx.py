# -*- coding: utf-8 -*-
from odoo import api, models
from collections import OrderedDict
from odoo.exceptions import AccessError

class ReportSalesByStoreXlsx(models.AbstractModel):
    _name = 'report.joyeria_reparaciones.report_sales_by_store_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Ventas por Tienda y Mes (Excel)'

    def generate_xlsx_report(self, workbook, data, records):
        # Sólo admins
        if not self.env.user.has_group('base.group_system'):
            raise AccessError("Sólo los administradores pueden generar este reporte.")

        # filtramos sólo los que tienen fecha de firma
        recs = records.filtered(lambda r: r.fecha_firma)
        # agrupamos por (tienda, año, mes)
        groups = OrderedDict()
        for r in recs:
            store = r.local_tienda or 'Sin Tienda'
            dt = r.fecha_firma
            key = (store, dt.year, dt.month)
            groups.setdefault(key, []).append(r)

        # formateos
        bold  = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        datef = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        sheet = workbook.add_worksheet("Ventas x Tienda")
        row = 0

        for (store, year, month), recs in groups.items():
            # título del grupo
            sheet.write(row, 0, f"{store} — {month:02d}/{year}", bold)
            row += 1
            # cabeceras
            headers = [
                "RMA", "Fecha Firma",
                "Metal Utilizado", "Gramos Utilizado",
                "Cobro Interno", "Hechura",
                "Cobros Extras", "Pago a Taller"
            ]
            for col, h in enumerate(headers):
                sheet.write(row, col, h, bold)
            row += 1

            # totales mensuales
            tot_gramos = tot_ci = tot_he = tot_ce = tot_pago = 0.0

            for r in recs:
                gramos = getattr(r, 'gramos_utilizado', None) or getattr(r, 'peso_total', 0.0)
                ci     = r.cobro_interno or 0.0
                he     = r.hechura       or 0.0
                ce     = r.cobros_extras or 0.0
                pago   = ci + he + ce

                # acumular
                tot_gramos += gramos
                tot_ci     += ci
                tot_he     += he
                tot_ce     += ce
                tot_pago   += pago

                # escribir fila
                sheet.write(row, 0, r.name)
                sheet.write_datetime(row, 1, r.fecha_firma, datef)
                sheet.write(row, 2, r.metal_utilizado or "")
                sheet.write_number(row, 3, gramos, money)
                sheet.write_number(row, 4, ci, money)
                sheet.write_number(row, 5, he, money)
                sheet.write_number(row, 6, ce, money)
                sheet.write_number(row, 7, pago, money)
                row += 1

            # fila de totales
            sheet.write(row, 0, "Total del mes:", bold)
            sheet.write_number(row, 3, tot_gramos, money)
            sheet.write_number(row, 4, tot_ci,     money)
            sheet.write_number(row, 5, tot_he,     money)
            sheet.write_number(row, 6, tot_ce,     money)
            sheet.write_number(row, 7, tot_pago,   money)
            row += 2  # espacio antes del siguiente grupo

        # autoajustar columnas
        for col in range(len(headers)):
            sheet.set_column(col, col, 18)
