# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   Prestashoperpconnect for OpenERP                                          #
#   Copyright (C) 2012 Akretion                                               #
#   Authors :                                                                 #
#           Sébastien BEAU <sebastien.beau@akretion.com>                      #
#           Mathieu VATEL <mathieu@julius.fr>                                 #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from osv import osv, fields
from base_external_referentials.decorator import only_for_referential
import time

class sale_order(osv.osv):
    _inherit='sale.order'

    @only_for_referential('prestashop')
    def _get_external_resources(self, cr, uid, external_session, external_id=None, resource_filter=None, mapping=None, fields=None, context=None):
        result = super(sale_order, self)._get_external_resources(cr, uid, external_session, \
                                            external_id=external_id, resource_filter=resource_filter, \
                                            mapping=mapping, fields=fields, context=context)
        for order in result:
            order_rows_ids = order['order_rows']
            order_rows_details = []
            if not isinstance(order_rows_ids, list):
                order_rows_ids = [order_rows_ids]
            for order_row_id in order_rows_ids:
                order_rows_details.append(self.pool.get('sale.order.line')._get_external_resources(cr, uid, \
                                                                            external_session, order_row_id, context=context)[0])
            order['order_rows'] = order_rows_details
        return result

    def _get_payment_information(self, cr, uid, external_session, order_id, resource, context=None):
        """
        Parse the external resource and return a dict of data converted
        """
        vals = super(sale_order, self)._get_payment_information(cr, uid, external_session, order_id, resource, context=context)
        vals['paid'] = bool(float(resource['total_paid_real']))
        vals['amount'] = float(resource['total_paid_real'])
        return vals

class sale_shop(osv.osv):
    _inherit = 'sale.shop'

    _columns = {
        'exportable_lang_ids': fields.many2many('res.lang', 'shop_lang_rel', 'lang_id', 'shop_id', 'Exportable Languages'),
    }

#    @only_for_referential('prestashop')
#    def update_orders(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {}
#        for shop in self.browse(cr, uid, ids):
#            #get all orders, which the state is not draft and the date of modification is superior to the last update, to exports
#            req = "select ir_model_data.res_id, ir_model_data.name from sale_order inner join ir_model_data on sale_order.id = ir_model_data.res_id where ir_model_data.model='sale.order' and sale_order.shop_id=%s and ir_model_data.referential_id IS NOT NULL "
#            param = (shop.id,)
#
#            if shop.last_update_order_export_date:
#                req += "and sale_order.write_date > %s"
#                param = (shop.id, shop.last_update_order_export_date)
#
#            cr.execute(req, param)
#            results = cr.fetchall()
#
#            for result in results:
#                ids = self.pool.get('sale.order').search(cr, uid, [('id', '=', result[0])])
#                if ids:
#                    id = ids[0]
#                    order = self.pool.get('sale.order').browse(cr, uid, id, context)
#                    order_ext_id = result[1].split('sale_order/')[1]
#                    self.update_shop_orders(cr, uid, order, order_ext_id, context)
#                    logging.getLogger('external_synchro').info("Successfully updated order with OpenERP id %s and ext id %s in external sale system" % (id, order_ext_id))
#            self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_update_order_export_date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
#        return False

#    @only_for_referential('prestashop')
#    def update_shop_orders(self, cr, uid, order, ext_id, context=None):
#        if context is None: context = {}
#        result = {}
#        date = '2012-04-15 10:46:57'
#        history_obj = self.pool.get('sale.order.history')
#        history_ids = history_obj.search(cr, uid, [('order_id', '=', order.id),('date_add', '>=', date)])
#        if history_ids:
#            self.export_history(cr, uid, [2], history_ids, context=context)
#        return result
#
#    def export_history(self, cr, uid, ids, history_ids, context=None):
#        self.export_resources(cr, uid, ids, history_ids, 'sale.order.history', context=context)
#        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
