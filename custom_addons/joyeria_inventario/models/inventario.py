from odoo import models, fields

class InventarioJoyeria(models.Model):
    _name = 'joyeria.inventario'
    _description = 'Resumen de Inventario Joyería'

    name = fields.Char(string='Nombre', required=True)
    sucursal = fields.Char(string='Sucursal')
    tipo = fields.Selection([
        ('recepcion', 'Recepciones'),
        ('entrega', 'Órdenes de entrega'),
        ('transferencia', 'Transferencias internas')
    ], string='Tipo de operación', required=True)

    estado = fields.Selection([
        ('a_procesar', 'A Procesar'),
        ('en_espera', 'En espera'),
        ('retrasado', 'Retrasado'),
        ('completado', 'Completado')
    ], string='Estado', default='a_procesar')

    cantidad = fields.Integer(string='Cantidad a procesar', default=0)

    codigo = fields.Char(string='Código Interno')
    precio_compra = fields.Float(string='Precio de compra')
    precio_sugerido = fields.Float(string='Precio sugerido')
    descripcion = fields.Text(string='Descripción')
    foto = fields.Binary(string='Foto del producto', attachment=True)
