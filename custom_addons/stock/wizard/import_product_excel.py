from odoo import models, fields, api
import base64
import pandas as pd
from io import BytesIO

class ImportProductExcelWizard(models.TransientModel):
    _name = 'wizard.import.product.excel'
    _description = 'Wizard para importar productos desde Excel'

    file_excel = fields.Binary("Archivo Excel", required=True)
    file_name = fields.Char("Nombre del archivo")

    def action_import(self):
        if not self.file:
            return

        data = base64.b64decode(self.file)
        df = pd.read_excel(BytesIO(data), sheet_name='Productos')  # Cambia el nombre de la hoja si es necesario

        for i, row in df.iterrows():
            self.env['product.template'].create({
                'name': row.get('Nombre', ''),
                'default_code': row.get('CodJS', ''),
                'barcode': row.get('CodBar', ''),
                'list_price': row.get('Tarifa Pública', 0),
                'standard_price': row.get('Costo', 0),
                # Agrega aquí más campos según tu modelo y tus columnas
            })
