from datetime import date, timedelta

import requests_mock
from mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.product_rental.tests.common import MockedEmptySessionMixin
from odoo.addons.queue_job.tests.common import trap_jobs

from ..models.colissimo_utils import shipping_data
from ..models.delivery_mixin import CommownTrackDeliveryMixin as DeliveryMixin
from .common import BaseShippingTC, pdf_page_num


class CheckMailMixin:
    "Small helper class to check sent emails easily"

    def _check_mail(self, mail, subject, content, check_recipients=None):
        self.assertEqual(mail.message_type, "notification")
        self.assertEqual(mail.subject, subject)
        self.assertIn(content, mail.body)
        if check_recipients is not None:
            self.assertItemsEqual(mail.partner_ids.mapped("name"), check_recipients)
        return mail


class CrmLeadShippingTC(MockedEmptySessionMixin, BaseShippingTC):
    def setUp(self):
        super(CrmLeadShippingTC, self).setUp()

        self.sender = self.env.ref("base.res_partner_2")
        self.sender.update(
            {
                "country_id": self._country("FR"),
                "mobile": "0601020304",
            }
        )

        partner = self.env.ref("base.res_partner_1")
        product = self.env["product.product"].create(
            {"name": "Fairphone", "shipping_parcel_type_id": self.parcel_type.id}
        )
        team = self.env.ref("sales_team.salesteam_website_sales")
        team.shipping_account_id = self.shipping_account

        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "name": product.name,
                            "product_uom_qty": 1,
                            "price_unit": product.list_price,
                        },
                    )
                ],
            }
        )

        self.lead = self.env["crm.lead"].create(
            {
                "name": "[SO00000] Fake order",
                "partner_id": partner.id,
                "type": "opportunity",
                "team_id": team.id,
                "so_line_id": so.order_line[0].id,
            }
        )

    def _country(self, code):
        return self.env["res.country"].search([("code", "=", code)])

    def test_shipping_data_product_code(self):
        base_kwargs = {
            "sender": self.sender,
            "recipient": self.lead.partner_id,
            "order_number": "SO00000",
            "commercial_name": "Commown",
            "weight": 0.5,
        }

        # French label
        self.lead.partner_id.country_id = self._country("FR")
        data = shipping_data(**base_kwargs)
        self.assertEqual(data["letter"]["service"]["productCode"], "DOS")

        # French return label
        data = shipping_data(is_return=True, **base_kwargs)
        self.assertEqual(data["letter"]["service"]["productCode"], "CORE")

        # International label
        self.lead.partner_id.country_id = self._country("BE")
        data = shipping_data(**base_kwargs)
        self.assertEqual(data["letter"]["service"]["productCode"], "COLI")

        # International Return label
        self.lead.partner_id.country_id = self._country("BE")
        data = shipping_data(is_return=True, **base_kwargs)
        self.assertEqual(data["letter"]["service"]["productCode"], "CORI")

    def print_label(self, leads, parcel_type, use_full_page_per_label=False):
        return self._print_label(
            "commown_shipping.lead.print_label.wizard",
            leads,
            parcel_type,
            use_full_page_per_label,
        )

    def test_shipping_data_empty_name(self):
        self.lead.partner_id.firstname = False
        data = shipping_data(
            sender=self.sender,
            recipient=self.lead.partner_id,
            order_number="SO00000",
            commercial_name="Commown",
            weight=0.5,
        )
        self.assertEqual(data["letter"]["addressee"]["address"]["firstName"], "")

    @requests_mock.Mocker()
    def test_create_parcel_label(self, mocker):
        lead = self.lead

        self.mock_colissimo_ok(mocker)

        lead._create_parcel_label(
            self.parcel_type,
            self.shipping_account,
            lead.partner_id,
            lead.get_label_ref(),
        )

        self.assertEqual(lead.expedition_ref, "6X0000000000")
        self.assertEqual(lead.expedition_date, date.today())
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "crm.lead"), ("res_id", "=", lead.id)]
        )
        self.assertEqual(len(attachments), 1)
        att = attachments[0]
        self.assertEqual(att.datas_fname, "6X0000000000.pdf")
        self.assertEqual(att.name, self.parcel_type.name + ".pdf")
        self.assertEqualFakeLabel(att)

    def test_print_parcel_action(self):
        leads = self.env["crm.lead"]
        for num in range(5):
            leads += self.lead.copy({"name": "[SO%05d] Test lead" % num})

        with requests_mock.Mocker() as mocker:
            self.mock_colissimo_ok(mocker)
            all_labels = self.print_label(leads, self.parcel_type)

        self.assertEqual(all_labels.name, self.parcel_type.name + ".pdf")
        self.assertEqual(pdf_page_num(all_labels), 2)

    def test_recipient_partner(self):
        so = self.lead.so_line_id.order_id
        so.partner_shipping_id = self.lead.partner_id.copy({"name": "SO Delivery"})

        # Test pre-requisites:
        self.assertFalse(self.lead.recipient_partner_id)

        # Real test:
        self.assertEqual(self.lead._recipient_partner(), so.partner_shipping_id)

    def test_onchange_expedition_ref(self):
        # Check Pre-requisite
        self.assertFalse(self.lead.expedition_ref)

        # Check different cases
        self.lead.expedition_ref = " AA JJ PP\n"
        self.lead._normalize_expedition_ref()
        self.assertEqual(self.lead.expedition_ref, "AAJJPP")

        ref_with_link = "Link: http://unsecured_link.coop"
        self.lead.expedition_ref = ref_with_link
        self.lead._normalize_expedition_ref()
        self.assertEqual(self.lead.expedition_ref, ref_with_link)

        ref_with_link = "Link: https://secured_link.coop"
        self.lead.expedition_ref = ref_with_link
        self.lead._normalize_expedition_ref()
        self.assertEqual(self.lead.expedition_ref, ref_with_link)

        # Test onchange loop stop with context (no normalization)
        ref = " AA JJ PP\n"
        self.lead.expedition_ref = ref
        self.lead.with_context(
            in_onchange_expedition_ref=True
        )._normalize_expedition_ref()
        self.assertEqual(self.lead.expedition_ref, ref)

    def test_check_expedition_ref(self):
        stage = self.env["crm.stage"].create({"name": "TEST [log: check exp-ref]"})
        # Check Pre-requisite
        self.assertFalse(self.lead.expedition_ref)

        expected_msg = "Lead has no expedition ref. Please fill it in."

        with self.assertRaises(ValidationError) as err:
            self.lead.stage_id = stage
        self.assertEqual(err.exception.args, (expected_msg, None))

        self.lead.expedition_ref = "TESTREFFF"
        self.lead.stage_id = stage

        # Check results
        self.assertEqual(self.lead.stage_id, stage)


