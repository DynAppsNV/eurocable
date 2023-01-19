# Copyright 2022 Eezee-IT (<http://www.eezee-it.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, api, _
from odoo.tools import float_round


class IntrastatReports(models.Model):
    _inherit = 'account.intrastat.report'
    _name = 'account.intrast.clients'

    def _get_columns_name(self, options):
        """ Insert new column Intrastat in report"""

        columns = [
            {'name': ''},
            {'name': _('System')},
            {'name': _('Country Code')},
            {'name': _('Transaction Code')},
        ]
        if self._show_region_code():
            columns += [
                {'name': _('Region Code')},
            ]
        columns += [
            {'name': _('Commodity Code')},
            {'name': _('Weight')},
            {'name': _('Quantity')},
            {'name': _('Value'), 'class': 'number'},
            {'name': _('Origin Country')},
            {'name': _('Partner VAT')},
        ]
        return columns

    def _build_query(self, date_from, date_to, journal_ids, invoice_types=None,
                     with_vat=False):
        """delete the join with the product in order to obtain all
        the lines with or without product"""
        invoice_types = ['out_invoice', 'out_refund']
        query, params = super(IntrastatReports, self)._build_query(date_from, date_to, journal_ids,
                                                                   invoice_types=invoice_types,
                                                                   with_vat=False)
        query['select'] = '''
            row_number() over () AS sequence,
            CASE WHEN inv.move_type IN ('out_invoice', 'out_refund')
            THEN %(export_merchandise_code)s ELSE
            %(export_merchandise_code)s END AS system,
            country.code AS country_code,
            country.name AS country_name,
            inv_line.quantity AS line_quantity,
            product_country.name AS intrastat_product_origin_country_name,
            company_country.code AS comp_country_code,
            transaction.code AS transaction_code,
            inv_line_intrastat.code AS intrastat,
            inv_line.id AS id,
            inv.id AS invoice_id,
            inv.currency_id AS invoice_currency_id,
            inv.name AS invoice_number,
            coalesce(inv.date, inv.invoice_date) AS invoice_date,
            inv.move_type AS invoice_type,
            inv_incoterm.code AS invoice_incoterm,
            comp_incoterm.code AS company_incoterm,
            inv_transport.code AS invoice_transport,
            comp_transport.code AS company_transport,
            CASE WHEN inv.move_type IN ('out_invoice', 'out_refund') THEN 'Arrival' ELSE 'Dispatch'
            END AS type, partner.vat as partner_vat,
            CASE WHEN inv_line.price_subtotal = 0 THEN inv_line.price_unit * inv_line.quantity ELSE
            inv_line.price_subtotal END AS value,
            inv_line.weight AS weight,
            inv_line.uom_id AS uom_id,
            inv_line.region_code AS region_code,
            inv_line.uom_category_id AS uom_category_id,
            inv_line.quantity AS quantity,
            inv_line.co_commd AS commodity_code,
            CASE WHEN inv_line.intrastat_transaction_id IS NULL THEN '1' ELSE transaction.code END AS trans_code,
        CASE WHEN inv_line.intrastat_product_origin_country_id IS NULL
             THEN \'QU\'
         ELSE product_country.code END AS intrastat_product_origin_country,
         CASE WHEN partner_country.id IS NULL THEN \'QV999999999999\'
             ELSE partner.vat
            END AS partner_vat
        '''
        query['from'] = '''
        account_move_line inv_line
            LEFT JOIN account_move inv ON inv_line.move_id = inv.id
            LEFT JOIN account_intrastat_code transaction ON inv_line.intrastat_transaction_id = transaction.id
            LEFT JOIN res_company company ON inv.company_id = company.id
            LEFT JOIN account_intrastat_code company_region ON company.intrastat_region_id = company_region.id
            LEFT JOIN res_partner partner ON inv_line.partner_id = partner.id
            LEFT JOIN res_partner comp_partner ON company.partner_id = comp_partner.id
            LEFT JOIN res_country country ON inv.intrastat_country_id = country.id
            LEFT JOIN res_country company_country ON comp_partner.country_id = company_country.id
            LEFT JOIN uom_uom inv_line_uom ON inv_line.product_uom_id = inv_line_uom.id
            LEFT JOIN account_incoterms inv_incoterm ON inv.invoice_incoterm_id = inv_incoterm.id
            LEFT JOIN account_incoterms comp_incoterm ON company.incoterm_id = comp_incoterm.id
            LEFT JOIN account_intrastat_code inv_line_intrastat ON inv_line.intrastat_id = inv_line_intrastat.id
            LEFT JOIN account_intrastat_code inv_transport ON inv.intrastat_transport_mode_id = inv_transport.id
            LEFT JOIN account_intrastat_code comp_transport ON company.intrastat_transport_mode_id = comp_transport.id
            LEFT JOIN res_country product_country ON product_country.id = inv_line.intrastat_product_origin_country_id
            LEFT JOIN res_country partner_country ON partner.country_id = partner_country.id AND
            partner_country.intrastat IS TRUE
            LEFT JOIN uom_uom ref_weight_uom on ref_weight_uom.category_id = %(weight_category_id)s and
            ref_weight_uom.uom_type = 'reference'
    '''
        query['where'] = '''
            inv.state = 'posted'
            AND inv_line.display_type IS NULL
            AND NOT inv_line.quantity = 0
            AND inv.company_id = %(company_id)s
            AND company_country.id != country.id
            AND country.intrastat = TRUE AND (country.code != 'GB' OR inv.date < '2021-01-01')
            AND coalesce(inv.date, inv.invoice_date) >= %(date_from)s
            AND coalesce(inv.date, inv.invoice_date) <= %(date_to)s
            AND inv.journal_id IN %(journal_ids)s
            AND inv.move_type IN %(invoice_types)s
            AND NOT inv_line.exclude_from_invoice_tab
            '''
        return query, params

    @api.model
    def _create_intrastat_report_line(self, options, vals):
        vals.update({
            'value': float_round(vals['value'], precision_rounding=1)
        })

        intrastat_report_line = super()._create_intrastat_report_line(options, vals)
        del(intrastat_report_line['columns'][4:6])
        intrastat_report_line['columns'].insert(4, {'name': vals['intrastat']})
        del (intrastat_report_line['columns'][7])
        del (intrastat_report_line['columns'][7])

        """recover data """
        origin_country = list(intrastat_report_line['columns'][5].values())[0]
        vat = list(intrastat_report_line['columns'][6].values())[0]
        prod_weight = list(intrastat_report_line['columns'][7].values())[0]
        qty = list(intrastat_report_line['columns'][8].values())[0]
        value = list(intrastat_report_line['columns'][9].values())[0]

        """Change position"""
        if prod_weight:
            intrastat_report_line['columns'][5] = {'name': int(float_round(prod_weight, precision_rounding=1))}
        else:
            intrastat_report_line['columns'][5] = {'name': ''}
        intrastat_report_line['columns'][6] = {'name': qty}
        intrastat_report_line['columns'][7] = {'name': value}
        intrastat_report_line['columns'][8] = {'name': origin_country}
        intrastat_report_line['columns'][9] = {'name': vat}
        return intrastat_report_line

    @api.model
    def _fill_missing_values(self, vals_list):
        """remove the behavior of this function"""
        return vals_list

    @api.model
    def _fill_supplementary_units(self, query_results):
        query_results = super()._fill_supplementary_units(query_results)
        for vals in query_results:
            if vals['supplementary_units'] is None:
                vals['supplementary_units'] = vals['line_quantity']
        return query_results

    def _get_filter_journals(self):
        # only show sale/purchase journals
        return self.env['account.journal'].search([
            ('company_id', 'in', self.env.companies.ids or [self.env.company.id]),
            ('type', '=', 'sale')
            ], order="company_id, name")
