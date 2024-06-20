from odoo.tests.common import TransactionCase


class TranslatorManagerRequestsTC(TranslatorManagerCommonTC):
    """
    Tests use-cases relating to the creation of new translation requests
    """

    def setUp():
        super(TransactionCase, self).setUp()

        self.test_author = self.env['res.partner'].search([("id", "=", 13757)])
        self.test_diffs = "This is a diff of a file <br> second line c:"

    def test_new_request(self):
        """
        Tests whether the creation of a new request is functionnal
        """
        content_version_3_de = self.env.ref("commown_translation_manager.demo_translation_2_de")
        content_version_3_de.create_request(self.test_diffs, self.test_author)

        self.assertEqual(
            self.env['commown_translation_manager.translation_request'].search_count([
                ("origin_t10n_id", "=", content_version_3_de.id),
                ("is_closed", "=", False)
            ]),
            1
        )

    def test_request_already_exists_origin_lang(self):
        """
        Tests behavior when a request already exists, from the current language to other languages.
        """
        content_version_1_fr = self.env.ref("commown_translation_manager.demo_translation_1_fr")
        content_version_1_fr.create_request(self.test_diffs, self.test_author)

        self.assertEqual(
            self.env["commown_translation_manager.translation_request"].search_count([
                ("origin_t10n_id", "=", content_version_1_fr.id),
                ("is_closed", "=", False)
            ]),
            1
        )

    def test_request_already_exists_target_lang(self):
        """
        Tests behavior when a request already exists, from one or different languages to the current language.
        """
        content_version_2_fr = self.env.ref("demo_translation_2_fr")
        content_version_2_fr.create_request(self.test_diffs, self.test_author)

        self.assertEqual(
            self.env["commown_translation_manager.translation_request"].search_count([
                ("target_t10n_id", "=", content_version_2_de),
                ("is_closed", "=", False)
            ]),
            1
        )

