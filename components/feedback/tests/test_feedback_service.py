import os
import unittest
from unittest import mock

from pony.orm import ObjectNotFound, Database


class TestFeedbackService(unittest.TestCase):

    db: Database
    user1_id: int

    @mock.patch.dict(os.environ, {'DFM_ENV': 'Test'})
    def setUp(self):
        from components.feedback.models import db
        from components.feedback.feedback_service import FeedbackService
        self.user1_id = 1
        self.service = FeedbackService()
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.db = db

    def tearDown(self):
        pass

    def test_add_valid_text(self):
        self.service.add(self.user1_id, "Test")
        feedback_list = self.service.get_all()
        self.assertEqual(1, len(feedback_list))

    def test_add_no_text(self):
        with self.assertRaises(ValueError):
            self.service.add(self.user1_id, None)

    def test_get_valid_id(self):
        text = "Test"
        self.service.add(self.user1_id, text)
        feedback_id = self.service.get_all()[0].id
        feedback = self.service.get(feedback_id)
        self.assertEqual(text, feedback.text)
        self.assertEqual(self.user1_id, feedback.user_id)

    def test_get_invalid_id(self):
        feedback = self.service.get(0)
        self.assertEqual(None, feedback)

    def test_set_resolved_valid_id(self):
        self.service.add(self.user1_id, "Test1")
        self.service.add(self.user1_id, "Test2")
        feedback1_id = self.service.get_all()[0].id
        feedback2_id = self.service.get_all()[1].id
        self.service.set_resolved(feedback1_id)
        feedback1 = self.service.get(feedback1_id)
        self.assertIsNotNone(feedback1.done)
        feedback2 = self.service.get(feedback2_id)
        self.assertIsNone(feedback2.done)

    def test_set_resolved_invalid_id(self):
        with self.assertRaises(ObjectNotFound):
            self.service.set_resolved(0)

    def test_get_all_feedback_exists(self):
        self.service.add(self.user1_id, "Test")
        feedback_list = self.service.get_all()
        self.assertEqual(1, len(feedback_list))

    def test_get_all_no_feedback(self):
        feedback_list = self.service.get_all()
        self.assertEqual(0, len(feedback_list))

    def test_get_stats_feedback_exists(self):
        self.service.add(self.user1_id, "Test")
        stats = self.service.get_stats()
        expected = {'count': 1}
        self.assertEqual(expected, stats)

    def test_get_stats_no_feedback(self):
        stats = self.service.get_stats()
        expected = {'count': 0}
        self.assertEqual(expected, stats)


if __name__ == '__main__':
    unittest.main()
