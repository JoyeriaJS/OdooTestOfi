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
        const pos = this.pos || this.env.pos;

         // ===================================
        // BLOQUEAR VENTA DIRECTA DE PRODUCTOS AUXILIARES RMA
        // ===================================
        //if (
        //    (product.name === "Producto SUBTOTAL" || product.name === "Producto ABONO") &&
         //   !options.permitir_linea_rma_aux
        //) {
          //  await popup.add(ErrorPopup, {
            //    title: "Acción no permitida",
              //  body: `No se puede vender "${product.name}" por separado. Este producto solo puede agregarse desde un Producto RMA.`,
            //});
            //return;
        //}

        // ===================================
        // PRODUCTO NO INVENTARIADO
        // ===================================
        if (product.name === "Producto No Inventariado") {
            const gramos = await popup.add(NumberPopup, {
                title: "Ingrese gramos",
            });

            if (!gramos.confirmed || !gramos.payload) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar los gramos.",
                });
                return;
            }

            const precio = await popup.add(NumberPopup, {
                title: "Ingrese precio",
            });

            if (!precio.confirmed || !precio.payload) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar el precio.",
                });
                return;
            }

            const descripcion = await popup.add(TextInputPopup, {
                title: "Ingrese descripción",
            });

            if (!descripcion.confirmed || !descripcion.payload) {
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
                line.descripcion_personalizada = descripcion.payload;
            }

            return;
        }

        // ===================================
        // PRODUCTO GASTO
        // ===================================
        if (product.name === "Producto GASTO") {
            const nombre = await popup.add(TextInputPopup, {
                title: "Ingrese nombre",
                placeholder: "Ej: Lápiz, Bolsa, Taxi",
            });

            if (!nombre.confirmed || !nombre.payload || !nombre.payload.trim()) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar el nombre.",
                });
                return;
            }

            const descripcion = await popup.add(TextInputPopup, {
                title: "Ingrese descripción",
                placeholder: "Detalle del gasto",
            });

            if (!descripcion.confirmed || !descripcion.payload || !descripcion.payload.trim()) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar la descripción.",
                });
                return;
            }

            const precio = await popup.add(NumberPopup, {
                title: "Ingrese precio",
            });

            if (!precio.confirmed || !precio.payload) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar el precio.",
                });
                return;
            }

            const precioNumerico = Math.abs(parseFloat(precio.payload || 0));

            if (!precioNumerico || precioNumerico <= 0) {
                await popup.add(ErrorPopup, {
                    title: "Dato obligatorio",
                    body: "Debe ingresar un precio válido.",
                });
                return;
            }

            options.price = -precioNumerico;
            options.quantity = 1;
            options.merge = false;

            await super.add_product(product, options);

            const line = this.get_selected_orderline();
            if (line) {
                line.es_producto_gasto = true;
                line.precio_bloqueado = -precioNumerico;
                line.gasto_nombre = nombre.payload.trim();
                line.gasto_descripcion = descripcion.payload.trim();
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

            if (!rmaInput.confirmed || !rmaInput.payload) {
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
                    console.warn("QR no válido");
                }
            }

            // ===================================
            // NORMALIZAR
            // ===================================
            numeroRMA = numeroRMA
                .replace("RMA/", "")
                .replace("RMA-", "")
                .replace("rma/", "")
                .replace("rma-", "")
                .trim();

            // ===================================
            // CONSULTAR BACKEND
            // ===================================
            const resultado = await rpc("/pos/buscar_rma", {
                numero_rma: numeroRMA,
            });

            if (resultado.error) {
                await popup.add(ErrorPopup, {
                    title: "Error",
                    body: resultado.error,
                });
                return;
            }

            const subtotal = parseFloat(resultado.subtotal || 0);
            const abono = parseFloat(resultado.abono || 0);
            const saldo = parseFloat(resultado.saldo || 0);

            if (saldo <= 0) {
                await popup.add(ErrorPopup, {
                    title: "Error",
                    body: "El RMA no tiene saldo pendiente.",
                });
                return;
            }

            // ===================================
            // BUSCAR PRODUCTOS AUXILIARES
            // ===================================
            let productoSubtotal = null;
            let productoAbono = null;

            const allProducts = Object.values(pos.db.product_by_id || {});
            productoSubtotal = allProducts.find((p) => p.name === "Producto SUBTOTAL");
            productoAbono = allProducts.find((p) => p.name === "Producto ABONO");

            if (!productoSubtotal || !productoAbono) {
                await popup.add(ErrorPopup, {
                    title: "Error de configuración",
                    body: 'Debes tener creados y cargados en POS los productos "Producto SUBTOTAL" y "Producto ABONO".',
                });
                return;
            }

            // ===================================
            // AGREGAR LÍNEAS DEL RMA
            // ===================================

            // Línea subtotal
            await super.add_product(productoSubtotal, {
                price: subtotal,
                quantity: 1,
                merge: false,
            });

            const lineSubtotal = this.get_selected_orderline();
            if (lineSubtotal) {
                lineSubtotal.numero_rma = resultado.rma;
                lineSubtotal.es_linea_rma_aux = true;
                lineSubtotal.tipo_linea_rma = "subtotal";
                lineSubtotal.precio_bloqueado = subtotal;
            }

            // Línea abono (negativa para que el total final sea el saldo)
            await super.add_product(productoAbono, {
                price: -abono,
                quantity: 1,
                merge: false,
            });

            const lineAbono = this.get_selected_orderline();
            if (lineAbono) {
                lineAbono.numero_rma = resultado.rma;
                lineAbono.es_linea_rma_aux = true;
                lineAbono.tipo_linea_rma = "abono";
                lineAbono.precio_bloqueado = -abono;
            }

            // Línea principal RMA en 0 para identificar la operación
            await super.add_product(product, {
                price: 0,
                quantity: 1,
                merge: false,
            });

            const lineRMA = this.get_selected_orderline();
            if (lineRMA) {
                lineRMA.numero_rma = resultado.rma;
                lineRMA.precio_original_rma = saldo;
                lineRMA.subtotal_rma = subtotal;
                lineRMA.abono_rma = abono;
                lineRMA.saldo_rma = saldo;
                lineRMA.es_linea_rma_principal = true;
                lineRMA.precio_bloqueado = 0;
                lineRMA.set_unit_price(0);
            }

            return;
        }

        return await super.add_product(product, options);
    },
});

