from odoo import api, fields, models


class Content(models.Model):
    _name = "commown_translation_manager.content"
    _description = "Textual content"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
        comodel_name="commown_translation_manager.version",
        inverse_name="content_id",
        string="Translations",
    )

    request_ids = fields.One2many(
        comodel_name="commown_translation_manager.translation_request",
        inverse_name = "content_id",
    )

    def send_create_vers_messages(self):
        translators_teams = self.env["commown_translation_manager.translation_team"].search([
            ("target_lang", "in", self.site_id.supported_langs.ids),
        ])

        self.message_subscribe(translators_teams.mapped("translator_ids"))

        # TODO : Post a message with a template to prompt other languages of a translation


    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        new_content = super().create(vals)
        
        new_content.send_create_vers_messages()

        return new_content
