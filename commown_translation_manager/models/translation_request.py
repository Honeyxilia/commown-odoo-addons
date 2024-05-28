from odoo import fields, models


class translationRequest(models.Model):
    _name = "commown_translation_manager.translation_request"
    _description = "Translation request of a content"

    content_translation_id = fields.Many2one(
        "commown_translation_manager.translation",
        required=True,
    )

    translator = fields.Many2one(
        "res.partner",
        required=True,
    )

    modification_date = fields.Date(
        required=True,
    )

    origin_lang = fields.Many2one(
        "res.lang",
        required=True,
    )

    target_lang = fields.Many2one(
        "res.lang",
        required=True,
    )

    modifications = fields.Html(
        required=True,
    )
