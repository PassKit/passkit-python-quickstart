import unittest

import event_tickets


class EventTicketMethodsTests(unittest.TestCase):
    def test_guided_event_ticket_methods_are_exported(self):
        expected = {
            "count_tickets",
            "create_event",
            "create_production",
            "create_ticket_type",
            "create_venue",
            "delete_event",
            "delete_production",
            "delete_ticket",
            "delete_ticket_type",
            "delete_venue",
            "get_ticket_by_id",
            "get_ticket_by_number",
            "get_tickets_by_order_number",
            "issue_ticket",
            "list_tickets",
            "redeem_ticket",
            "update_ticket",
            "validate_ticket",
        }
        self.assertTrue(expected.issubset(event_tickets.__all__))
        self.assertTrue(all(callable(getattr(event_tickets, name)) for name in expected))
