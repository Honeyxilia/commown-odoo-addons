from odoo import fields, models


class Content(models.Model):
    _name = "commown_translation_manager.content"
    _description = "Textual content"

    _sql_constraints = [
        ("url_path_uniq", "unique (url_path)", "Content already exists!"),
    ]

    site_id = fields.Many2one(
        comodel_name="commown_translation_manager.content_site",
        string="Site",
        required=True,
        ondelete="cascade",
    )

    content_name = fields.Text(
        translate=True,
    )

    url_path = fields.Char(
        string="URL Path",
        required=True,
    )

    translation_ids = fields.One2many(
        comodel_name="commown_translation_manager.translation",
        inverse_name="content_id",
        string="Translations",
    )
