from odoo.tests.common import TransactionCase


class TranslatorManagerRequestsTC(TranslatorManagerCommonTC):
    """
    Tests use-cases relating to the creation of new translation requests
    """

    def setUp():
        super(TransactionCase, self).setUp()
        self.content_version_2_de = self.env.ref("commown_translation_manager.demo_translation_2_de")

    def test_new_request(self):
        """
        Tests whether the creation of a new request is functionnal
        """
        author = self.env['res.partner'].search([("id", "=", 13757)])
        diff = "This is a diff of a file \n c:"

        content_version.content_id.create_request()    

    def test_request_already_exists_origin_lang(self):
        """
        Tests behavior when a request already exists, from the current language to other languages.
        """
        pass

    def test_request_already_exists_target_lang(self):
        """
        Tests behavior when a request already exists, from one or different languages to the current language.
        """
        pass

    def test_request_already_exists_other_langs(self):
        """
        Tests behavior when a request exists concerning only other languages than the current one
        """
        pass
