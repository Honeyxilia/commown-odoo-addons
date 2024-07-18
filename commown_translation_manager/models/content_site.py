from odoo import fields, models


class ContentSite(models.Model):
    _name = "commown_translation_manager.content_site"
    _description = "Content site"

    _sql_constraints = [
        ("url_uniq", "unique (url)", "Site URL already exists!"),
        ("name_uniq", "unique (name)", "Site name already exists!"),
    ]

    name = fields.Char(
        string="Site Name",
        required=True,
    )

    url = fields.Char(
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
    )

    def action_open_site_requests(self):
        """
        Opens a kanban view with all related translation requests from site.
        """
        req_ids = (
            self.env["commown_translation_manager.translation_request"]
            .search([("origin_t10n_id.content_id.site_id", "=", self.id)])
            .ids
        )

        domain = "[('id', 'in', [%s])]" % ",".join(str(_id) for _id in req_ids)

        return {
            "type": "ir.actions.act_window",
            "res_model": "commown_translation_manager.translation_request",
            "name": self.name,
            "view_mode": "kanban,form",
            "view_type": "kanban",
            "domain": domain,
            "target": "current",
        }

    def new_content(self, title, url_path, base_ver_lang, content_url_path=""):
        """
        Create a content and all corresponding versions 
        after a new content is detected.
        """
        created_content = self.env["commown_translation_manager.content"].create({
            "name": title,
            "site_id": self.id,
            "url_path": url_path,
        })

        self.env["commown_translation_manager.version"].create({
            "content_id": created_content.id,
            "url_path": content_url_path if content_url_path else url_path,
            "language": base_ver_lang.id,
            "modification_date": fields.Datetime.now()
        })
