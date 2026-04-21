{
    'name': 'Reporte Salida Taller Joyería',
    'version': '1.0',
    'summary': 'Reporte con suma de salidas del taller por rango de fechas',
    'author': 'DR',
    'category': 'Operations',
    'depends': ['base', 'joyeria_reparaciones'],
    'data': [
        'security/ir.model.access.csv',
        'views/salida_taller_wizard_view.xml',
        'report/salida_taller_template.xml',
        'report/report.xml',
        
    ],
    'installable': True,
    'application': False,
}
