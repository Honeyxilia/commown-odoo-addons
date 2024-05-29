from odoo import api, fields, models


class TranslationRequestStage(models.Model):
    _name = "commown_translation_manager.translation_request_stage"
    _description = "Stages for translation requests"

    name = fields.Char(
        required=True,
        translate=True,
    )

    description = fields.Text(
        translate=True,
    )

    sequence = fields.Integer()

    is_open = fields.Boolean(
        required=True,
    )


class TranslationRequest(models.Model):
    _name = "commown_translation_manager.translation_request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Translation request of a content"

    origin_t10n_id = fields.Many2one(
        "commown_translation_manager.translation",
        required=True,
    )

    target_t10n_id = fields.Many2one(
        "commown_translation_manager.translation",
        required=True,
    )

    content_id = fields.Many2one(
        "commown_translation_manager.content",
        related="origin_t10n_id.content_id",
    )

    authors = fields.Many2many(
        "res.partner",
    )

    translator = fields.Many2one(
        "res.partner",
        relation="commown_translation_team_translation_request_translators_rel",
    )

    origin_lang = fields.Many2one(
        related="origin_t10n_id.language",
        string="Origin language",
    )

    target_lang = fields.Many2one(
        related="target_t10n_id.language",
        string="Target language",
    )

    diffs = fields.Html(
        required=True,
    )

    stage_id = fields.Many2one(
        "commown_translation_manager.translation_request_stage",
        required=True,
    )

    is_open = fields.Boolean(
        related="stage_id.is_open",
    )

    @api.multi
    def name_get(self):
        result = []

        for record in self:
            result.append(
                (
                    record.id,
                    f"{record.origin_t10n_id.content_id.name}"
                    f" ({record.origin_lang.code} -> {record.target_lang.code})",
                )
            )
        
        return result

