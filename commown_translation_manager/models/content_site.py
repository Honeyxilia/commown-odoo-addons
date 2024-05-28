from odoo import fields, models


class ContentSite(models.Model):
    _name = "commown_translation_manager.content_site"
    _description = "Content site"
    _order = "site_name, site_url"
    _rec_name = "site_name"

    _sql_constraints = [
        ("url_uniq", "unique (site_url)", "Site URL already exists!"),
        ("name_uniq", "unique (site_name)", "Site name already exists!"),
    ]

    site_name = fields.Char(
        string="Site Name",
        required=True,
    )

    site_url = fields.Char(
        string="Site URL",
        required=True,
    )

    supported_langs = fields.Many2one(
        "res.lang",
        string="Supported languages",
    )

    content_ids = fields.One2many(
        comodel_name="commown_translation_manager.content",
        inverse_name="site_id",
        string="Contents",
        required=True,
    )
