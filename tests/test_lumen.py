"""
Unit tests for Lumen CLI Tool
"""
import unittest
import tempfile
import os
import zipfile
from PIL import Image
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lumen import validate_zip, extract_zip, is_tiff_file, convert_tiff_to_png, process_directory

class TestLumen(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def tearDown(self):
        """Tear down test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir)
        
    def test_validate_zip_valid(self):
        """Test validation of a valid ZIP file"""
        # Create a temporary ZIP file
        zip_path = os.path.join(self.test_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("dummy.txt", "content")
            
        self.assertTrue(validate_zip(zip_path))
        
    def test_validate_zip_invalid(self):
        """Test validation of an invalid ZIP file"""
        # Create a file that is not a ZIP
        not_zip_path = os.path.join(self.test_dir, "notzip.txt")
        with open(not_zip_path, 'w') as f:
            f.write("not a zip content")
            
        self.assertFalse(validate_zip(not_zip_path))
        
    def test_validate_zip_nonexistent(self):
        """Test validation of a nonexistent file"""
        nonexistent_path = os.path.join(self.test_dir, "nonexistent.zip")
        self.assertFalse(validate_zip(nonexistent_path))
        
    def test_is_tiff_file(self):
        """Test TIFF file detection"""
        self.assertTrue(is_tiff_file("image.tif"))
        self.assertTrue(is_tiff_file("image.tiff"))
        self.assertTrue(is_tiff_file("image.TIF"))  # Case insensitive
        self.assertTrue(is_tiff_file("image.TIFF"))
        self.assertFalse(is_tiff_file("image.png"))
        self.assertFalse(is_tiff_file("image.jpg"))
        self.assertFalse(is_tiff_file("document.pdf"))
        
    def test_convert_tiff_to_png_8bit(self):
        """Test conversion of 8-bit TIFF to PNG"""
        # Create a simple 8-bit grayscale image
        img = Image.new('L', (10, 10), color=128)
        tiff_path = os.path.join(self.test_dir, "test_8bit.tif")
        img.save(tiff_path, 'TIFF')
        
        png_path = os.path.join(self.output_dir, "test_8bit.png")
        
        # This should not raise an exception
        result = convert_tiff_to_png(tiff_path, png_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(png_path))
        
    def test_process_directory_empty(self):
        """Test processing directory with no TIFF files"""
        # Create a non-TIFF file
        txt_path = os.path.join(self.test_dir, "document.txt")
        with open(txt_path, 'w') as f:
            f.write("not an image")
            
        converted, failed = process_directory(self.test_dir, self.output_dir)
        self.assertEqual(converted, 0)
        self.assertEqual(failed, 0)
        
    def test_process_directory_with_tiff(self):
        """Test processing directory with TIFF files"""
        # Create a simple 8-bit grayscale image
        img = Image.new('L', (10, 10), color=128)
        tiff_path = os.path.join(self.test_dir, "test.tif")
        img.save(tiff_path, 'TIFF')
        
        converted, failed = process_directory(self.test_dir, self.output_dir)
        self.assertEqual(converted, 1)
        self.assertEqual(failed, 0)
        
        # Check that PNG was created
        expected_png = os.path.join(self.output_dir, "test.png")
        self.assertTrue(os.path.exists(expected_png))

if __name__ == '__main__':
    unittest.main()