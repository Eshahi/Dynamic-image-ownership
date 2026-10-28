"""Pure-logic tests; no client invocation, network, images or models."""
import importlib.util
import pathlib
import unittest
import urllib.parse

spec = importlib.util.spec_from_file_location("identifiers", pathlib.Path(__file__).with_name("tifs_stage_c_identifiers.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class IdentifierTests(unittest.TestCase):
    def row(self):
        return dict(title="File:Example.jpg", pageid=1, sha1="a"*40,
                    url="https://upload.wikimedia.org/a.jpg", descriptionurl="https://commons.wikimedia.org/wiki/File:Example.jpg",
                    mime="image/jpeg", width=512, height=512, size=1000,
                    licence="CC BY-SA 4.0", licence_code="cc-by-sa-4.0",
                    licence_url="https://creativecommons.org/licenses/by-sa/4.0", artist_html="<b>Alice</b>")

    def test_dates(self):
        order = m.date_order()
        self.assertEqual(len(order), 2922)
        self.assertEqual(len(set(order)), 2922)
        self.assertEqual(order, m.date_order())

    def test_wikitext(self):
        self.assertEqual(m.parse_template("{{Potd filename|1=Example.jpg <!--a-->|2=2020}}"), "File:Example.jpg")
        self.assertEqual(m.parse_template(" Example.jpg "), "File:Example.jpg")
        self.assertIsNone(m.parse_template("{{unknown|Example.jpg}}"))
        self.assertIsNone(m.parse_template("{{Potd filename|nested {{unknown}}.jpg}}"))

    def test_url(self):
        self.assertEqual(m.url_key("https://x/A.jpg?utm_source=y&id=1"), "https://x/a.jpg?id=1")
        self.assertNotEqual(m.url_key("https://x/A.jpg?id=1"), m.url_key("https://x/A.jpg?id=2"))

    def test_eligibility(self):
        blank = tuple(set() for _ in range(4))
        row = self.row()
        self.assertEqual(m.rejection(row, blank, blank, set()), [])
        self.assertIn("repeated_new_creator", m.rejection(row, blank, blank, {"alice"}))
        old = ({"wikimedia-commons:page:1"},set(),set(),set())
        self.assertIn("prior_page", m.rejection(row, old, blank, set()))
        old = ({"coco:train2017:1"},set(),set(),set())
        self.assertEqual(m.rejection(row, old, blank, set()), [])
        row["width"] = 511
        self.assertIn("file_constraints", m.rejection(row, blank, blank, set()))

    def test_license(self):
        row = self.row()
        self.assertTrue(m.licence_ok(row))
        row["licence_url"] = "https://evil.example/creativecommons.org/licenses/by-sa/4.0"
        self.assertFalse(m.licence_ok(row))
        row.update(licence="Public domain", licence_code="pd", copyrighted="False", licence_url=None)
        self.assertTrue(m.licence_ok(row))
        row["copyrighted"] = "True"
        self.assertFalse(m.licence_ok(row))

    def test_api_only(self):
        for kind, titles in [("template", ["Template:Potd/2020-01-01"]), ("file", ["File:X.jpg"])]:
            url = urllib.parse.urlsplit(m.request_url(kind, titles))
            self.assertEqual((url.scheme,url.netloc,url.path), ("https","commons.wikimedia.org","/w/api.php"))
            query = urllib.parse.parse_qs(url.query)
            self.assertNotIn("iiurlwidth", query)
            self.assertNotIn("iiurlheight", query)
        for kind, titles in [("file", ["https://upload.wikimedia.org/a.jpg"]), ("file", ["File:a.jpg|File:b.jpg"]), ("file", ["File:x.jpg"]*51), ("thumbnail", ["File:a.jpg"])]:
            with self.assertRaises(ValueError):
                m.request_url(kind, titles)

    def test_redirect_rejected(self):
        with self.assertRaises(ValueError):
            m.NoRedirect().redirect_request(None,None,302,"",{},"https://upload.wikimedia.org/a.jpg")


if __name__ == "__main__":
    unittest.main()
