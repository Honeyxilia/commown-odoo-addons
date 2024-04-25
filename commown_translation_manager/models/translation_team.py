from odoo import fields, models


class TranslationTeam(models.Model):
    _name = "commown_translation_manager.translation_team"
    _description = "Translation team"

    translators = fields.Many2many(
        "res.partner",
        string="Translators",
    )

    initial_lang = fields.Selection(
        string="Initial language",
        related="lang",
        required="true",
    )

    target_lang = fields.Selection(
        string="Target language",
        related="lang",
        required="true",
    )
