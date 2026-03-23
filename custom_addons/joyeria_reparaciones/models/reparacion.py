from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import base64
import re  
import qrcode
from datetime import datetime
from io import BytesIO
import uuid
import logging
import pytz
from  pytz import utc
from pytz import timezone
from datetime import datetime, timedelta
import unicodedata


CHILE_TZ = pytz.timezone('America/Santiago')

class Reparacion(models.Model):
    _name = 'joyeria.reparacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # 👈 Esto habilita el historial
    _description = 'Reparación de Joyería'
    partner_id = fields.Many2one('res.partner', string="Cliente")
    

    name = fields.Char(
        string='Referencia de reparación',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo'
    )
    producto_id = fields.Many2one('joyeria.producto', string='Producto a reparar', required=False)
    
    # Código que ingresa la vendedora
    codigo_ingresado = fields.Char(
        string="Código ingresado",
        help="Código entregado por administración.",
        store=True
)


    # Código generado por administración
    auth_code_id = fields.Many2one(
        "joyeria.reparacion.authcode",
        string="Código seleccionado por administración",
        domain="[('used','=',False)]",
        groups="base.group_system",  # solo admins lo ven
    )


    requiere_autorizacion = fields.Boolean(
        string="Requiere autorización",
        compute="_compute_requiere_autorizacion",
        store=True
)
    codigo_autorizacion_id = fields.Many2one(
    "joyeria.reparacion.authcode",
    string="Código autorizado",
    readonly=True
)
    costo_cero_definitivo = fields.Boolean(
    string="Es RMA sin costo",
    default=False,
    readonly=True
)


    modelo = fields.Char(string='Modelo', required=False)
    cliente_id = fields.Many2one('res.partner', string='Nombre y apellido del Cliente', required=True)
    nombre_cliente = fields.Char(string='Nombre y apellido del cliente', required=False)
    apellido_cliente = fields.Char(string="Apellido del cliente", required=False)
    correo_cliente = fields.Char(string="Correo electrónico")
    telefono = fields.Char(string='Teléfono', required=True)
    direccion_entrega = fields.Selection([
        ('local 345', 'Paseo Estado 344, Local 345, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 906', 'Paseo Estado 344, Local 906, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 392', 'Paseo Estado 344, Local 392, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 329', 'Paseo Estado 344, Local 329, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 325', 'Paseo Estado 344, Local 325, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 383 online', 'Paseo Estado 344, Local 383 Online, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 921', 'Paseo Estado 344, Local 921, Santiago Centro, Metro Plaza de Armas (Galería Pasaje Matte)'),
        ('local 584', 'Monjitas 873, Local 584, Santiago Centro, Metro Plaza de Armas'),
        ('local maipu', 'Jumbo, Av. Los Pajaritos 3302 (Local Maipú), Metro Santiago Bueras')
    ], string='Dirección de entrega', required=True)
    vencimiento_garantia = fields.Date(string='Vencimiento de la garantía',compute='_compute_vencimiento_garantia',store=True)
    fecha_entrega = fields.Date(string='Fecha de entrega', tracking=True)
    responsable_id = fields.Many2one('res.users', string="Responsable", default=False, tracking=True)
    fecha_retiro = fields.Datetime(string='Fecha y hora de retiro', tracking=True)
    fecha_recepcion = fields.Datetime(
        string="Fecha de recepción",
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )

    tipo_cliente= fields.Selection([
        ('cliente normal', 'Cliente Normal'),
        ('cliente mayorista', 'Cliente Mayorista'),
        ('cliente preferente', 'Cliente Preferente')

    ], string='Tipo Cliente', required=True, tracking=True)

    tipo_joya = fields.Selection([
        ('anillo', 'Anillo'),
        ('argolla', 'Argolla'),
        ('aros', 'Aros'),
        ('cadena', 'Cadena'),
        ('colgante', 'Colgante'),
        ('pulsera', 'Pulsera'),
        ('otro', 'Otro')
    ], string='Tipo de joya', required=True)
    
    metal = fields.Selection([
        ('oro 14k', 'Oro 14K'),
        ('oro 18k rosado', 'Oro 18K Rosado'),
        ('oro 18k amarillo', 'Oro 18K Amarillo'),
        ('oro 18k blanco', 'Oro 18K Blanco'),
        ('oro 18k multi', 'Oro 18K Multi'), 
        ('plata', 'Plata'),
        ('plata con oro', 'Plata con Oro'),
        ('plata con oro 18k', 'Plata con Oro 18K'),
        ('platino', 'Platino'),
        ('otros', 'Otros')
    ], string='Metal Fabricación', required=True, tracking=True)
    
    peso = fields.Selection([
        ('estandar', 'Estándar'),
        ('especial', 'Especial')
    ], string='Tipo de peso', required=True, tracking=True)
    peso_valor = fields.Float(string='Peso', required=False, tracking=True)
    vendedora_id= fields.Many2one('joyeria.vendedora', string='Recibido por', readonly=True, tracking=True)
    servicio = fields.Selection([
        ('reparacion', 'Reparación'),
        ('fabricacion', 'Fabricación')
    ], string='Servicio', required=True, tracking=True)
    solicitud_cliente = fields.Text(string='Solicitud del cliente', tracking=True, required=True)
    #producto_recibido_por = fields.Char(string='Recibido por', tracking=True)
    #unidades = fields.Selection([
    #    ('gr', 'Gramo'),
     #   ('kg', 'Kilogramo'),
    #], string='Unidades', required=True)
    n_cm_reparacion = fields.Char(string='N° CM Reparación')
    n_cm_fabricacion = fields.Char(string='N° CM Fabricación')
    cantidad = fields.Float(string='Cantidad', required=True, tracking=True)
    local_tienda = fields.Selection([
        ('local 345', 'Local 345'),
        ('local 906', 'Local 906'),
        ('local 584', 'Local 584'),
        ('local 392', 'Local 392'),
        ('local 329', 'Local 329'),
        ('local 325', 'Local 325'),
        ('local 383 online', 'Local 383 Online'),
        ('local maipu', 'Local Maipú'),
        ('local 921', 'Local 921'),
    ], string='Tienda', required=True)
    precio_unitario = fields.Float(string='Precio unitario', tracking=True)
    extra = fields.Float(string='Extra', tracking=True)
    extra2 = fields.Float(string='Extra 2', tracking=True)
    extra3 = fields.Float(string='Extra 3', tracking=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    abono = fields.Float(string='Abono', tracking=True,)
    saldo = fields.Float(string="Saldo", compute='_compute_saldo', store=True)

    express = fields.Boolean(string='Express', tracking=True)
    qr = fields.Binary(string='Código QR', attachment=True)
    notas = fields.Text(string='Notas')
    comentarios = fields.Text(string="Comentarios")

    lineas_operacion_ids = fields.One2many(
        'joyeria.operacion', 'reparacion_id', string='Operaciones')

    estado = fields.Selection([
        ('presupuesto', 'Presupuesto'),
        ('reparado', 'Reparado'),
        ('reparado y entregado', 'Reparado y Entregado'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='presupuesto', tracking=True, required=True, store=True, readonly=False)
    descripcion_extra_1 = fields.Char()
    descripcion_extra_2 = fields.Char()
    descripcion_extra_3 = fields.Char()

    clave_autenticacion_manual = fields.Char(string='QR de quien recibe', required=True)

    # NUEVOS CAMPOS
    metal_utilizado = fields.Selection([
        ('oro 14k', 'Oro 14K'),
        ('oro 18k rosado', 'Oro 18K Rosado'),
        ('oro 18k amarillo', 'Oro 18K Amarillo'),
        ('oro 18k blanco', 'Oro 18K Blanco'),
        ('oro 18k multi', 'Oro 18K Multi'), 
        ('plata', 'Plata'),
        ('plata con oro', 'Plata con Oro'),
        ('plata con oro 18k', 'Plata con Oro 18K'),
        ('platino', 'Platino'),
        ('otros', 'Otros')
    ], string='Metal utilizado')
    
    gramos_utilizado = fields.Float("Gramos utilizados(gr)")


    metales_extra = fields.Float("Metales extra(gr)")

    cobro_interno = fields.Float("Cobro interno")
    hechura = fields.Float("Hechura")
    hechura2 = fields.Float("Hechura")
    cobros_extras = fields.Float("Cobros extras")
    total_salida_taller = fields.Float("Total salida del taller", compute="_compute_total_salida", store=True)
    peso_total = fields.Float("Peso total", compute="_compute_peso_total", store=True)

        # ==============================
    # CAMPOS FORMULARIO POR METAL
    # ==============================

    # PLATA
    plata_diseno = fields.Boolean(string="Diseño")
    plata_casting = fields.Boolean(string="Casting")
    plata_piedras = fields.Boolean(string="Piedras")
    plata_cantidad_piedras = fields.Integer(string="Cantidad piedras")
    plata_total = fields.Float(string="Total Plata", compute="_compute_total_plata", store=True)


    # ORO AMARILLO
    oro_amarillo_diseno = fields.Boolean(string="Diseño")
    oro_amarillo_casting = fields.Boolean(string="Casting")
    oro_amarillo_piedras = fields.Boolean(string="Piedras")
    oro_amarillo_cantidad_piedras = fields.Integer(string="Cantidad piedras")
    oro_amarillo_total = fields.Float(string="Total Oro Amarillo", compute="_compute_total_oro_amarillo", store=True)


    # ORO ROSADO
    oro_rosado_diseno = fields.Boolean(string="Diseño")
    oro_rosado_casting = fields.Boolean(string="Casting")
    oro_rosado_piedras = fields.Boolean(string="Piedras")
    oro_rosado_cantidad_piedras = fields.Integer(string="Cantidad piedras")
    oro_rosado_total = fields.Float(string="Total Oro Rosado", compute="_compute_total_oro_rosado", store=True)


    # OTROS METALES
    otros_casting = fields.Boolean(string="Casting")
    otros_piedras = fields.Boolean(string="Piedras")
    otros_cantidad_piedras = fields.Integer(string="Cantidad piedras")
    otros_total = fields.Float(string="Total Otros", compute="_compute_total_otros", store=True)


    #firma_salida_id = fields.Many2one('joyeria.vendedora', string="Firma salida del taller", readonly=True)
    #fecha_salida_taller = fields.Datetime("🕒 Fecha y hora de salida", readonly=True)
    firma_id = fields.Many2one('joyeria.vendedora', string='Retirado por', readonly=True, tracking=True)
    fecha_firma = fields.Datetime(string='Fecha de firma', readonly=True)
    clave_firma_manual = fields.Char(string='QR de quien retira')


    @api.depends('plata_diseno','plata_casting','plata_piedras','plata_cantidad_piedras')
    def _compute_total_plata(self):
        for r in self:
            total = 0
            if r.plata_diseno:
                total += 4000
            if r.plata_casting:
                total += 4000
            if r.plata_piedras:
                total += r.plata_cantidad_piedras * 300
            r.plata_total = total


    @api.depends('oro_amarillo_diseno','oro_amarillo_casting','oro_amarillo_piedras','oro_amarillo_cantidad_piedras')
    def _compute_total_oro_amarillo(self):
        for r in self:
            total = 0
            if r.oro_amarillo_diseno:
                total += 4000
            if r.oro_amarillo_casting:
                total += 4000
            if r.oro_amarillo_piedras:
                total += r.oro_amarillo_cantidad_piedras * 300
            r.oro_amarillo_total = total


    @api.depends('oro_rosado_diseno','oro_rosado_casting','oro_rosado_piedras','oro_rosado_cantidad_piedras')
    def _compute_total_oro_rosado(self):
        for r in self:
            total = 0
            if r.oro_rosado_diseno:
                total += 4000
            if r.oro_rosado_casting:
                total += 4000
            if r.oro_rosado_piedras:
                total += r.oro_rosado_cantidad_piedras * 300
            r.oro_rosado_total = total


    @api.depends('otros_casting','otros_piedras','otros_cantidad_piedras')
    def _compute_total_otros(self):
        for r in self:
            total = 0
            if r.otros_casting:
                total += 4000
            if r.otros_piedras:
                total += r.otros_cantidad_piedras * 300
            r.otros_total = total

    @api.depends('precio_unitario', 'extra', 'extra2', 'extra3', 'abono', 'saldo')
    def _compute_requiere_autorizacion(self):
        for rec in self:

            # Convertir None/False/vacío en 0
            precio_unitario = rec.precio_unitario or 0
            extra = rec.extra or 0
            extra2 = rec.extra2 or 0
            extra3 = rec.extra3 or 0
            abono = rec.abono or 0
            saldo = rec.saldo or 0

            # Solo requiere autorización si REALMENTE todo es 0
            rec.requiere_autorizacion = (
                precio_unitario == 0 and
                extra == 0 and
                extra2 == 0 and
                extra3 == 0 and
                abono == 0 and
                saldo == 0
            )



    @staticmethod
    def _normalize_name(name):
        """Normaliza el nombre: minúsculas, sin tildes, espacios simples."""
        if not name:
            return ''
        s = ''.join(c for c in unicodedata.normalize('NFKD', name) if not unicodedata.combining(c))
        s = s.lower()
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    @api.constrains('cliente_id')
    def _check_cliente_id_unique_name(self):
        """
        Valida que el cliente asignado en cliente_id no duplique el nombre
        de otro cliente (persona activa sin ser usuario del sistema).
        """
        for rec in self:
            cliente = rec.cliente_id
            if not cliente or not cliente.active or cliente.is_company:
                continue

            nombre_normalizado = rec._normalize_name(cliente.name)

            # Buscar otros partners con el mismo nombre canónico
            duplicates = self.env['res.partner'].search([
                ('id', '!=', cliente.id),
                ('active', '=', True),
                ('is_company', '=', False),
            ], limit=50)

            for dup in duplicates:
                if rec._normalize_name(dup.name) == nombre_normalizado:
                    # Si el duplicado tiene usuario, lo ignoramos (puede ser responsable del sistema)
                    tiene_usuario = self.env['res.users'].search_count([('partner_id', '=', dup.id)], limit=1)
                    if not tiene_usuario:
                        raise ValidationError(
                            "El cliente «%s» ya existe con el mismo nombre y apellido.\n"
                            "Por favor selecciona el cliente existente o combina los contactos."
                            % (dup.name,)
                        )


    @api.depends('fecha_recepcion')
    def _compute_vencimiento_garantia(self):
        for rec in self:
            if rec.fecha_recepcion:
                # Suma un mes exacto
                rec.vencimiento_garantia = \
                    (fields.Datetime.from_string(rec.fecha_recepcion)
                     + relativedelta(months=1)).date()
            else:
                rec.vencimiento_garantia = False


    @api.constrains('fecha_entrega', 'fecha_recepcion')
    def _check_fecha_entrega_no_anterior_a_recepcion(self):
        for record in self:
            if record.fecha_entrega and record.fecha_recepcion:
                fecha_recepcion_date = fields.Datetime.to_datetime(record.fecha_recepcion).date()

                if record.fecha_entrega < fecha_recepcion_date:
                    raise ValidationError(
                        _("La fecha de entrega no puede ser anterior a la fecha de recepción.")
                    )

    @api.onchange('fecha_entrega')
    def _onchange_fecha_entrega(self):
        if self.fecha_entrega and self.fecha_recepcion:
            fecha_recepcion_date = fields.Datetime.to_datetime(self.fecha_recepcion).date()

            if self.fecha_entrega < fecha_recepcion_date:
                self.fecha_entrega = False
                return {
                    'warning': {
                        'title': _('Fecha inválida'),
                        'message': _('La fecha de entrega no puede ser anterior a la fecha de recepción.'),
                    }
                }


    @api.onchange('express')
    def _onchange_express(self):
        if self.express:
            self.fecha_entrega = fields.Date.today()


    @api.onchange('local_tienda')
    def _onchange_local_tienda(self):
        for rec in self:
            if not rec.local_tienda:
                continue

            mapping = {
                "local 345": "local 345",
                "local 906": "local 906",
                "local 392": "local 392",
                "local 329": "local 329",
                "local 325": "local 325",
                "local 383 online": "local 383 online",
                "local 921": "local 921",
                "local 584": "local 584",
                "local maipu": "local maipu",
            }

            # Si existe la clave, la usa; si no, no rompe
            rec.direccion_entrega = mapping.get(rec.local_tienda)

    @api.onchange('responsable_id')
    def _onchange_responsable_id(self):
        if not self.env.user.has_group('base.group_system'):
            if self.responsable_id and self.responsable_id != self.env.user:
                raise UserError("No tienes permisos para modificar el campo 'Responsable'.")

    @api.onchange('clave_autenticacion_manual')
    def _onchange_clave_autenticacion_manual(self):
        """ Buscar vendedora por clave manual o por código QR escaneado y asignar automáticamente """
        if self.clave_autenticacion_manual:
            clave = self.clave_autenticacion_manual.strip().upper()
            vendedora = self.env['joyeria.vendedora'].search([
                '|',
                '|',
                ('clave_autenticacion', '=', clave),
                ('clave_qr', '=', clave),
                ('codigo_qr', '=', clave),
            ], limit=1)
            self.vendedora_id = vendedora.id if vendedora else False
        else:
            self.vendedora_id = False
    
    
    

    @api.onchange('responsable_id')
    def _onchange_responsable_auto_confirm_first_time(self):
        for rec in self:
            # Valor "persistido" antes del cambio (lo que hay en la BD)
            prev_tenía_responsable = bool(rec._origin.responsable_id) if rec._origin and rec._origin.id else False
            # Si no tenía responsable en BD y ahora sí se asignó, auto-confirmar
            if (not prev_tenía_responsable) and rec.responsable_id and rec.estado != 'confirmado':
                rec.estado = 'confirmado'
    
    @api.onchange('clave_firma_manual')
    def _onchange_firma_auto_entregado_first_time(self):
        for rec in self:
            # ¿Tenía firma antes en la BD?
            prev_tenia_firma = bool(rec._origin.firma_id) if rec._origin and rec._origin.id else False
            # Si ahora hay clave (se escaneó) y ya quedó asignada la firma (tu onchange actual la setea),
            # y antes NO tenía firma, entonces es la primera vez -> pasar a "reparado y entregado".
            if (not prev_tenia_firma) and rec.clave_firma_manual and rec.firma_id and rec.estado != 'reparado y entregado':
                rec.estado = 'reparado y entregado'

    @api.onchange('estado')
    def _onchange_estado(self):
        """Si se marca como cancelado, limpiar los montos a 0"""
        if self.estado == 'cancelado':
            self.gramos_utilizado = 0.0
            self.metales_extra = 0.0
            self.cobro_interno = 0.0
            self.hechura = 0.0
            self.cobros_extras = 0.0
            self.hechura2 = 0.0

    
    #@api.model
    #def create(self, vals):
     #   if not vals.get('vendedora_id'):
      #      raise ValidationError("Debe escanear una vendedora válida antes de crear la orden.")
       # return super(Reparacion, self).create(vals)



    @api.constrains('servicio', 'n_cm_fabricacion', 'n_cm_reparacion')
    def _check_campos_cm_por_servicio(self):
        for record in self:
            if record.servicio == 'fabricacion':
                if record.n_cm_reparacion and record.n_cm_fabricacion:
                    raise ValidationError("Solo se debe completar el campo N° CM Fabricación cuando el servicio es Fabricación.")
                if not record.n_cm_fabricacion:
                    raise ValidationError("Debes completar el campo N° CM Fabricación si el servicio es Fabricación.")
        
            elif record.servicio == 'reparacion':
                if record.n_cm_fabricacion and record.n_cm_reparacion:
                    raise ValidationError("Solo se debe completar el campo N° CM Reparación cuando el servicio es Reparación.")
                if not record.n_cm_reparacion:
                    raise ValidationError("Debes completar el campo N° CM Reparación si el servicio es Reparación.")




    ###Validacion correo
    @api.constrains('correo_cliente')
    def _check_email_format(self):
        for record in self:
            if record.correo_cliente:
                email_regex = r"[^@]+@[^@]+\.[^@]+"
                if not re.match(email_regex, record.correo_cliente):
                    raise ValidationError("El correo electrónico ingresado no es válido.")
                
    ###Validacion teléfono
    @api.constrains('telefono')
    def _check_telefono_format(self):
        pattern = r'^\+56\s9\s\d{4}\s\d{4}$'
        for record in self:
            if record.telefono and not re.match(pattern, record.telefono):
                raise ValidationError(
                    "El teléfono debe tener el formato “+56 9 XXXX XXXX”, "
                    "por ejemplo: +56 9 XXXX XXXX"
                )

    @api.depends()
    def _compute_estado(self):
        for rec in self:
            if not self.env.user.has_group('joyeria_reparaciones.grupo_gestion_estado_reparacion'):
                rec.estado = rec.estado  # No cambia el valor, pero evita la edición

    @api.depends('cantidad', 'precio_unitario', 'extra', 'extra2', 'extra3', 'hechura2', 'tipo_cliente')
    def _compute_subtotal(self):
        for rec in self:

            # Determinar precio base según tipo de cliente
            if rec.tipo_cliente in ['cliente mayorista', 'cliente preferente']:
                precio_base = rec.hechura2 or 0.0
            else:
                precio_base = rec.precio_unitario or 0.0

            # Calcular subtotal correctamente
            rec.subtotal = (
                (rec.cantidad or 0.0) * precio_base
                + (rec.extra or 0.0)
                + (rec.extra2 or 0.0)
                + (rec.extra3 or 0.0)
            )

    @api.depends('subtotal', 'abono')
    def _compute_saldo(self):
        for rec in self:
            rec.saldo = rec.subtotal - rec.abono


    @api.depends('gramos_utilizado', 'metales_extra')
    def _compute_peso_total(self):
        for rec in self:
            rec.peso_total = rec.gramos_utilizado + rec.metales_extra

    #def write(self, vals):
     #   for rec in self:
      #      peso = vals.get('peso', rec.peso)
       #     peso_valor = vals.get('peso_valor', rec.peso_valor)
        #    if peso == 'especial' and not peso_valor:
         #       raise ValidationError("Debe ingresar un valor para el peso si selecciona tipo 'Especial'.")
        #return super().write(vals)

    @api.depends('cobro_interno', 'hechura', 'cobros_extras', 'otros_total', 'oro_rosado_total', 'oro_amarillo_total', 'plata_total')
    def _compute_total_salida(self):
        for rec in self:
            rec.total_salida_taller = (rec.cobro_interno or 0) + (rec.hechura or 0) + (rec.cobros_extras or 0) + (rec.otros_total or 0) + (rec.oro_rosado_total or 0) + (rec.oro_amarillo_total or 0) + (rec.plata_total or 0)

    @api.onchange('clave_firma_manual')
    def _onchange_clave_firma_manual(self):
        self._procesar_firma()


    from datetime import datetime
    import pytz

    CHILE_TZ = pytz.timezone('America/Santiago')

    def _procesar_firma(self):
        if self.clave_firma_manual:
            clave = self.clave_firma_manual.strip().upper()
            vendedora = self.env['joyeria.vendedora'].search([
                '|', '|',
                ('clave_autenticacion', '=', clave),
                ('clave_qr', '=', clave),
                ('codigo_qr', '=', clave),
            ], limit=1)
            if vendedora:
                self.firma_id = vendedora.id

                # ✅ Obtener hora exacta de Chile, convertir a UTC y eliminar tzinfo (Odoo requiere naive)
                ahora_chile = datetime.now(pytz.timezone('America/Santiago'))
                ahora_utc_naive = ahora_chile.astimezone(pytz.UTC).replace(tzinfo=None)

                self.fecha_firma = ahora_utc_naive


    @api.onchange('clave_autenticacion_manual')
    def _onchange_clave_autenticacion_manual(self):
        self._procesar_vendedora()


    def _procesar_vendedora(self):
        """Asigna la vendedora desde la clave de autenticación manual"""
        if self.clave_autenticacion_manual:
            clave = self.clave_autenticacion_manual.strip().upper()
            vendedora = self.env['joyeria.vendedora'].search([
                '|', '|',
                ('clave_autenticacion', '=', clave),
                ('clave_qr', '=', clave),
                ('codigo_qr', '=', clave),
            ], limit=1)
            if vendedora:
                self.vendedora_id = vendedora.id

# ###create funcional(se modifica)######
    @api.model
    def create(self, vals):
        ahora = datetime.now(CHILE_TZ).strftime('%d/%m/%Y %H:%M:%S')
        mensajes = []

        is_admin = self.env.uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')
        is_import = bool(self.env.context.get('import_file') or self.env.context.get('from_import'))

        # ============================================================
        # 🆕 CLIENTE ESPECIAL → USAR HECHURA
        # ============================================================
        tipo_cliente = vals.get("tipo_cliente")

        if tipo_cliente in ["cliente mayorista", "cliente preferente"]:
            precio = vals.get("precio_unitario", 0) or 0

            if precio > 0:
                vals["hechura2"] = precio
                vals["precio_unitario"] = 0

        # ============================================================
        # 🔐 VALIDACIÓN DE AUTORIZACIÓN PARA RMA SIN COSTO
        # ============================================================

        precio_unitario = vals.get("precio_unitario", 0) or 0
        extra = vals.get("extra", 0) or 0
        extra2 = vals.get("extra2", 0) or 0
        extra3 = vals.get("extra3", 0) or 0
        abono = vals.get("abono", 0) or 0
        saldo = vals.get("saldo", 0) or 0

        precio0 = (
            precio_unitario == 0 and
            extra == 0 and
            extra2 == 0 and
            extra3 == 0 and
            abono == 0 and
            saldo == 0
        )

        if precio0 and not is_admin:

            vals["costo_cero_definitivo"] = True

            self.env["joyeria.reparacion.authcode"].search([]).check_expired()

            _logger = logging.getLogger(__name__)
            _logger.warning("===== DEBUG AUTORIZACIÓN CREA =====")
            _logger.warning("VALS codigo_ingresado = %s", vals.get("codigo_ingresado"))
            _logger.warning("====================================")

            codigo_ing = vals.get("codigo_ingresado") or self._context.get("codigo_ingresado") or ""
            codigo_ing = str(codigo_ing).strip().upper()

            if not codigo_ing:
                raise ValidationError("❌ Debes ingresar un código de autorización para reparaciones sin costo.")

            codes = self.env["joyeria.reparacion.authcode"].search([
                ('used', '=', False),
                ('expired', '=', False),
            ])

            code = next(
                (c for c in codes if (c.codigo or "").strip().upper() == codigo_ing),
                False
            )

            if not code:
                raise ValidationError("❌ El código ingresado no existe o ya fue utilizado.")

            code.write({
                'used': True,
                'usado_por_id': self.env.uid,
                'fecha_uso': datetime.now()
            })

            vals["codigo_autorizacion_id"] = code.id

        # ============================================================
        # ⚙️ RESTO DE TU LÓGICA (NO TOCADA)
        # ============================================================

        if (not is_admin) and (not is_import) and vals.get('peso') == 'especial' and not vals.get('peso_valor'):
            raise ValidationError("Debe ingresar un valor para el campo 'Peso' si selecciona tipo de peso 'Especial'.")

        if not is_import and not is_admin:

            peso_tipo = vals.get('peso')
            peso_valor = vals.get('peso_valor')

            if peso_tipo == 'estandar':
                if peso_valor not in (0, False, None):
                    raise ValidationError(
                        "❌ Para tipo de peso 'Estándar', el campo 'Peso' debe ser 0.\n"
                        "Ingrese 0 o deje el campo vacío."
                    )

        if vals.get('name', 'Nuevo') == 'Nuevo':
            secuencia = self.env['ir.sequence'].next_by_code('joyeria.reparacion')
            if not secuencia:
                raise ValidationError("No se pudo generar la secuencia.")
            vals['name'] = secuencia.replace("'", "-")

        if not vals.get('vendedora_id') and vals.get('clave_autenticacion_manual'):
            clave = str(vals['clave_autenticacion_manual']).strip().upper()
            vendedora = self.env['joyeria.vendedora'].search([
                '|', '|',
                ('clave_autenticacion', '=', clave),
                ('clave_qr', '=', clave),
                ('codigo_qr', '=', clave),
            ], limit=1)
            if vendedora:
                vals['vendedora_id'] = vendedora.id
                mensajes.append(f"📦 Recibido por: <b>{vendedora.name}</b> el <b>{ahora}</b>")

        if not vals.get('firma_id') and vals.get('clave_firma_manual'):
            clave = str(vals['clave_firma_manual']).strip().upper()
            vendedora_firma = self.env['joyeria.vendedora'].search([
                '|', '|',
                ('clave_autenticacion', '=', clave),
                ('clave_qr', '=', clave),
                ('codigo_qr', '=', clave),
            ], limit=1)
            if vendedora_firma:
                vals['firma_id'] = vendedora_firma.id
                ahora_chile = datetime.now(pytz.timezone('America/Santiago'))
                ahora_utc_naive = ahora_chile.astimezone(pytz.UTC).replace(tzinfo=None)
                vals['fecha_firma'] = ahora_utc_naive
                mensajes.append(f"✍️ Retirado por: <b>{vendedora_firma.name}</b> el <b>{ahora}</b>")

        if vals.get('clave_autenticacion_manual') and not vals.get('vendedora_id'):
            raise ValidationError("❌ Clave inválida: No se encontró ninguna vendedora con esa clave (quien recibe).")

        if vals.get('clave_firma_manual') and not vals.get('firma_id'):
            raise ValidationError("❌ Clave inválida: No se encontró ninguna vendedora con esa clave (quien retira).")

        record = super().create(vals)

        if hasattr(record, '_generar_codigo_qr'):
            record._generar_codigo_qr()

        for msg in mensajes:
            record.message_post(body=msg)

        return record






    class ResPartnerRestrictWriteForRMAClients(models.Model):
        _inherit = 'res.partner'

        def _is_admin(self):
            return self.env.uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')

        def write(self, vals):
            # Admin siempre puede editar
            if self._is_admin():
                return super().write(vals)

            # ¿Alguno de estos partners es/ha sido usado como cliente en una reparación?
            # (Si sí, solo admin puede editar su información)
            Reparacion = self.env['joyeria.reparacion'].sudo()
            if Reparacion.search_count([('cliente_id', 'in', self.ids)]) > 0:
                raise ValidationError(
                    "Solo los administradores pueden editar la información de clientes asociados a reparaciones."
                )

            # Si no están vinculados a reparaciones, permitir edición normal
            return super().write(vals)

    




    #ef write(self, vals):
     #
    #  for record in self:
     #      ya_tiene_vendedora = bool(record.vendedora_id)

      #      # Si ya hay vendedora asignada, no permitir modificarla ni borrar claves
       #     if ya_tiene_vendedora:
        #        if 'vendedora_id' in vals and not vals['vendedora_id']:
         #           raise ValidationError("No puede eliminar la vendedora una vez asignada.")
#
 #               for campo in ['clave_autenticacion', 'codigo_qr', 'clave_autenticacion_manual']:
  #                  if campo in vals and not vals[campo]:
   #                     raise ValidationError(f"No puede eliminar el valor de {campo} una vez asignada la vendedora.")
#
 #               claves_cambiadas = any(campo in vals for campo in ['clave_autenticacion', 'codigo_qr', 'clave_autenticacion_manual'])
  #              if 'vendedora_id' in vals or claves_cambiadas:
   #                 raise ValidationError("No se puede modificar la clave o la vendedora una vez asignada.")
#
 #           # Procesar firma si se ingresa por primera vez
  #          if vals.get('clave_firma_manual'):
   #             record._procesar_firma()
#
 #       return super(Reparacion, self).write(vals)
    
    def _normalizar_clave(self, clave):
        """
        Limpia la clave escaneada por el lector QR, eliminando caracteres extraños
        como 'QR' o comillas, dejando solo lo esencial.
        """
        clave = clave.strip().upper()
        clave = clave.replace("QR'", "").replace("QR", "").replace("'", "").strip()
        return clave


###write funcional"""""""""
    def write(self, vals):
        is_admin = self.env.uid == SUPERUSER_ID or self.env.user.has_group('base.group_system')

        # ============================================================
        # 🆕 CLIENTE ESPECIAL → HECHURA + BLOQUEO PRECIO
        # ============================================================
        for rec in self:
            tipo = vals.get("tipo_cliente", rec.tipo_cliente)

            if tipo in ["cliente mayorista", "cliente preferente"]:

                precio = vals.get("precio_unitario", rec.precio_unitario) or 0

                if precio > 0:
                    vals["hechura2"] = precio
                    vals["precio_unitario"] = 0

        # ============================================================
        # 🔧 VALIDACIONES EXISTENTES (NO TOCAR)
        # ============================================================
        if not is_admin:
            for rec in self:
                if 'peso' in vals and vals['peso'] != rec.peso:
                    raise ValidationError("No se permite cambiar el tipo de peso una vez creado el registro.")

        # ============================================================
        # 📲 QR (NO TOCADO)
        # ============================================================
        for rec in self:

            if vals.get('clave_autenticacion_manual'):
                clave = vals['clave_autenticacion_manual'].strip().upper()
                vendedora = rec.env['joyeria.vendedora'].search([
                    '|', '|',
                    ('clave_autenticacion', '=', clave),
                    ('clave_qr', '=', clave),
                    ('codigo_qr', '=', clave),
                ], limit=1)
                if vendedora:
                    vals['vendedora_id'] = vendedora.id

            if vals.get('clave_firma_manual'):
                clave = vals['clave_firma_manual'].strip().upper()
                vendedora_firma = rec.env['joyeria.vendedora'].search([
                    '|', '|',
                    ('clave_autenticacion', '=', clave),
                    ('clave_qr', '=', clave),
                    ('codigo_qr', '=', clave),
                ], limit=1)
                if vendedora_firma:
                    vals['firma_id'] = vendedora_firma.id
                    ahora_chile = datetime.now(pytz.timezone('America/Santiago'))
                    ahora_utc_naive = ahora_chile.astimezone(pytz.UTC).replace(tzinfo=None)
                    vals['fecha_firma'] = ahora_utc_naive

        return super().write(vals)




        

    def imprimir_reporte_responsables(self):
        # Rango de fechas fijo, puedes cambiarlo más adelante a dinámico
        fecha_inicio = datetime.strptime('2024-01-01', '%Y-%m-%d')
        fecha_fin = datetime.strptime('2025-12-31', '%Y-%m-%d')

        reparaciones = self.search([
            ('fecha_entrega', '>=', fecha_inicio),
            ('fecha_entrega', '<=', fecha_fin),
        ], order='fecha_entrega asc')  # Orden ascendente por fecha_entrega

        return self.env.ref('joyeria_reparaciones.reporte_reparaciones_responsable_action').report_action(
            reparaciones,
            data={
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            }
        )
    
    
    def copy(self, default=None):
        if self.env.user.has_group('joyeria_reparaciones.grupo_gestion_estado_reparacion'):
            raise UserError("No tienes permiso para duplicar órdenes de reparación.")
        return super(Reparacion, self).copy(default)


    def _generar_codigo_qr(self):
        for record in self:
            if record.name:
                texto_qr = str(record.name).replace("'", "-").strip()
                qr_img = qrcode.make(texto_qr)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                record.qr = base64.b64encode(buffer.getvalue())
    

    def unlink(self):
        if self.env.user.has_group('joyeria_reparaciones.grupo_gestion_estado_reparacion'):
            raise UserError("No tienes permiso para eliminar órdenes de reparación.")
        return super(Reparacion, self).unlink()
    
    


    @api.onchange('cliente_id')
    def _onchange_cliente_id(self):
        if self.cliente_id:
            nombre_completo = self.cliente_id.name or ''
            partes = nombre_completo.split(' ', 1)
            self.nombre_cliente = partes[0] if partes else ''
            self.apellido_cliente = partes[1] if len(partes) > 1 else ''
            self.correo_cliente = self.cliente_id.email or ''
            self.telefono = self.cliente_id.phone or ''
            #self.direccion_entrega = self.cliente_id.street or ''


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            # Reemplaza comillas mal leídas por guiones para búsquedas correctas
            name = name.replace("'", "-")
            args += [('name', operator, name)]
        return self.search(args, limit=limit).name_get()


class ResPartnerRequirePhoneAlways(models.Model):
    _inherit = 'res.partner'

    @api.constrains('phone', 'mobile', 'is_company', 'active')
    def _check_phone_required_for_person(self):
        """
        Obliga a ingresar teléfono (phone o mobile) para PERSONAS activas.
        Se ejecuta en create/write y es independiente del contexto del popup.
        """
        for rec in self:
            # Sólo aplica a clientes/personas (no empresas) y activos
            if rec.active and not rec.is_company:
                if not (rec.phone and rec.phone.strip()) and not (rec.mobile and rec.mobile.strip()):
                    raise ValidationError(
                        "Debe ingresar un número de teléfono (Teléfono o Móvil) para crear/guardar el cliente."
                    )


class Operacion(models.Model):
    _name = 'joyeria.operacion'
    _description = 'Línea de operación de reparación'

    reparacion_id = fields.Many2one('joyeria.reparacion', string='Reparación')
    producto_id = fields.Many2one('product.product', string='Producto')
    descripcion = fields.Char(string='Descripción')
    cantidad = fields.Float(string='Cantidad')
    unidad_medida = fields.Char(string='Unidad de medida')
    precio_unitario = fields.Float(string='Precio unitario')


class Vendedora(models.Model):
    
    
    _name = 'joyeria.vendedora'
    _description = 'Vendedora'

    name = fields.Char("Nombre completo", required=True)
    codigo_qr = fields.Char("Código QR", readonly=True, copy=False)
    qr_image = fields.Binary("QR", readonly=True)
    es_vendedora_qr = fields.Boolean(string="Generado por QR", default=True)
    clave_autenticacion = fields.Char("Clave de Autenticación", readonly=True, copy=False)
    clave_input = fields.Char(string="Clave Vendedora (Escaneo/Manual)")
    clave_qr = fields.Char(string='Clave QR / Clave de Autenticación', required=True, default=lambda self: str(uuid.uuid4()))
    cargo = fields.Char(string="Cargo")
    empresa = fields.Char(string="Empresa")



    @api.onchange('clave_autenticacion')
    def _onchange_clave_autenticacion(self):
        if self.clave_autenticacion:
            vendedora = self.env['joyeria.vendedora'].search([('clave_autenticacion', '=', self.clave_autenticacion.strip())], limit=1)
            if vendedora:
                self.vendedora_id = vendedora
            else:
                self.vendedora_id = False
                return {
                    'warning': {
                        'title': "Clave inválida",
                        'message': "No se encontró ninguna vendedora con esa clave.",
                    }
                }

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # 👉 Esto hace que no se devuelvan resultados en el autocomplete del campo vendedora_id
        return []


    @api.model
    def create(self, vals):
        generar_qr = vals.pop('generar_qr', True)
        if generar_qr and not vals.get('codigo_qr'):
            vals['codigo_qr'] = self.env['ir.sequence'].next_by_code('joyeria.vendedora.qr')

        # Generar clave automáticamente
        if not vals.get('clave_autenticacion'):
            vals['clave_autenticacion'] = str(uuid.uuid4()).split('-')[0].upper()  # algo como 'A1B2C3D4'

        rec = super().create(vals)
        if generar_qr:
            rec._generar_qr()
        return rec

    def _generar_qr(self):
        import qrcode
        import base64
        from io import BytesIO

        for rec in self:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(rec.codigo_qr)  # ✅ Aquí usamos la clave QR única y segura
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            rec.qr_image = base64.b64encode(buffer.getvalue())


    def imprimir_etiqueta_vendedora(self):
        return self.env.ref('joyeria_reparaciones.action_report_etiqueta_vendedora').report_action(self)

    @api.model
    def validar_vendedora_pos(self, codigo):
        codigo = (codigo or "").strip()

        vendedora = self.search([
            '|', '|',
            ('codigo_qr', '=', codigo),
            ('clave_qr', '=', codigo),
            ('clave_autenticacion', '=', codigo),
        ], limit=1)

        if not vendedora:
            return False

        return {
            'id': vendedora.id,
            'name': vendedora.name,
        }