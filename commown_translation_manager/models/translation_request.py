from odoo import fields, models


class TranslationRequest(models.Model):
    _name = "commown_translation_manager.translation_request"
    _description = "Translation request of a content"

    origin_t10n_id = fields.Many2one(
        "commown_translation_manager.translation",
        required=True,
    )

    target_t10n_id = fields.Many2one(
        "commown_translation_manager.translation",
        required=True,
    )

    authors = fields.Many2many(
        "res.partner",
    )

    translator = fields.Many2one(
        "res.partner",
        required=True,
        relation="commown_translation_team_translation_request_translators_rel",
    )

    last_modification_date = fields.Date(
        required=True,
    )

    origin_lang = fields.Many2one(
        related="origin_t10n_id.language",
    )

    target_lang = fields.Many2one(
        related="target_t10n_id.language",
    )

    diffs = fields.Html(
        required=True,
    )