patch(Orderline.prototype, {
    set_unit_price(price) {
        if (this.es_linea_rma_principal) {
            if (price !== 0) {
                const popup = this.env.services.popup;
                popup.add(ErrorPopup, {
                    title: "Acción no permitida",
                    body: "No se puede modificar manualmente la línea principal del RMA.",
                });
                return super.set_unit_price(0);
            }
            return super.set_unit_price(0);
        }

        if (this.tipo_linea_rma === "subtotal") {
            const precioBloqueado = this.precio_bloqueado ?? this.get_unit_price();
            if (price !== precioBloqueado) {
                const popup = this.env.services.popup;
                popup.add(ErrorPopup, {
                    title: "Acción no permitida",
                    body: "No se puede modificar el precio de Producto SUBTOTAL.",
                });
                return super.set_unit_price(precioBloqueado);
            }
            return super.set_unit_price(precioBloqueado);
        }

        if (this.tipo_linea_rma === "abono") {
            const precioBloqueado = this.precio_bloqueado ?? this.get_unit_price();
            if (price !== precioBloqueado) {
                const popup = this.env.services.popup;
                popup.add(ErrorPopup, {
                    title: "Acción no permitida",
                    body: "No se puede modificar el precio de Producto ABONO.",
                });
                return super.set_unit_price(precioBloqueado);
            }
            return super.set_unit_price(precioBloqueado);
        }

        if (this.es_producto_gasto) {
            const precioBloqueado = this.precio_bloqueado ?? this.get_unit_price();
            if (price !== precioBloqueado) {
                const popup = this.env.services.popup;
                popup.add(ErrorPopup, {
                    title: "Acción no permitida",
                    body: "No se puede modificar el precio de Producto GASTO.",
                });
                return super.set_unit_price(precioBloqueado);
            }
            return super.set_unit_price(precioBloqueado);
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

        json.es_linea_rma_principal = this.es_linea_rma_principal || false;
        json.es_linea_rma_aux = this.es_linea_rma_aux || false;
        json.tipo_linea_rma = this.tipo_linea_rma || "";
        json.precio_bloqueado = this.precio_bloqueado || 0;

        json.es_producto_gasto = this.es_producto_gasto || false;
        json.gasto_nombre = this.gasto_nombre || "";
        json.gasto_descripcion = this.gasto_descripcion || "";

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

        this.es_linea_rma_principal = json.es_linea_rma_principal || false;
        this.es_linea_rma_aux = json.es_linea_rma_aux || false;
        this.tipo_linea_rma = json.tipo_linea_rma || "";
        this.precio_bloqueado = json.precio_bloqueado || 0;

        this.es_producto_gasto = json.es_producto_gasto || false;
        this.gasto_nombre = json.gasto_nombre || "";
        this.gasto_descripcion = json.gasto_descripcion || "";
    },

    export_for_printing() {
        const line = super.export_for_printing(...arguments);

        line.gramos = this.gramos || "";
        line.descripcion_personalizada = this.descripcion_personalizada || "";
        line.numero_rma = this.numero_rma || "";

        line.subtotal_rma = this.subtotal_rma || 0;
        line.abono_rma = this.abono_rma || 0;
        line.saldo_rma = this.saldo_rma || 0;

        line.es_linea_rma_principal = this.es_linea_rma_principal || false;
        line.es_linea_rma_aux = this.es_linea_rma_aux || false;
        line.tipo_linea_rma = this.tipo_linea_rma || "";
        line.precio_bloqueado = this.precio_bloqueado || 0;

        line.es_producto_gasto = this.es_producto_gasto || false;
        line.gasto_nombre = this.gasto_nombre || "";
        line.gasto_descripcion = this.gasto_descripcion || "";

        return line;
    },
});