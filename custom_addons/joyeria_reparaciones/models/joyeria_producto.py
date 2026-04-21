from odoo import models, fields

class JoyeriaProducto(models.Model):
    _name = 'joyeria.producto'
    _description = 'Producto exclusivo de la joyería'

    name = fields.Char(string='Nombre del producto', required=True)
    descripcion = fields.Text(string='Descripción')
    tipo = fields.Selection([
        ('anillo', 'Anillo'),
        ('collar', 'Collar'),
        ('pulsera', 'Pulsera'),
        ('otro', 'Otro'),
    ], string='Tipo de joya', default='otro')
    metal = fields.Char(string='Metal')
    peso = fields.Float(string='Peso (g)')
    modelo = fields.Char(string='Modelo')
    precio_unitario = fields.Float(string='Precio unitario', tracking=True)
    
    imagen = fields.Image(string='Imagen del producto')
