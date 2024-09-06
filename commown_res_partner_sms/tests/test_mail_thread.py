import requests_mock
from odoo_test_helper import FakeModelLoader

from odoo.tests.common import SavepointCase


class MailThreadTC(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a fake model to test abstract model MailThread
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import MailThreadTest

        cls.loader.update_registry((MailThreadTest,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_message_post_send_sms_html(self):
        mail_thread = self.env["mail.thread.test"].create({})
        html_message = "<div><p>TEST SMS</p><div>"
        message_num = len(mail_thread.message_ids)
        with requests_mock.Mocker() as rm:
            rm.get("https://www.ovh.com/cgi-bin/sms/http2sms.cgi", text="OK")
            mail_thread.message_post_send_sms_html(html_message, numbers=["0600070022"])
        self.assertEqual(len(mail_thread.message_ids), message_num + 1)
        sms = mail_thread.message_ids[0]
        self.assertEqual(sms.subtype_id, self.env.ref("mail.mt_note"))
        self.assertIn("SMS message sent", sms.body)
