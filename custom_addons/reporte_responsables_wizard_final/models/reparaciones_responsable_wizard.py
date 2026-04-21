from odoo import models, fields

class ReparacionesResponsableWizard(models.TransientModel):
    _name = "reparaciones.responsable.wizard"
    _description = "Wizard para reporte por responsable"

    responsable = fields.Many2one('res.users', string="Responsable", required=True)
    fecha_inicio = fields.Date(string="Fecha inicio", required=True)
    fecha_fin = fields.Date(string="Fecha fin", required=True)

    def imprimir_pdf(self):
        data = {
            'responsable_id': self.responsable.id,
            'responsable_name': self.responsable.name,
            'fecha_inicio': str(self.fecha_inicio),
            'fecha_fin': str(self.fecha_fin),
        }
        return self.env.ref('reporte_responsables_wizard_final.action_reporte_responsable_pdf_action').report_action(self, data=data)


                            
                        