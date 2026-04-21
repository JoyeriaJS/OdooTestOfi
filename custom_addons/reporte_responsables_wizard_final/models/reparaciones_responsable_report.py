from odoo import models, api

class ReparacionesResponsableReport(models.AbstractModel):
    _name = 'report.reporte_responsables_wizard_final.reparaciones_responsable_template'
    _description = 'Reporte por responsable'

    @api.model
    def _get_report_values(self, docids, data=None):
        responsable_id = data.get('responsable_id')
        responsable_name = data.get('responsable_name')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        Reparacion = self.env['joyeria.reparacion']
        domain = [
            ('responsable_id', '=', responsable_id),
            ('fecha_entrega', '>=', fecha_inicio),
            ('fecha_entrega', '<=', fecha_fin),
        ]
        reparaciones = Reparacion.sudo().search(domain, order='fecha_entrega desc') or Reparacion.browse([])

        return {
            'responsable_name': responsable_name,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'reparaciones': reparaciones,
        }