class CrmLeadDeliveryTC(TransactionCase, CheckMailMixin):
    def setUp(self):
        super(CrmLeadDeliveryTC, self).setUp()
        team = self.env.ref("sales_team.salesteam_website_sales")
        team.update(
            {
                "delivery_tracking": True,
                "on_delivery_email_template_id": self.env.ref(
                    "commown_shipping.delivery_email_example"
                ).id,
            }
        )
        self.lead = self.env["crm.lead"].create(
            {
                "name": "[SO99999-01] TEST DELIVERY",
                "partner_id": self.env.ref("base.res_partner_1").id,
                "type": "opportunity",
                "team_id": team.id,
            }
        )

    def _last_message(self):
        return self.env["mail.message"].search(
            [("res_id", "=", self.lead.id), ("model", "=", "crm.lead")]
        )[0]

    def check_mail_delivered(self, subject, code):
        return self._check_mail(self._last_message(), subject, "code: " + code)

    def test_delivery_email_template(self):
        # Shipping deactivated, template set => None expected
        self.lead.team_id.delivery_tracking = False
        assert (
            self.lead.team_id.on_delivery_email_template_id
        ), "test prerequisite error"
        self.assertIsNone(self.lead.delivery_email_template())

        # Shipping activated, no lead custom template => custom expected
        self.lead.team_id.delivery_tracking = True
        self.lead.on_delivery_email_template_id = False
        self.assertEqual(
            self.lead.delivery_email_template(),
            self.lead.team_id.on_delivery_email_template_id,
        )

        # Shipping activated, custom template => custom expected
        self.lead.on_delivery_email_template_id = (
            self.lead.team_id.on_delivery_email_template_id.copy().id
        )
        self.assertEqual(
            self.lead.delivery_email_template().name, "Post-delivery email (copy)"
        )

        # Shipping deactivated, even with custom template => None expected
        self.lead.team_id.delivery_tracking = False
        self.assertIsNone(self.lead.delivery_email_template())

    def test_actions_on_delivery_send_email_team_template(self):

        self.assertTrue(self.lead.send_email_on_delivery)

        # Simulate delivery
        self.lead.expedition_status = "[LIVCFM] Test"
        self.lead.delivery_date = date(2018, 1, 1)

        # Check result
        self.check_mail_delivered("Product delivered", "LIVCFM")

    def test_actions_on_delivery_send_email_no_status(self):
        "Check empty expedition status is OK"

        self.assertTrue(self.lead.send_email_on_delivery)

        # Simulate delivery
        self.lead.expedition_status = False
        self.lead.delivery_date = "2018-01-01"

        # Check result
        self.check_mail_delivered("Product delivered", "EMPTY_CODE")

    def test_actions_on_delivery_send_email_custom_template(self):

        self.assertTrue(self.lead.send_email_on_delivery)

        self.lead.on_delivery_email_template_id = (
            self.lead.team_id.on_delivery_email_template_id.copy(  # noqa: B950
                {"subject": "Test custom email"}
            ).id
        )

        # Simulate delivery
        self.lead.expedition_status = "[LIVGAR] Test"
        self.lead.delivery_date = "2018-01-01"

        # Check result
        self.check_mail_delivered("Test custom email", "LIVGAR")

    def test_actions_on_delivery_send_email_no_template(self):
        "A user error must be raised in the case no template was specified"

        self.assertTrue(self.lead.send_email_on_delivery)
        self.lead.on_delivery_email_template_id = False
        self.lead.team_id.on_delivery_email_template_id = False

        # Simulate delivery
        self.assertRaises(UserError, self.lead.update, {"delivery_date": "2018-01-01"})


