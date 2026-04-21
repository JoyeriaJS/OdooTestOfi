{
    'name': 'POS QR Auth - No Wizard',
    'version': '1.0',
    'author': 'Joyería Sebastián',
    'category': 'Point of Sale',
    'license': 'AGPL-3',
    'depends': ['point_of_sale', 'joyeria_reparaciones'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_qr_auth_views.xml',
        'views/report_rma_pos.xml',
    ],
    'assets': {
        'point_of_sale.assets_backend': [
            'pos_qr_auth_no_wizard/static/src/js/qr_auth.js',
        ],
    },
    'installable': True,
    'application': False,
}