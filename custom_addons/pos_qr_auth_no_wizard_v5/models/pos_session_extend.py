from odoo import models, fields

class PosSession(models.Model):
    _inherit = 'pos.session'

    vendedora_id = fields.Many2one('joyeria.vendedora', string='Vendedora')

    def button_print_report(self):
        today = fields.Date.context_today(self)
        # Call report action on pos.session model
        return self.env.ref('pos_qr_auth_no_wizard.action_report_rma_pos').report_action(
            self, data={'date_start': today, 'date_end': today})
