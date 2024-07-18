from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TranslatorManagerContentTC(SavepointCase):
    """
    Tests use-cases related to the creation of content and versions.
    """
    def setUp(self):
        super().setUp()

        self.demo_content_site_1 = self.env.ref("commown_translation_manager.demo_content_site_1")
    
    def test_new_content(self):
        """
        Tests if new content gets added to the database
        with both the base version and versions that need to be translated.
        """
        origin_lang = self.env.ref("base.lang_fr")
        content_title = "This is a test dummy"
        url_path = "/test_content"

        test_created_content = self.demo_content_site_1.new_content(content_title, url_path, origin_lang)

        created_content_versions = self.env['commown_translation_manager.content_version'].search_count([
            ("content_id", "=", test_created_content.id)
        ])

        self.assertEqual(len(created_content_versiwons.ids), 2)

    def test_delete_content(self):
        pass

    def test_delete_version(self):
        self.assertEqual(
            self.env['commown_translation_manager.content_version'].search_count([
                ("content_id", "=", 0),
                ("language", "=", "fr")
            ]),
            0
        )
