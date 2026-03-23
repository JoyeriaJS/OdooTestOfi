/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useService } from "@web/core/utils/hooks";

patch(PaymentScreen.prototype, {

    setup() {
        super.setup();
        this.rpc = useService("rpc");
    },

    async validateOrder(isForceValidate) {

        const order = this.currentOrder;

        // ==============================
        // VALIDACIÓN 50% PRECIO MÍNIMO
        // ==============================

        const lines = order.get_orderlines();

        for (let line of lines) {

            const esProductoRMA =
                line.product &&
                line.product.display_name &&
                line.product.display_name.trim() === "Producto RMA";

            const esLineaAuxiliarRMA =
                line.es_linea_rma_aux === true &&
                (
                    line.tipo_linea_rma === "abono" ||
                    line.tipo_linea_rma === "subtotal"
                );

            if (esProductoRMA || esLineaAuxiliarRMA) {
                continue;
            }

            const precioOriginal = line.product.lst_price || 0;
            const precioVenta = line.get_unit_price();

            if (precioVenta < (precioOriginal * 0.5)) {

                alert(
                    "No se puede vender el producto '" +
                    line.product.display_name +
                    "' PRECIO ERRONEO."
                );

                return;
            }
        }


        // ==============================
        // DESCUENTO AUTORIZADO
        // ==============================

        const paymentlines = order.paymentlines;
        let metodoPermitido = false;

        paymentlines.forEach(line => {
            const name = line.payment_method.name.toLowerCase();

            if (name.includes("efectivo") || name.includes("transferencia")) {
                metodoPermitido = true;
            }
        });

        if (metodoPermitido) {

            const codigo = prompt("Ingrese código de autorización de descuento");

            if (codigo) {

                const descuento = await this.rpc("/pos/validar_descuento", {
                    codigo: codigo
                });

                if (descuento) {

                    const lines = order.get_orderlines();

                    if (descuento.tipo_descuento === "porcentaje") {

                        const porcentaje = parseFloat(descuento.porcentaje);

                        lines.forEach(line => {
                            line.set_discount(porcentaje);
                        });

                    }

                    if (descuento.tipo_descuento === "monto") {

                        const total = order.get_total_with_tax();
                        const porcentaje = (descuento.monto / total) * 100;

                        lines.forEach(line => {
                            line.set_discount(porcentaje);
                        });

                    }

                    alert("Descuento aplicado correctamente");

                } else {

                    alert("Código inválido o ya utilizado");
                    return;

                }

            }

        }

        await super.validateOrder(isForceValidate);
    }

});