from odoo.tests.common import TransactionCase


class TranslatorManagerTestContent(TransactionCase):
    """
    Tests use-cases related to the creation of content and versions.
    """

    def setUp():
        super(TranslatorManagerTestContent, self).setUp()
        self.demo_content_site_1 = self.env.ref("demo_content_site_1")
    
    def test_new_content(self):
        """
        Tests if new content gets added to the database
        with both the base version and versions that need to be translated.
        """
        origin_lang = "fr"
        content_title = "This is a test dummy"
        url_path = "/test_content"

        self.demo_content_site_1.new_content(content_title, url_path, origin_lang)

        self.assertIsNotNone(None)

    def test_delete_content(self):
        pass

    def test_delete_version(self):
        pass
