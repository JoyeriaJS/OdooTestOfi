{
    'name': "Cargos entre Locales por Traspasos",
    'version': '1.0',
    'depends': ['stock', 'base', 'product', 'sale', 'contacts', 'sale_management',],
    'author': "DR",
    'category': 'Inventory',
    'description': 'Reporte de cargos entre locales a través de traspasos internos',
    'data': [

        'security/ir.model.access.csv',
        'report/stock_transfer_charge_report_action.xml',
        'report/stock_transfer_charge_report_templates.xml',
        'report/report_product_label_templates.xml',
    ],

    
    'installable': True,
    'application': False,
}
