/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Order } from "@point_of_sale/app/store/models";




patch(Order.prototype, {

    setup() {
        super.setup(...arguments);
        this.vendedora_id = this.vendedora_id || null;
        this.vendedora_name = this.vendedora_name || null;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.vendedora_id = this.vendedora_id || null;
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.vendedora_id = json.vendedora_id || null;
    },

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.vendedora_name = this.vendedora_name || "";
        return result;
    },

});