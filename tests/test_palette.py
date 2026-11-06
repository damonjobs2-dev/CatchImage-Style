import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image

spec = importlib.util.spec_from_file_location('palette', Path(__file__).parents[1] / 'scripts/palette.py')
palette = importlib.util.module_from_spec(spec)
spec.loader.exec_module(palette)


class PaletteTests(unittest.TestCase):
    def test_transparent_pixels_do_not_create_a_background(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.png'
            image = Image.new('RGBA', (4, 1))
            image.putdata([(255, 0, 0, 255), (255, 0, 0, 255), (0, 0, 255, 255), (0, 255, 0, 0)])
            image.save(path)
            data = palette.sample(path, 2)
            self.assertEqual(data['sampledPixels'], 3)
            self.assertEqual({c['hex'] for c in data['swatches']}, {'#FF0000', '#0000FF'})
            self.assertAlmostEqual(data['swatches'][0]['share'], 2 / 3, places=5)

    def test_exif_orientation_is_applied(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'oriented.jpg'
            image = Image.new('RGB', (8, 4), 'red')
            exif = Image.Exif()
            exif[274] = 6
            image.save(path, exif=exif)
            data = palette.sample(path, 2)
            self.assertEqual((data['width'], data['height']), (4, 8))

    def test_fully_transparent_image_returns_no_palette(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'empty.png'
            Image.new('RGBA', (2, 2), (255, 255, 255, 0)).save(path)
            self.assertEqual(palette.sample(path)['swatches'], [])


if __name__ == '__main__':
    unittest.main()
