
{
    'name': 'Importador Inventario Joyería',
    'version': '1.0',
    'summary': 'Importa productos desde Excel al stock estándar de Odoo',
    'category': 'Inventory',
    'author': 'Joyería Sebastián',
    'depends': ['stock','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/import_product_btn.xml',
        'wizard/importar_productos_wizard.xml',
    ],
    'installable': True,
    'application': False,
}
