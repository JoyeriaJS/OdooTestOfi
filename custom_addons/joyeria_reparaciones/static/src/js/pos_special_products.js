/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(Order.prototype, {
    async add_product(product, options = {}) {
        const popup = this.env.services.popup;
        const rpc = this.env.services.rpc;

        // ===================================
        // PRODUCTO NO INVENTARIADO
        // ===================================
        if (product.name === "Producto No Inventariado") {
            const gramos = await popup.add(NumberPopup, {
                title: "Ingrese gramos",
            });

            if (!gramos.confirmed || gramos.payload === null || gramos.payload === "") {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar los gramos.",
                });
                return;
            }

            const precio = await popup.add(NumberPopup, {
                title: "Ingrese precio",
            });

            if (!precio.confirmed || precio.payload === null || precio.payload === "") {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar el precio.",
                });
                return;
            }

            const descripcion = await popup.add(TextInputPopup, {
                title: "Ingrese descripción",
            });

            if (!descripcion.confirmed || !descripcion.payload?.trim()) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar la descripción.",
                });
                return;
            }

            options.price = parseFloat(precio.payload);

            await super.add_product(product, options);

            const line = this.get_selected_orderline();
            if (line) {
                line.gramos = gramos.payload;
                line.descripcion_personalizada = descripcion.payload.trim();
            }

            return;
        }

        // ===================================
        // PRODUCTO RMA
        // ===================================
        if (product.name === "Producto RMA") {
            const rmaInput = await popup.add(TextInputPopup, {
                title: "Ingrese número de RMA",
                placeholder: "Ej: RMA/01160, RMA-01160, 1160 o escanee QR",
            });

            if (!rmaInput.confirmed || !rmaInput.payload?.trim()) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar el número de RMA.",
                });
                return;
            }

            let numeroRMA = rmaInput.payload.trim();

            // ===================================
            // SOPORTE PARA QR (URL ODOO)
            // ===================================
            if (numeroRMA.includes("http")) {
                try {
                    const url = new URL(numeroRMA);
                    const match = url.hash.match(/id=(\d+)/);
                    if (match) {
                        numeroRMA = match[1];
                    }
                } catch (e) {
                    console.warn("QR no válido", e);
                }
            }

            // ===================================
            // NORMALIZAR
            // ===================================
            numeroRMA = numeroRMA
                .replace(/^RMA\//i, "")
                .replace(/^RMA-/i, "")
                .trim();

            // ===================================
            // CONSULTAR BACKEND
            // ===================================
            let resultado;
            try {
                resultado = await rpc("/pos/buscar_rma", {
                    numero_rma: numeroRMA,
                });
            } catch (error) {
                await popup.add(ErrorPopup, {
                    title: "Error de conexión",
                    body: "No se pudo consultar el RMA en el servidor.",
                });
                console.error("Error RPC /pos/buscar_rma:", error);
                return;
            }

            if (!resultado) {
                await popup.add(ErrorPopup, {
                    title: "Error",
                    body: "No se recibió respuesta del servidor.",
                });
                return;
            }

            if (resultado.error) {
                await popup.add(ErrorPopup, {
                    title: "Error",
                    body: resultado.error,
                });
                return;
            }

            const precio_backend = parseFloat(resultado.saldo || 0);

            if (!precio_backend || precio_backend <= 0) {
                await popup.add(ErrorPopup, {
                    title: "Error",
                    body: "El RMA no tiene saldo pendiente.",
                });
                return;
            }

            options.price = precio_backend;

            await super.add_product(product, options);

            const line = this.get_selected_orderline();
            if (line) {
                line.numero_rma = resultado.rma || numeroRMA;
                line.precio_original_rma = parseFloat(resultado.saldo || 0);
                line.subtotal_rma = parseFloat(resultado.subtotal || 0);
                line.abono_rma = parseFloat(resultado.abono || 0);
                line.saldo_rma = parseFloat(resultado.saldo || 0);
            }

            return;
        }

        return await super.add_product(product, options);
    },
});

patch(Orderline.prototype, {
    set_unit_price(price) {
        if (this.numero_rma) {
            const precio_original = this.precio_original_rma;

            if (precio_original !== undefined && price !== precio_original) {
                const popup = this.env.services.popup;

                popup.add(ErrorPopup, {
                    title: "Acción no permitida",
                    body: "No se puede modificar el precio de un producto RMA.",
                });

                return super.set_unit_price(precio_original);
            }
        }

        return super.set_unit_price(...arguments);
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);

        json.gramos = this.gramos || "";
        json.descripcion_personalizada = this.descripcion_personalizada || "";
        json.numero_rma = this.numero_rma || "";
        json.precio_original_rma = this.precio_original_rma || 0;
        json.subtotal_rma = this.subtotal_rma || 0;
        json.abono_rma = this.abono_rma || 0;
        json.saldo_rma = this.saldo_rma || 0;

        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);

        this.gramos = json.gramos || "";
        this.descripcion_personalizada = json.descripcion_personalizada || "";
        this.numero_rma = json.numero_rma || "";
        this.precio_original_rma = json.precio_original_rma || 0;
        this.subtotal_rma = json.subtotal_rma || 0;
        this.abono_rma = json.abono_rma || 0;
        this.saldo_rma = json.saldo_rma || 0;
    },

    export_for_printing() {
        const line = super.export_for_printing(...arguments);

        line.gramos = this.gramos || "";
        line.descripcion_personalizada = this.descripcion_personalizada || "";
        line.numero_rma = this.numero_rma || "";
        line.subtotal_rma = this.subtotal_rma || 0;
        line.abono_rma = this.abono_rma || 0;
        line.saldo_rma = this.saldo_rma || 0;

        return line;
    },
});