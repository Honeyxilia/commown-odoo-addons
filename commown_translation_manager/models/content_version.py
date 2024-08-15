from odoo import fields, models
import ipdb


class ContentVersion(models.Model):
    _name = "commown_translation_manager.version"
    _description = "Content version of a specific language"
    _order = "modification_date desc"

    _sql_constraints = [
        ("url_path_uniq", "unique (url_path)", "Content already exists!"),
    ]

    content_id = fields.Many2one(
        comodel_name="commown_translation_manager.content",
        string="Content",
        required=True,
        ondelete="cascade",
    )

    url_path = fields.Char(
        string="URL Path",
        required=True,
    )

    language = fields.Many2one(
        "res.lang",
        required=True,
    )

    modification_date = fields.Datetime(
        "Last modification date",
        required=True,
    )

    def create_request(self, req_diff, author):
        """
        Checks for existing requests and
        creates/modify an existing request accordingly
        """

        self.modification_date = fields.Datetime.now()

        content_versions = self.env["commown_translation_manager.version"].search([
            ("content_id", "=", self.content_id.id),
            ("id", "!=", self.id)
        ])

        content_langs = []
        for ver in content_versions:
            content_langs += ver.language

        # Processing requests with current version as origin
        content_translation_requests_with_origin_ver = self.env["commown_translation_manager.translation_request"].search([
            ("origin_t10n_id", "=", self.id),
            ("is_closed", "=", False), 
        ])

        for req in content_translation_requests_with_origin_ver:
            content_langs.remove(req.target_lang)
            req.authors.append((6, 0, author.id))
            req.diffs += f"<br>___________<br>New modification detected on {self.modification_date.strftime('%y-%m-%d-%H-%M')}"

        # Processing requests with current version as target
        content_translation_requests_with_target_ver = self.env["commown_translation_manager.translation_request"].search([
            ("target_t10n_id", "=", self.id),
            ("is_closed", "=", False), 
        ])

        for req in content_translation_requests_with_target_ver:
            content_langs.remove(req.origin_lang)
            req.message_post(
                body=f"New modification to report :\n{req_diff}",
                message_type="comment"
            )

        # Creating a request for each remaining language
        created_reqs = []

        stage_new = self.env.ref("commown_translation_manager.stage_new")
        for ver in content_versions:
            if ver.language not in content_langs:
                continue

            created_reqs += self.env['commown_translation_manager.translation_request'].create({
                "create_date": self.modification_date,
                "origin_t10n_id": self.id,
                "target_t10n_id": ver.id,
                "authors": (6, 0, author.id),
                "diffs": req_diff,
                "stage_id": stage_new.id,
            })
            ipdb.set_trace()
