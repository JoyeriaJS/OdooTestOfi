from odoo import models, fields, api
from datetime import date

class SalidaTallerWizard(models.TransientModel):
    _name = 'salida.taller.wizard'
    _description = 'Reporte de salida del taller'

    fecha_inicio = fields.Date(string='Fecha inicio', required=True, default=lambda self: date.today().replace(day=1))
    fecha_fin = fields.Date(string='Fecha fin', required=True, default=lambda self: date.today())

    def imprimir_pdf(self):
        data = {
            'fecha_inicio': str(self.fecha_inicio),
            'fecha_fin': str(self.fecha_fin),
        }
        return self.env.ref('joyeria_reporte_salida_taller.action_salida_taller_pdf').report_action(self, data=data)

        

                            

