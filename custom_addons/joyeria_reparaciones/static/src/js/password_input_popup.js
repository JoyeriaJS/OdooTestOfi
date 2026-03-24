/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class PasswordInputPopup extends Component {
    static template = "joyeria_reparaciones.PasswordInputPopup";
    static components = { Dialog };
    static props = {
        close: Function,
        title: { type: String, optional: true },
        body: { type: String, optional: true },
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            value: "",
        });
    }

    confirm() {
        this.props.close({
            confirmed: true,
            payload: this.state.value,
        });
    }

    cancel() {
        this.props.close({
            confirmed: false,
            payload: null,
        });
    }
}