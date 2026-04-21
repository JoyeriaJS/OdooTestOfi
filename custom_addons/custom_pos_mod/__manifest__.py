{
    'name': 'Custom POS Mod',
    'version': '1.0',
    'summary': 'Modificaciones al Punto de Venta',
    'author': 'Tu Nombre',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_custom_templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'custom_pos_mod/static/src/js/custom_pos.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
