from odoo import api, fields, models


class TranslationRequestStage(models.Model):
    _name = "commown_translation_manager.translation_request_stage"
    _description = "Stages for translation requests"
    _fold_name = "is_closed"

    name = fields.Char(
        required=True,
        translate=True,
    )

    description = fields.Text(
        translate=True,
    )

    sequence = fields.Integer()

    is_closed = fields.Boolean(
        required=True,
    )


class TranslationRequest(models.Model):
    _name = "commown_translation_manager.translation_request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Translation request of a content"

    origin_t10n_id = fields.Many2one(
        "commown_translation_manager.version",
        required=True,
    )

    target_t10n_id = fields.Many2one(
        "commown_translation_manager.version",
        required=True,
    )

    content_id = fields.Many2one(
        "commown_translation_manager.content",
        related="origin_t10n_id.content_id",
    )

    authors = fields.Many2many(
        "res.partner",
    )

    translator_id = fields.Many2one(
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

    @api.model
    def _read_group_stages_ids(self, stages, domain, order):
        return self \
            .env["commown_translation_manager.translation_request_stage"] \
            .search([])

    stage_id = fields.Many2one(
        "commown_translation_manager.translation_request_stage",
        group_expand="_read_group_stages_ids",
        track_visibility="is_closed",
        help="Select the current stage of the translation",
        required=True,
    )

    is_closed = fields.Boolean(
        related="stage_id.is_closed",
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

