"""
Unit tests for the Lumen core conversion API.
"""

import os
import shutil
import sys
import tempfile
import unittest
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lumen_core import (
    LumenError,
    convert_tiff_to_png,
    convert_zip,
    extract_zip,
    is_tiff_file,
    process_directory,
    validate_zip,
)


class TestLumenCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_tiff(self, path, mode="L", size=(10, 10), color=128):
        img = Image.new(mode, size, color=color)
        img.save(path, "TIFF")

    def create_zip_with_files(self, zip_path, files):
        with zipfile.ZipFile(zip_path, "w") as zf:
            for arcname, source_path in files:
                zf.write(source_path, arcname)

    def test_validate_zip_valid(self):
        zip_path = os.path.join(self.test_dir, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("dummy.txt", "content")

        validate_zip(zip_path)

    def test_validate_zip_invalid(self):
        not_zip_path = os.path.join(self.test_dir, "notzip.txt")
        with open(not_zip_path, "w", encoding="utf-8") as file:
            file.write("not a zip content")

        with self.assertRaises(LumenError):
            validate_zip(not_zip_path)

    def test_validate_zip_nonexistent(self):
        nonexistent_path = os.path.join(self.test_dir, "nonexistent.zip")

        with self.assertRaises(LumenError):
            validate_zip(nonexistent_path)

    def test_extract_zip(self):
        zip_path = os.path.join(self.test_dir, "extract.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("nested/file.txt", "content")

        extract_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        extract_zip(zip_path, extract_dir)

        self.assertTrue(os.path.exists(os.path.join(extract_dir, "nested", "file.txt")))

    def test_is_tiff_file(self):
        self.assertTrue(is_tiff_file("image.tif"))
        self.assertTrue(is_tiff_file("image.tiff"))
        self.assertTrue(is_tiff_file("image.TIF"))
        self.assertTrue(is_tiff_file("image.TIFF"))
        self.assertFalse(is_tiff_file("image.png"))
        self.assertFalse(is_tiff_file("image.jpg"))
        self.assertFalse(is_tiff_file("document.pdf"))

    def test_convert_tiff_to_png_8bit(self):
        tiff_path = os.path.join(self.test_dir, "test_8bit.tif")
        self.create_tiff(tiff_path)
        png_path = os.path.join(self.output_dir, "test_8bit.png")

        result = convert_tiff_to_png(tiff_path, png_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(png_path))

    def test_process_directory_empty(self):
        txt_path = os.path.join(self.test_dir, "document.txt")
        with open(txt_path, "w", encoding="utf-8") as file:
            file.write("not an image")

        converted, failed, total = process_directory(self.test_dir, self.output_dir)
        self.assertEqual(converted, 0)
        self.assertEqual(failed, 0)
        self.assertEqual(total, 0)

    def test_process_directory_with_tiff(self):
        tiff_path = os.path.join(self.test_dir, "test.tif")
        self.create_tiff(tiff_path)

        converted, failed, total = process_directory(self.test_dir, self.output_dir)
        self.assertEqual(converted, 1)
        self.assertEqual(failed, 0)
        self.assertEqual(total, 1)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "test.png")))

    def test_convert_zip_success_with_progress_and_logs(self):
        source_dir = os.path.join(self.test_dir, "source")
        nested_dir = os.path.join(source_dir, "nested")
        os.makedirs(nested_dir, exist_ok=True)

        first_tiff = os.path.join(source_dir, "image1.tif")
        second_tiff = os.path.join(nested_dir, "image2.tiff")
        self.create_tiff(first_tiff)
        self.create_tiff(second_tiff)

        zip_path = os.path.join(self.test_dir, "images.zip")
        self.create_zip_with_files(
            zip_path,
            [
                ("image1.tif", first_tiff),
                ("nested/image2.tiff", second_tiff),
            ],
        )

        events = []
        logs = []

        result = convert_zip(
            zip_path,
            output_dir=self.output_dir,
            progress_callback=events.append,
            log_callback=lambda level, message: logs.append((level, message)),
        )

        self.assertEqual(result["converted"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["output_dir"], self.output_dir)
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["current"], 1)
        self.assertEqual(events[0]["total"], 2)
        self.assertTrue(any(level == "success" for level, _ in logs))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "image1.png")))
        self.assertTrue(
            os.path.exists(os.path.join(self.output_dir, "nested", "image2.png"))
        )

    def test_convert_zip_without_tiffs(self):
        zip_path = os.path.join(self.test_dir, "no_tiffs.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("document.txt", "content")

        logs = []
        result = convert_zip(
            zip_path,
            output_dir=self.output_dir,
            log_callback=lambda level, message: logs.append((level, message)),
        )

        self.assertEqual(result["converted"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["total"], 0)
        self.assertTrue(any(level == "warning" for level, _ in logs))

    def test_convert_zip_nonexistent_raises(self):
        with self.assertRaises(LumenError):
            convert_zip(os.path.join(self.test_dir, "missing.zip"), self.output_dir)


if __name__ == "__main__":
    unittest.main()
