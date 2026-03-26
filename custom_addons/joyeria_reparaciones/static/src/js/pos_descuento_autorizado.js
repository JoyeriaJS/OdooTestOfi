/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useService } from "@web/core/utils/hooks";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(PaymentScreen.prototype, {

    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.popup = useService("popup");
    },

    async validateOrder(isForceValidate) {

        const order = this.currentOrder;

        // ==============================
        // 1️⃣ DESCUENTO (PRIMERO)
        // ==============================

        if (!order.descuento_aplicado) {

            const paymentlines = order.paymentlines || [];

            let metodoPermitido = false;

            paymentlines.forEach(line => {
                const name = (line.payment_method?.name || "").toLowerCase();

                if (
                    name.includes("efectivo") ||
                    name.includes("transferencia") ||
                    name.includes("credito") ||
                    name.includes("crédito")
                ) {
                    metodoPermitido = true;
                }
            });

            if (metodoPermitido) {

                const codigo = prompt("Ingrese código de autorización de descuento");

                if (!codigo) {
                    return;
                }

                const descuento = await this.rpc("/pos/validar_descuento", {
                    codigo: codigo
                });

                if (!descuento) {
                    alert("Código inválido o ya utilizado");
                    return;
                }

                // VALIDAR MÉTODO DE PAGO
                const metodosOrden = paymentlines.map(
                    l => (l.payment_method?.name || "").toLowerCase().trim()
                );

                const metodosPermitidos = (descuento.metodos_pago_nombres || []).map(
                    m => (m || "").toLowerCase().trim()
                );

                const metodoValido = metodosOrden.some(m =>
                    metodosPermitidos.includes(m)
                );

                if (!metodoValido) {
                    alert("Este descuento no es válido para el método de pago seleccionado.");
                    return;
                }

                // APLICAR DESCUENTO
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

                // MARCAR COMO USADO
                await this.rpc("/pos/usar_descuento", {
                    descuento_id: descuento.id
                });

                order.descuento_aplicado = true;

                alert("Descuento aplicado correctamente");
            }
        }

        // ==============================
        // 2️⃣ VENDEDORA (SEGUNDO)
        // ==============================

        if (!order.vendedora_id) {

            const { confirmed, payload } = await this.popup.add(TextInputPopup, {
                title: "Clave de Vendedora",
                body: "Ingrese o escanee la clave para validar la venta",
                isPassword: true,
            });

            if (!confirmed || !payload) {
                return;
            }

            const codigo = payload.trim();

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

            order.vendedora_id = result.id;
            order.vendedora_name = result.name;
        }

        // ==============================
        // 3️⃣ VALIDAR ORDEN (FINAL)
        // ==============================

        return super.validateOrder(isForceValidate);
        
    },
    });