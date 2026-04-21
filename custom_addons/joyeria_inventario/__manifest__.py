{
    'name': 'Inventario Joyería',
    'version': '1.0',
    'summary': 'Gestión de inventario por locales',
    'description': 'Módulo personalizado para controlar inventario en locales de joyería.',
    'author': 'DR',
    'depends': ['base',  'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inventario_views.xml',
        'views/inventario_dashboard.xml',
        'views/joyeria_inventario_menu.xml',
        #'views/cargar_csv_view.xml',  # NUEVO
    ],
    'installable': True,
    'application': True,
}
