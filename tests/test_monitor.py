import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from monitor import KST, ACCOUNTS, amount, rate, demo_data, render, validate, send_slack


class MonitorTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 6, 12, 5, tzinfo=KST)
        self.data = demo_data(ACCOUNTS[0], self.now)

    def test_rate(self):
        self.assertEqual(rate(Decimal('742300'), Decimal('1200000')), '61.9%')
        self.assertEqual(rate(Decimal('1'), Decimal('0')), '산출 불가')

    def test_bad_money(self):
        for value in [None, True, 'NaN', 'Infinity', '-1', 'missing']:
            with self.assertRaises(ValueError):
                amount(value)

    def test_incomplete_and_wrong_basis(self):
        for field, value in [('complete', False), ('vat_basis', 'excluded'),
                             ('budget_period', 'lifetime'), ('date', '2026-10-05')]:
            with self.assertRaises(ValueError):
                validate(dict(self.data, **{field: value}), ACCOUNTS[0], self.now)

    def test_duplicate(self):
        self.data['ad_groups'] *= 2
        with self.assertRaises(ValueError):
            validate(self.data, ACCOUNTS[0], self.now)

    def test_stale(self):
        self.data['as_of'] = (self.now - timedelta(hours=3)).isoformat()
        with self.assertRaises(ValueError):
            validate(self.data, ACCOUNTS[0], self.now)

    def test_partial_failure_no_total(self):
        text, failed = render([(ACCOUNTS[0], self.data), (ACCOUNTS[1], RuntimeError())], self.now)
        self.assertTrue(failed)
        self.assertNotIn('전체 합계 |', text)
        self.assertIn('742,300', text)

    def test_totals(self):
        text, failed = render([(a, demo_data(a, self.now)) for a in ACCOUNTS], self.now)
        self.assertFalse(failed)
        self.assertIn('1,126,500원 / 1,900,000원 | 59.3%', text)

    @patch('monitor.urlopen')
    @patch.dict('os.environ', {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/test/only/fake'})
    def test_slack_payload_without_network(self, opener):
        response = opener.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b'ok'
        send_slack('테스트')
        self.assertEqual(opener.call_args.args[0].method, 'POST')


if __name__ == '__main__':
    unittest.main()
