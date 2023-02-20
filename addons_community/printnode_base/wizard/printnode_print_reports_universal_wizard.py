# Copyright 2021 VentorTech OU
# See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models, _


REPORT_DOMAIN = [
    ('report_type', 'in', ['qweb-pdf', 'qweb-text', 'py3o']),
    ('report_name', 'not in', [
        'sale.report_saleorder_pro_forma',
        'product.report_pricelist',
        'product.report_producttemplatelabel',
        'product.report_producttemplatelabel_dymo',
        'stock.label_product_product_view',
    ]),
]


class PrintnodePrintReportsUniversalWizard(models.TransientModel):
    _name = 'printnode.print.reports.universal.wizard'
    _description = 'Print Reports Wizard'

    report_id = fields.Many2one(
        comodel_name='ir.actions.report',
        domain=lambda self: self._get_available_reports()
    )

    number_copy = fields.Integer(
        default=1,
        string='Copies',
    )

    with_custom_qty = fields.Boolean(
        string="Custom quantity for each record (Experimental)",
        default=False,
    )

    record_line_ids = fields.One2many(
        comodel_name='printnode.print.reports.universal.wizard.line',
        inverse_name='wizard_id',
        string='Records',
        default=lambda self: self._get_record_line_ids(),
    )

    record_names = fields.Text(
        string='Will be printed',
        readonly=True,
        compute='_compute_record_names',
    )

    printer_id = fields.Many2one(
        comodel_name='printnode.printer',
        default=lambda self: self._default_printer_id(),
    )

    printer_bin = fields.Many2one(
        'printnode.printer.bin',
        string='Printer Bin',
        required=False,
        domain='[("printer_id", "=", printer_id)]',
    )

    status = fields.Char(related='printer_id.status')

    def _default_printer_id(self):
        """
        Return default printer for wizard
        """
        # There can be default report from settings (this method called before the deafult value
        # to report_id will be applied)
        report_id = self.report_id

        # User rules
        user_rules_printer_id = self.env['printnode.rule'].search([
            ('user_id', '=', self.env.uid),
            ('report_id', '=', report_id.id),  # There will be no rules for report_id = False
        ], limit=1).printer_id

        # Workstation printer
        workstation_printer_id = self.env.user._get_workstation_device(
            'printnode_workstation_printer_id')

        # Priority:
        # 1. Printer from User Rules (if exists)
        # 2. Default Workstation Printer (User preferences)
        # 3. Default printer for current user (User Preferences)
        # 4. Default printer for current company (Settings)
        return user_rules_printer_id or workstation_printer_id or \
            self.env.user.printnode_printer or self.env.company.printnode_printer

    @api.constrains('number_copy')
    def _check_quantity(self):
        for rec in self:
            if rec.number_copy < 1:
                raise exceptions.ValidationError(
                    _('Quantity can not be less than 1')
                )

    @api.onchange('printer_id')
    def _onchange_printer(self):
        """
        Reset printer_bin field to avoid bug with printing
        in wrong bin
        """
        self.printer_bin = self.printer_id.default_printer_bin.id

    @api.onchange('report_id')
    def _onchange_wizard_printer(self):
        self.printer_id = self._default_printer_id()

    def get_report(self):
        self.ensure_one()
        return self.report_id

    def get_docids(self):
        self.ensure_one()
        objects = self._get_records()
        return objects

    def _get_records(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if not (active_ids and active_model):
            return

        return self.env[active_model].browse(active_ids)

    @api.depends('record_line_ids')
    def _compute_record_names(self):
        # Update record_id field based on active_model value from context
        self.record_line_ids._update_record_id_field()

        for rec in self:
            record_names = [
                record_line.record_id.display_name
                for record_line in rec.record_line_ids
            ]
            self.record_names = ", ".join(record_names)

    def _get_available_reports(self):
        active_model = self.env.context.get('active_model')
        return [*REPORT_DOMAIN, ('model', '=', active_model)]

    def _get_record_line_ids(self):
        record_ids = self._get_records()

        lines_vals = [{'record_id': rec.id} for rec in record_ids]
        record_line_ids = self.env['printnode.print.reports.universal.wizard.line'].create(
            lines_vals)

        return [(6, 0, record_line_ids.ids)]

    def do_print(self):
        self.ensure_one()

        # Update record_id field based on active_model value from context
        self.record_line_ids._update_record_id_field()

        report = self.get_report()

        if not report or not self.record_line_ids:
            raise exceptions.UserError(_('No documents to print!'))

        # Create empty recordset
        active_model = self.env.context.get('active_model')
        docids = self.env[active_model]

        # Add copies
        if not self.with_custom_qty:
            # The same quantity for all records
            for i in range(self.number_copy):
                docids = docids.concat(self.record_line_ids.mapped('record_id'))
        else:
            # Custom quantity for each record
            for line in self.record_line_ids:
                for i in range(line.quantity):
                    docids += line.record_id

        # If no printer than download PDF
        if not self.printer_id:
            return report.with_context(download_only=True).report_action(docids=docids)

        options = {}
        if self.printer_bin:
            options['bin'] = self.printer_bin.name

        # If printer than send to printnode
        self.printer_id.printnode_print(
            report,
            docids,
            options=options,
        )

        title = _('Report was sent to printer')
        message = _('Document "{}" was sent to printer {}').format(
            report.name, self.printer_id.name)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }


class PrintnodePrintReportsUniversalWizardLine(models.TransientModel):
    _name = 'printnode.print.reports.universal.wizard.line'
    _description = 'Record Line'

    record_id = fields.Integer(
        # Hacky way to set dynamic field
        # Made this field to be integer because most of IDs are integer
    )

    quantity = fields.Integer(
        required=True,
        default=1,
    )

    wizard_id = fields.Many2one(
        comodel_name='printnode.print.reports.universal.wizard',
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity < 1:
                raise exceptions.ValidationError(
                    _('Quantity can not be less than 1 for product {product}').format(
                        product=rec.product_id.display_name)
                )

    @api.model
    def create(self, vals):
        # Update type of record_id field based on active_model value from context
        self._update_record_id_field()

        return super().create(vals)

    def read(self, fields=None, load='_classic_read'):
        # Update type of record_id field based on active_model value from context
        self._update_record_id_field()

        return super().read(fields, load)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        # Update type of record_id field based on active_model value from context
        self._update_record_id_field()

        return super().fields_get(allfields, attributes)

    def _update_record_id_field(self):
        active_model = self.env.context.get('active_model')

        if self.env.context.get('install_mode') or not active_model:
            # Do nothing on module installation or no active_model in context
            return

        field = fields.Many2one(comodel_name=active_model)

        self._pop_field('record_id')
        self._add_field('record_id', field)
        field.setup(self)
