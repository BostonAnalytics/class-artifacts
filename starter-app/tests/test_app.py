"""Run from starter-app/:  python -m unittest discover tests"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

import app as appmod  # noqa: E402


class StarterAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = appmod.app
        cls.app.config["TESTING"] = True
        with cls.app.app_context():
            with open(os.path.join(os.path.dirname(HERE), "roster_sample.csv"), encoding="utf-8") as fh:
                appmod.load_roster(fh.read())

    def login(self, client, user, pw):
        return client.post("/login", data={"username": user, "password": pw}, follow_redirects=True)

    def test_login_required(self):
        c = self.app.test_client()
        self.assertEqual(c.get("/").status_code, 302)

    def test_bad_password(self):
        c = self.app.test_client()
        r = self.login(c, "thomas", "wrong")
        self.assertIn(b"do not match", r.data)

    def test_student_builds_artifact(self):
        c = self.app.test_client()
        self.login(c, "thomas", "apple")
        r = c.get("/a/m2")
        self.assertIn(b"Your input", r.data)                  # m2 has variants
        r = c.post("/a/m2", data={"decision": "Do it now", "reasons": ["Cost", "Risk", "Not an option"],
                                  "evidence": "Sales grew 12% last quarter."}, follow_redirects=True)
        self.assertIn(b"Artifact for Discussion 2", r.data)
        self.assertIn(b"Cost, Risk", r.data)
        self.assertNotIn(b"Not an option", r.data)             # unknown options are dropped
        txt = c.get("/a/m2/artifact.txt")
        self.assertEqual(txt.status_code, 200)
        self.assertIn(b"Sales grew 12%", txt.data)

    def test_variant_is_stable(self):
        act = appmod.BY_SLUG["m2"]
        self.assertEqual(appmod.variant_for("ann", act), appmod.variant_for("ann", act))
        self.assertIsNone(appmod.variant_for("ann", appmod.BY_SLUG["m1"]))

    def test_students_see_only_their_own(self):
        a, b = self.app.test_client(), self.app.test_client()
        self.login(a, "maria", "plum")
        a.post("/a/m1", data={"my_answer": "Maria private answer", "partner_difference": "", "final_answer": "x"})
        self.login(b, "josh", "fig")
        self.assertNotIn(b"Maria private answer", b.get("/a/m1").data)
        self.assertEqual(b.get("/admin/").status_code, 403)

    def test_instructor_view_and_export(self):
        s = self.app.test_client()
        self.login(s, "tara", "lime")
        s.post("/a/m3", data={"question": "Q", "inputs": "a", "outputs": "b", "tool": "This needs code",
                              "why": ["Too many rows"]})
        t = self.app.test_client()
        self.login(t, "instructor", "change-me")
        r = t.get("/admin/m3/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"This needs code", r.data)
        csv_ = t.get("/admin/m3/export.csv")
        self.assertIn(b"tara", csv_.data)

    def test_close_blocks_submissions(self):
        t = self.app.test_client()
        self.login(t, "instructor", "change-me")
        t.post("/admin/m1/toggle")
        s = self.app.test_client()
        self.login(s, "adriana", "kiwi")
        r = s.post("/a/m1", data={"my_answer": "late"}, follow_redirects=True)
        self.assertIn(b"closed", r.data)
        t.post("/admin/m1/toggle")                             # reopen for other tests


if __name__ == "__main__":
    unittest.main()
