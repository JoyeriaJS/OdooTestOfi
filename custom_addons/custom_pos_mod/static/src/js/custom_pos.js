odoo.define('custom_pos_mod.custom_script', function (require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');

    const CustomProductScreen = ProductScreen => class extends ProductScreen {
        // Ejemplo: mostrar un mensaje al abrir la pantalla
        mounted() {
            super.mounted();
            console.log('¡Pantalla del POS cargada con éxito!');
        }
    };

    require('point_of_sale.ProductScreen').ProductScreen = CustomProductScreen(ProductScreen);
});
