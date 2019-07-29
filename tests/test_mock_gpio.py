import unittest
from unittest import mock

from gpio import error
from gpio import mock as mockgpio


class MockGpioOutputTestGroup(unittest.TestCase):

    def test_set_init_into_low_state(self):
        self.output = mockgpio.OutputChannel(1, mock.Mock())
        self.assertFalse(self.output.state)
        self.assertEqual(self.output.pin, 1)

    def test_set_high_low_changes_state(self):
        self.output = mockgpio.OutputChannel(1, mock.Mock())
        self.output.set_high()
        self.assertTrue(self.output.state)
        self.output.set_low()
        self.assertFalse(self.output.state)


class MockGpioInputTestGroup(unittest.TestCase):

    def setUp(self):
        self.pin_idx = 1
        self.input = mockgpio.InputChannel(self.pin_idx, True, mock.Mock())

    def test_retreive_pin_after_init(self):
        self.assertEqual(self.input.pin, self.pin_idx)

    def test_set_input_state_externally_updates_state(self):
        self.assertFalse(self.input.state)
        self.input.activate()
        self.assertTrue(self.input.state)

    def test_set_state_externally_invokes_callbacks(self):
        foo = mock.Mock()
        self.input.register_callback(foo)
        self.input.activate()
        foo.assert_called()

    def test_cannot_deregister_unregistered_callback(self):
        with self.assertRaises(error.GpioError):
            def foo(): pass
            self.input.deregister_callback(foo)