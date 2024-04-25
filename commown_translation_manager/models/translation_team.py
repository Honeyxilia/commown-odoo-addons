from odoo import fields, models


class TranslationTeam(models.Model):
    _name = "commown_translation_manager.translation_team"
    _description = "Translation team"

    name = fields.Char(
        required=True,
    )

    translators = fields.Many2many(
        "res.users",
        domain="[('share','=',False)]",
        string="Translators",
    )

    initial_lang = fields.Many2one(
        "res.lang",
        string="Initial language",
        required="true",
    )

    target_lang = fields.Many2one(
        "res.lang",
        string="Target language",
        required="true",
    )
