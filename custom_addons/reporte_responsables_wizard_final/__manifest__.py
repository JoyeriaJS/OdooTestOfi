
{
    'name': 'Reporte Responsables Wizard3',
    'version': '1.0',
    'depends': ['base', 'web'],
    'data': [
        'views/reparaciones_responsable_wizard_action.xml',
        'security/ir.model.access.csv',
        'views/reparaciones_responsable_wizard_view.xml',
        'report/reporte_responsable_pdf_action.xml',
        'report/reparaciones_responsable_template.xml',
    ],
    'application': False,
}
