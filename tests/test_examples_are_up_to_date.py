import json
import unittest

from src.transform import PretalxSubmission


class TestPretalxSubmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("./data/examples/pretalx/submissions.json") as fd:
            cls.pretalx_submissions = json.load(fd)

        with open("./data/examples/pretalx/speakers.json") as fd:
            cls.pretalx_speakers = json.load(fd)

    def test_sessions_example(self):
        self.assertEqual(self.pretalx_submissions[0]["code"], "A8CD3F")
        pretalx = self.pretalx_submissions[0]

        transformed = PretalxSubmission.parse_obj(pretalx)

        with open("./data/examples/output/sessions.json") as fd:
            sessions = json.load(fd)

        self.assertEqual(transformed.dict(), sessions["A8CD3F"])


if __name__ == "__main__":
    unittest.main()
