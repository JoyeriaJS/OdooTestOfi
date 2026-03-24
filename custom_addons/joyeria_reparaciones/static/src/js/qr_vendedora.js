/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Order } from "@point_of_sale/app/store/models";

patch(PaymentScreen.prototype, {

    async validateOrder(isForceValidate) {

        const { confirmed, payload } = await this.popup.add(TextInputPopup, {
            title: "Clave de Vendedora",
            body: "Ingrese o escanee la clave para validar la venta",
            isPassword: "true",
        });

        if (!confirmed || !payload) {
            return;
        }

        const codigo = payload.trim();

        // 🔥 Validación directa en backend
        const result = await this.orm.call(
            'joyeria.vendedora',
            'validar_vendedora_pos',
            [codigo]
        );

        if (!result) {
            await this.popup.add(ErrorPopup, {
                title: "Clave inválida",
                body: "No se encontró una vendedora con esa clave.",
            });
            return;
        }

        // 🔹 Asignamos a la orden
        this.currentOrder.vendedora_id = result.id;
        this.currentOrder.vendedora_name = result.name;

        return super.validateOrder(isForceValidate);
    },
});


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