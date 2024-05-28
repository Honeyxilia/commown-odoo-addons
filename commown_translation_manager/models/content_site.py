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

    supported_langs = fields.Many2many(
        "res.lang",
        string="Supported languages",
    )

    content_ids = fields.One2many(
        comodel_name="commown_translation_manager.content",
        inverse_name="site_id",
        string="Contents",
        required=True,
    )

    def action_open_site_requests(self):
        """
            Opens a kanban view with all related translation requests from site.
        """
        req_ids = self.env["commown_translation_manager.translation_request"].search(
                [('origin_t10n_id.content_id.site_id', '=', self.id)]
            ).ids
        
        domain = None
        
        if req_ids:
            domain = "[('id', 'in', [%s])]" % ",".join(str(_id) for _id in req_ids)

        return {
            "type": "ir.actions.act_window",
            "res_model": "commown_translation_manager.translation_request",
            "name": self.site_name,
            "view_mode": "kanban,form",
            "view_type": "kanban",
            "domain": domain,
            "target": "current",
        }
