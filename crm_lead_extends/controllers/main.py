# -*- coding: utf-8 -*-

import logging
import json
from datetime import date as dt

from odoo import http
from odoo.http import request as Request

_logger = logging.getLogger(__name__)

ACTIVITY_TYPE = {   'Llamada': 'mail.mail_activity_data_call',
                    'Email': 'mail.mail_activity_data_email',
                    'Whatsapp': 'crm_lead_extends.mail_activity_whatsapp'
                }

TEMPLATE = {
    'CETUS': 'crm_lead_extends.email_template_apto_CETUS',
    'CETI': 'crm_lead_extends.email_template_apto_CETI',
    'DELTA': 'crm_lead_extends.email_template_apto_DELTA',
    'TAU': 'crm_lead_extends.email_template_apto_TAU',
    'KAI': 'crm_lead_extends.email_template_apto_KAI',
    'MENKAR': 'crm_lead_extends.email_template_apto_MENKAR',
}


class LeadController(http.Controller):

    @http.route('/lead/outside', auth='public', methods=['POST'], csrf=False)
    def index(self, **kw):
        mail_activity = Request.env['mail.activity'].sudo()
        company_id = Request.env['res.company'].sudo().browse( int(kw.get('company_id')) )
        user_id = Request.env.ref('base.user_admin').sudo()
        crm_lead = Request.env['crm.lead'].sudo().with_context(lang=user_id.lang)

        _logger.info( kw )

        partner_id = Request.env['res.partner'].sudo().search([ ('email', '=', kw.get('email')), ('company_id', '=', company_id.id) ], limit=1)
        values = ( kw.get('contact_way'), kw.get('name'), kw.get('phone'), kw.get('email'), kw.get('apartment'), dt.today().strftime('%d-%m-%Y') )
        msg = "Forma de Contacto: %s\nNombre: %s\nPhone: %s\nEmail: %s\nApartamento: %s\nFecha: %s\n\n"%values
        if partner_id:
            lead_id = crm_lead.search([('partner_id', '=', partner_id.id ), ('company_id', '=', company_id.id), ('type', '=', 'lead')], limit=1)
        else:    
            lead_id = crm_lead.search([('email_from', '=', kw.get('email') ), ('company_id', '=', company_id.id), ('type', '=', 'lead')], limit=1)
        


        #        UTM's

        utm_source = Request.env['utm.source'].sudo().with_context(lang=user_id.lang)
        utm_medium = Request.env['utm.medium'].sudo().with_context(lang=user_id.lang)
        utm_campaign = Request.env['utm.campaign'].sudo().with_context(lang=user_id.lang)
        
        utm_source_id = utm_source.search( [('name', 'ilike', kw.get('utm_source') )], limit=1 )
        utm_medium_id = utm_medium.search( [('name', 'ilike', kw.get('utm_medium') )], limit=1 )
        utm_campaign_id = utm_campaign.search( [('name', 'ilike', kw.get('utm_campaign') )], limit=1 )

        if not utm_source_id and  kw.get('utm_source'):
            utm_source_id = utm_source.create( { 'name':  kw.get('utm_source')} )

        if not utm_medium_id and kw.get('utm_medium'):
            utm_medium_id = utm_medium.create( { 'name':  kw.get('utm_medium')} )

        if not utm_campaign_id and kw.get('utm_campaign'):
            utm_campaign_id = utm_campaign.create( { 'name':  kw.get('utm_campaign')} )


        if not lead_id:
            lead_id = crm_lead.create( {  
                                'name': "%s's Lead from MIRA.GT"%kw.get('name'),
                                'email_from': kw.get('email'),
                                'phone': kw.get('phone'),
                                'contact_name': kw.get('name'),
                                'user_id': user_id.id,
                                'type': 'lead',
                                'company_id': company_id.id,
                                'source_id': utm_source_id.id if utm_source_id else False,
                                'medium_id': utm_medium_id.id if utm_medium_id else False,
                                'campaign_id': utm_campaign_id.id if utm_campaign_id else False,
                                'apartment': kw.get('apartment'),
                            } )
        if company_id.default_sale_team_id:
            lead_id.write( {
                            'team_id': company_id.default_sale_team_id.id, 
                            'user_id': company_id.default_sale_team_id.user_id.id
                            
                            } )
            
        mail_activity.create( {
                                'res_model_id': Request.env.ref('crm.model_crm_lead').id,
                                'res_id': lead_id.id,
                                'user_id' : lead_id.user_id.id,
                                'note': msg,
                                'date_deadline': dt.today(),
                                'activity_type_id': Request.env.ref( ACTIVITY_TYPE[ kw.get('contact_way') ] ).id, 
                                'summary': 'Lead from MIRA.GT',
                            } )       
        # SEND MAIL
        if lead_id:
            template_id = Request.env.ref( TEMPLATE[ kw.get('apartment') ]  ).sudo()
            template_id.send_mail(lead_id.id, force_send=True)
            _logger.info( 'SENT!' )
                 
        return Request.make_response( json.dumps( {'ok': True} ) )