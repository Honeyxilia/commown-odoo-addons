from odoo.tests.common import TransactionCase


class TranslatorManagerCommonTC(TransactionCase):
    """
    Shared methods in modules test classes (setUp).
    """
    def setUp(self, *args, **kwargs):
        super(TranslatorManagerCommonTC, self).setUp()
