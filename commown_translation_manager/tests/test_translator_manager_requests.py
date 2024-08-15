from datetime import datetime
from odoo import fields
from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TranslatorManagerRequestsTC(SavepointCase):
    """
    Tests use-cases relating to the creation of new translation requests
    """

    def setUp(self):
        super().setUp()

        self.test_author = self.env['res.partner'].search([("id", "=", 13757)])
        self.test_diffs = "This is a diff of a file <br> second line c:"

    def test_new_request(self):
        """
        Tests whether the creation of a new request is functionnal
        """
        before_create_time = fields.Datetime.now()

        content_version_3_de = self.env.ref("commown_translation_manager.demo_translation_3_de")
        rtn_value = content_version_3_de.create_request(self.test_diffs, self.test_author)

        requests_created = self.env['commown_translation_manager.translation_request'].search([
            ("origin_t10n_id", "=", content_version_3_de.id),
            ("is_closed", "=", False),
            ("create_date", ">=", datetime.strftime(before_create_time, "%Y-%m-%d %H:%M:%S")),
        ])

        self.assertEqual(len(requests_created.ids), 1)
        
        req_created = requests_created[0]
        
        self.assertEqual(req_created.target_lang.iso_code, "fr")


    def test_request_already_exists_origin_lang(self):
        """
        Tests behavior when a request already exists, from the current language to other languages.
        """
        content_version_1_fr = self.env.ref("commown_translation_manager.demo_translation_1_fr")
        content_version_1_fr.create_request(self.test_diffs, self.test_author)

        updated_requests = self.env["commown_translation_manager.translation_request"].search([
            ("origin_t10n_id", "=", content_version_1_fr.id),
            ("is_closed", "=", False)
        ])

        self.assertEqual(len(translation_requests_created), 1)


    def test_request_already_exists_target_lang(self):
        """
        Tests behavior when a request already exists, from one or different languages to the current language.
        """
        content_version_2_fr = self.env.ref("demo_translation_2_fr")
        content_version_2_fr.create_request(self.test_diffs, self.test_author)

        self.env["commown_translation_manager.translation_request"].search_count([
            ("target_t10n_id", "=", content_version_2_de),
            ("is_closed", "=", False)
        ])