def _status(code, label="test label", _date=None):
    return {"code": code, "label": label, "date": _date or date.today().isoformat()}


class CrmLeadDeliveryTrackingTC(TransactionCase, CheckMailMixin):
    def setUp(self):
        super(CrmLeadDeliveryTrackingTC, self).setUp()

        account = self.env.ref(
            "commown_shipping.shipping-account-colissimo-std-account"
        )
        self.team = self.env.ref("sales_team.salesteam_website_sales")
        mt_id = self.env.ref("commown_shipping.delivery_email_example").id
        self.team.update(
            {
                "delivery_tracking": True,
                "shipping_account_id": account.id,
                "default_perform_actions_on_delivery": False,
                "on_delivery_email_template_id": mt_id,
            }
        )
        self.stage_track = self._add_stage("Wait [colissimo: tracking]", self.team)
        self.lead1 = self._add_lead("l1", self.stage_track, self.team, "ref1")
        self.lead2 = self._add_lead("l2", self.stage_track, self.team, "ref2")
        self.lead3 = self._add_lead("l3", self.stage_track, self.team, "https://c.coop")
        self.stage_final = self._add_stage("OK [colissimo: final]", self.team)
        self.lead4 = self._add_lead("l4", self.stage_final, self.team, "ref4")

    def _add_stage(self, name, team, **kwargs):
        kwargs.update({"name": name, "team_id": team.id})
        return self.env["crm.stage"].create(kwargs)

    def _add_lead(self, name, stage, team, ref, **kwargs):
        kwargs.update(
            {
                "name": name,
                "stage_id": stage.id,
                "team_id": team.id,
                "expedition_ref": ref,
            }
        )
        return self.env["crm.lead"].create(kwargs)

    def test_tracked_records(self):
        team2 = self.stage_track.team_id.copy(
            {"name": "Test team", "delivery_tracking": False}
        )
        stage_track2 = self._add_stage("Wait2 [colissimo: tracking]", team2)
        self._add_lead("l21", stage_track2, team2, "l21ref")
        self._add_stage("Done2 [colissimo: final]", team2)

        self.assertEqual(
            self.env["crm.lead"]._delivery_tracked_records().ids,
            [self.lead2.id, self.lead1.id],
        )

    def exec_job_with_status(self, lead_statuses):
        """Run the delivery jobs mocking colissimo WS with given status
        Return the leads in the order of their name in `lead_statuses`.
        """
        with trap_jobs() as trap:
            leads = self.env["crm.lead"]._cron_delivery_auto_track()

        trap.assert_jobs_count(len(lead_statuses))

        for job in trap.enqueued_jobs:
            with patch.object(
                DeliveryMixin,
                "_delivery_tracking_colissimo_status",
                side_effect=lambda *args: lead_statuses[job.recordset.name],
            ):
                job.perform()

        return leads.sorted(lambda l: list(lead_statuses.keys()).index(l.name))

    def test_cron_ok1(self):
        leads = self.exec_job_with_status({l: _status("LIVCFM") for l in ("l1", "l2")})

        self.assertEqual(leads.mapped("expedition_status"), ["[LIVCFM] test label"] * 2)
        self.assertEqual(leads.mapped("stage_id"), self.stage_final)

    def test_cron_ok2(self):
        lead1, lead2 = self.exec_job_with_status(
            {"l1": _status("LIVCFM"), "l2": _status("RENLNA")}
        )

        self.assertItemsEqual(lead1.expedition_status, "[LIVCFM] test label")
        self.assertItemsEqual(lead2.expedition_status, "[RENLNA] test label")

        self.assertItemsEqual(lead1.stage_id, self.stage_final)
        self.assertItemsEqual(lead2.stage_id, self.stage_track)

    def test_cron_ok_mlvars1(self):
        self.env["crm.lead"]._cron_delivery_auto_track()
        lead1, lead2 = self.exec_job_with_status(
            {"l1": _status("LIVCFM"), "l2": _status("MLVARS")}
        )

        self.assertEqual(lead1.expedition_status, "[LIVCFM] test label")
        self.assertEqual(lead2.expedition_status, "[MLVARS] test label")

        self.assertEqual(lead1.stage_id, self.stage_final)
        self.assertEqual(lead2.stage_id, self.stage_track)

        self.assertFalse(lead1.expedition_urgency_mail_sent)
        self.assertFalse(lead2.expedition_urgency_mail_sent)

        self.assertEqual(
            lead1.mapped("message_ids.subtype_id.name"),
            ["Opportunity Created"],
        )

        self.assertEqual(
            lead2.mapped("message_ids.subtype_id.name"),
            ["Opportunity Created"],
        )

    def test_cron_ok_mlvars2(self):
        lead1, lead2 = self.lead1, self.lead2

        partner_id = self.env.ref("base.res_partner_1").id
        lead2.partner_id = partner_id
        lead2.message_follower_ids |= self.env["mail.followers"].create(
            {"partner_id": partner_id, "res_model": lead2._name, "res_id": lead2.id},
        )
        lead2.send_email_on_delivery = True

        date_old = (date.today() - timedelta(days=9)).isoformat()
        self.exec_job_with_status(
            {"l1": _status("LIVCFM"), "l2": _status("MLVARS", _date=date_old)},
        )

        self.assertEqual(lead1.expedition_status, "[LIVCFM] test label")
        self.assertEqual(lead2.expedition_status, "[MLVARS] test label")

        self.assertEqual(lead1.stage_id, self.stage_final)
        self.assertEqual(lead2.stage_id, self.stage_track)

        self.assertFalse(lead1.expedition_urgency_mail_sent)
        self.assertTrue(lead2.expedition_urgency_mail_sent)

        self.assertEqual(
            lead1.mapped("message_ids.subtype_id.name"),
            ["Opportunity Created"],
        )

        self.assertEqual(
            lead2.mapped("message_ids.subtype_id.name"),
            ["Note", "Discussions", "Opportunity Created"],
        )

        msg1, msg2 = lead2.message_ids[:2]
        subject = "YourCompany - Customer parcel waiting at the postoffice"
        self._check_mail(msg1, subject, "postoffice", ["YourCompany"])
        self._check_mail(msg2, "Product delivered", "code: MLVARS", ["Wood Corner"])
