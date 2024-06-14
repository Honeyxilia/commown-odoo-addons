from odoo import fields, models


class ContentVersion(models.Model):
    _name = "commown_translation_manager.version"
    _description = "Content version of a specific language"
    _order = "modification_date desc"

    _sql_constraints = [
        ("url_path_uniq", "unique (url_path)", "Content already exists!"),
    ]

    content_id = fields.Many2one(
        comodel_name="commown_translation_manager.content",
        string="Content",
        required=True,
        ondelete="cascade",
    )

    url_path = fields.Char(
        string="URL Path",
        required=True,
    )

    language = fields.Many2one(
        "res.lang",
        required=True,
    )

    modification_date = fields.Date(
        "Last modification date",
        required=True,
    )

    def create_request(self, diff, author):
        """
        Checks for existing requests and
        creates/modify an existing request accordingly
        """
        content_translation_requests = self.env["commown_translation_manager.translationrequests"].search([
            ("content_id", "=", self.id)
        ])

