from odoo import fields, models


class Translation(models.Model):
    _name = "commown_translation_manager.translation"
    _description = "Content translation"
    _order = "modification_date desc"

    _sql_constraints = [
        ("url_path_uniq", "unique (url_path)", "Content already exists!"),
    ]

    translator_id = fields.Many2one(
        "res.partner", 
        string="Translator",
    )
    
    content_id = fields.Many2one(
        "commown_translation_manager.content", 
        string="Content",
        required=True,
        ondelete="cascade",
    )

    url_path = fields.Char(
        string="URL Path",
        required=True,
    )
    
    language = fields.Char(
        "Language", 
        required=True,
    )

    modification_date = fields.Date(
        "Last modification date", 
        required=True,
    )
