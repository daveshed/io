import unittest
from unittest import mock

from gpio import error
from gpio import rpi


class GpioOutputTestGroup(unittest.TestCase):

    def setUp(self):
        self.mock_gpio = mock.Mock()
        self.pin_idx = 1
        self.output = rpi.OutputChannel(pin=self.pin_idx, gpio=self.mock_gpio)

    def test_initialising_output_calls_setup_set_low(self):
        self.mock_gpio.setup.assert_called_with(
            self.pin_idx, self.mock_gpio.OUT)
        self.assertEqual(self.output.pin, self.pin_idx)
        self.mock_gpio.output.assert_called_with(self.pin_idx, 0)
        self.assertFalse(self.output.state)

    def test_set_high_calls_ouput(self):
        self.output.set_high()
        self.mock_gpio.output.assert_called_with(self.pin_idx, 1)
        self.assertTrue(self.output.state)

    def test_set_low_calls_output(self):
        self.output.set_low()
        self.mock_gpio.output.assert_called_with(self.pin_idx, 0)
        self.assertFalse(self.output.state)


class FakeEventCaptureMixin:

    class EventConfiguration:

        def __init__(self, channel, edge, callback, bouncetime):
            self._channel = channel
            self._edge = edge
            self._callback = callback
            self._bouncetime = bouncetime

        @property
        def channel(self):
            return self._channel

        @property
        def edge(self):
            return self._edge

        @property
        def callback(self):
            return self._callback

        @property
        def bouncetime(self):
            return self._bouncetime

    def fake_add_event_detect(self, channel, edge, callback, bouncetime):
        self.event_config = \
            self.EventConfiguration(channel, edge, callback, bouncetime)

    def fake_rising_event(self):
        if self.event_config.edge == "RISING":
            self.event_config.callback(self.event_config.channel)

    def fake_falling_event(self):
        if self.event_config.edge == "FALLING":
            self.event_config.callback(self.event_config.channel)

    def create_mock_gpio(self):
        mock_gpio = mock.Mock()
        mock_gpio.add_event_detect.side_effect = self.fake_add_event_detect
        mock_gpio.FALLING = "FALLING"
        mock_gpio.RISING = "RISING"
        return mock_gpio


class GpioInputActiveLowTestGroup(unittest.TestCase, FakeEventCaptureMixin):

    def setUp(self):
        self.mock_gpio = self.create_mock_gpio()
        self.event_config = None
        self.pin_idx = 1
        self.active_low = True
        self.input = rpi.InputChannel(
            pin=self.pin_idx, active_low=self.active_low, gpio=self.mock_gpio)

    def test_initialising_input_calls_setup(self):
        self.mock_gpio.setup.assert_called_with(
            self.pin_idx, self.mock_gpio.IN, self.mock_gpio.PUD_UP)
        self.assertEqual(
            self.event_config.bouncetime, rpi.InputChannel._DEBOUNCE_MS)
        self.assertEqual(
            self.event_config.edge, 'FALLING')

    def test_retreiving_state_reads_gpio_high_signal_returns_false(self):
        self.mock_gpio.input.return_value = 1
        self.assertFalse(self.input.state)
        self.mock_gpio.input.assert_called()

    def test_retreiving_state_reads_gpio_low_signal_returns_true(self):
        self.mock_gpio.input.return_value = 0
        self.assertTrue(self.input.state)
        self.mock_gpio.input.assert_called()

    def test_input_activated_invokes_callbacks(self):
        foo = mock.Mock()
        bar = mock.Mock()
        self.input.register_callback(foo)
        self.input.register_callback(bar)
        # input is active low so a falling edge should invoke callbacks
        self.fake_falling_event()
        foo.assert_called()
        bar.assert_called()


class GpioInputActiveHighTestGroup(unittest.TestCase, FakeEventCaptureMixin):

    def setUp(self):
        self.mock_gpio = self.create_mock_gpio()
        self.pin_idx = 1
        self.active_low = False
        self.input = rpi.InputChannel(
            pin=self.pin_idx, active_low=self.active_low, gpio=self.mock_gpio)

    def test_initialising_input_calls_setup(self):
        self.mock_gpio.setup.assert_called_with(
            self.pin_idx, self.mock_gpio.IN, self.mock_gpio.PUD_DOWN)
        self.assertEqual(
            self.event_config.edge, 'RISING')

    def test_retreiving_state_reads_gpio_high_signal_returns_true(self):
        self.mock_gpio.input.return_value = 1
        self.assertTrue(self.input.state)
        self.mock_gpio.input.assert_called()

    def test_retreiving_state_reads_gpio_low_signal_returns_false(self):
        self.mock_gpio.input.return_value = 0
        self.assertFalse(self.input.state)
        self.mock_gpio.input.assert_called()

    def test_input_activated_invokes_callbacks(self):
        foo = mock.Mock()
        bar = mock.Mock()
        self.input.register_callback(foo)
        self.input.register_callback(bar)
        # input is active high so a rising edge should invoke callbacks
        self.fake_rising_event()
        foo.assert_called()
        bar.assert_called()

    def test_input_activated_does_not_call_deregistered_callbacks(self):
        bar = mock.Mock()
        self.input.register_callback(bar)
        self.input.deregister_callback(bar)
        self.fake_rising_event()
        bar.assert_not_called()

    def test_cannot_deregister_callback_not_registered(self):
        bar = mock.Mock()
        with self.assertRaises(error.GpioError):
            self.input.deregister_callback(bar)

    def test_input_deactivated_does_not_invoke_callbacks(self):
        foo = mock.Mock()
        self.input.register_callback(foo)
        self.fake_falling_event()
        foo.assert_not_called()
