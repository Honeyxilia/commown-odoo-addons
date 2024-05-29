from odoo import fields, models


class Content(models.Model):
    _name = "commown_translation_manager.content"
    _description = "Textual content"

    _sql_constraints = [
        ("url_path_uniq", "unique (url_path)", "Content already exists!"),
    ]

    name = fields.Text(
        translate=True,
    )

    site_id = fields.Many2one(
        comodel_name="commown_translation_manager.content_site",
        string="Site",
        required=True,
        ondelete="cascade",
    )

    url_path = fields.Char(
        string="URL Path",
    )

    translation_ids = fields.One2many(
        comodel_name="commown_translation_manager.translation",
        inverse_name="content_id",
        string="Translations",
    )
