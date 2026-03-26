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

            const esProductoGasto = line.es_producto_gasto === true;

            if (esProductoRMA || esLineaAuxiliarRMA || esProductoGasto) {
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
// ==============================
// DESCUENTO AUTORIZADO
// ==============================

    const paymentlines = order.paymentlines;

    let metodoPermitido = false;

    paymentlines.forEach(line => {
        const name = line.payment_method.name.toLowerCase();

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

        // ==============================
        // 🔥 DEBUG (NO BORRAR AÚN)
        // ==============================
        console.log("Orden:", paymentlines.map(l => l.payment_method.name));
        console.log("Permitidos:", descuento.metodos_pago_nombres);

        // ==============================
        // VALIDACIÓN MÉTODO DE PAGO REAL
        // ==============================

        const metodosPagoOrden = paymentlines.map(
            line => line.payment_method.name.toLowerCase().trim()
        );

        const metodosPermitidos = (descuento.metodos_pago_nombres || []).map(
            name => name.toLowerCase().trim()
        );

        const metodoValido = metodosPagoOrden.every(metodo =>
            metodosPermitidos.includes(metodo)
        );

        if (!metodoValido) {
            alert("Este descuento no es válido para el método de pago seleccionado.");
            return;
        }

        // ==============================
        // APLICAR DESCUENTO
        // ==============================

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

        // ==============================
        // 🔥 MARCAR COMO USADO (AHORA SÍ)
        // ==============================

        await this.rpc("/pos/usar_descuento", {
            descuento_id: descuento.id
        });

        alert("Descuento aplicado correctamente");
    }
    patch(PaymentScreen.prototype, {

    async validateOrder(isForceValidate) {

        const { confirmed, payload } = await this.popup.add(TextInputPopup, {
            title: "Clave de Vendedora",
            body: "Ingrese o escanee la clave para validar la venta",
            isPassword: true,
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


}

    });
    