import unittest
from image_sources.usb_camera import USBCamera


class TestUSBCamera(unittest.TestCase):
    def setUp(self):
        self.camera_ref = USBCamera()

    def tearDown(self):
        pass

    def test_start_and_stop_acquisition(self):
        self.camera_ref.start_acquisition(src=0)
        self.assertTrue(self.camera_ref.is_acquiring)

        self.camera_ref.stop_acquisition()
        self.assertFalse(self.camera_ref.is_acquiring)

    def test_camera_param(self):

        self.camera_ref.start_acquisition(src=0)
        self.assertEqual(self.camera_ref.fps,30)
        self.assertGreater(self.camera_ref.width,0)
        self.assertGreater(self.camera_ref.height, 0)
        self.camera_ref.stop_acquisition()

    def test_invalid_source_id(self):
        result = self.camera_ref.start_acquisition(src=-1)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
