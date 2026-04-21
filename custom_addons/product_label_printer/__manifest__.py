# -*- coding: utf-8 -*-
{
    "name": "Product Label Printer",
    "version": "1.0",
    "summary": "Imprime etiquetas de 2×2 cm con código de barras para productos",
    "author": "Tu Empresa",
    "category": "Inventory",
    "depends": ["base", "stock"],
    "data": [
        "views/report_product_label_templates.xml",
        "views/report_product_label_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
