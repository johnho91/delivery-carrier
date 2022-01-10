# Copyright 2013-2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def generate_default_label(self):
        """Generate a label from a qweb report."""
        self.ensure_one()
        report = self.env.ref("delivery_carrier_label_default.default_label")
        file_, file_type = report._render(res_ids=self.ids)
        return {
            "name": "%s.%s" % (report.name, file_type),
            "file": base64.b64encode(file_),
            "file_type": file_type,
        }

    def _get_packages_from_picking(self):
        """ Get all the packages from the picking """
        self.ensure_one()
        operation_obj = self.env["stock.move.line"]
        packages = self.env["stock.quant.package"].browse()
        operations = operation_obj.search(
            [
                "|",
                ("package_id", "!=", False),
                ("result_package_id", "!=", False),
                ("picking_id", "=", self.id),
            ]
        )
        for operation in operations:
            # Take the destination package. If empty, the package is
            # moved so take the source one.
            packages |= operation.result_package_id or operation.package_id
        return packages
