{
    "name": "Commown SCIC",
    "category": "Business",
    "summary": "Commown SCIC business application",
    "version": "12.0.1.3.27",
    "description": "Commown SCIC business applications",
    "author": "Commown SCIC",
    "license": "AGPL-3",
    "website": "https://commown.coop",
    "depends": [
        "account_loan",
        "base_user_role",
        "survey",
        # Commown modules
        "account_invoice_merge_auto_pay",
        "account_move_slimpay_import",
        "commown_contract_forecast",
        "commown_shipping",
        "commown_ergonomy_asset",
        "commown_lead_risk_analysis",
        "contract_auto_merge_invoice",
        "website_sale_payment_slimpay",
        "commown_contract_variable_discount",
        "commown_self_troubleshooting",
        "payment_slimpay_issue",
        "commown_res_partner_sms",
        "payment_token_uniquify",
        "product_rental",
        "project_rating_nps",
        "sale_product_email",
        "custom_report",
        "slimpay_statements_autoimport",
        "website_sale_affiliate_portal",
        "website_sale_affiliate_product_restriction",
        "website_sale_b2b",
        "website_sale_coupon",
        # OCA modules
        "account_payment_sale",
        "account_mass_reconcile",
        "auth_admin_passkey",
        "auth_signup",
        "base_automation",
        "bi_sql_editor",
        "contract_queue_job",
        "contract_variable_quantity",
        "crm_phone",
        "mail_debrand",
        "mass_mailing_list_dynamic",
        "mass_mailing_partner",
        "portal",
        "sale_management",
        "web_m2x_options",
        "web_notify",
        "website_sale_cart_selectable",
        "website_sale_require_login",
    ],
    "external_dependencies": {
        "python": ["magic", "pdfminer"],
        "bin": ["rsvg-convert"],
    },
    "data": [
        "data/account_payment_term.xml",
        "data/account_mass_reconcile.xml",
        "data/mail_templates.xml",
        "data/obsolescence_action.xml",
        "data/product.xml",
        "data/product_public_category.xml",
        "data/project_project.xml",
        "data/payment_button.xml",
        "security/ir.model.access.csv",
        "views/account_invoice.xml",
        "views/account_move.xml",
        "views/actions_account_invoice.xml",
        "views/actions_crm_lead.xml",
        "views/actions_utm.xml",
        "views/address_template.xml",
        "views/auth_signup.xml",
        "views/contract_contract.xml",
        "views/contract_template.xml",
        "views/crm_lead.xml",
        "views/debrand_notification.xml",
        "views/ir_attachment.xml",
        "views/payment_portal_templates.xml",
        "views/product_template.xml",
        "views/project_project.xml",
        "views/project_task.xml",
        "views/res_lang.xml",
        "views/res_partner.xml",
        "views/survey.xml",
        "views/website_portal_templates.xml",
        "views/website_sale_templates.xml",
        "views/website_site_portal_sale_templates.xml",
        "views/website_templates.xml",
    ],
    "qweb": [
        "static/src/xml/account_reconciliation.xml",
    ],
    "installable": True,
    "application": True,
}
