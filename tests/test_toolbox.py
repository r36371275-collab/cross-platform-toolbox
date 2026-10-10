import tempfile
import unittest
from pathlib import Path

from toolbox import disk_report, make_password, organize_folder


class ToolboxTests(unittest.TestCase):
    def test_password_length_and_character_set(self):
        password = make_password(32, use_symbols=False)
        self.assertEqual(len(password), 32)
        self.assertTrue(password.isalnum())

    def test_password_rejects_short_values(self):
        with self.assertRaises(ValueError):
            make_password(7)

    def test_organize_previews_without_moving(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "notes.txt"
            source.write_text("hello", encoding="utf-8")
            plan = organize_folder(folder)
            self.assertEqual(len(plan), 1)
            self.assertTrue(source.exists())
            self.assertEqual(plan[0][1].parent.name, "txt")

    def test_organize_applies_moves(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "photo.png"
            source.write_bytes(b"image")
            plan = organize_folder(folder, apply=True)
            self.assertEqual(len(plan), 1)
            self.assertFalse(source.exists())
            self.assertTrue((folder / "png" / "photo.png").exists())

    def test_disk_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = disk_report(Path(temporary))
            self.assertGreater(report["total_bytes"], 0)
            self.assertEqual(report["total_bytes"], report["used_bytes"] + report["free_bytes"])


if __name__ == "__main__":
    unittest.main()
