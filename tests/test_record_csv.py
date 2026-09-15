"""Synthetic serial checks: never open the teacher's physical board."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'record_csv.py'
spec = importlib.util.spec_from_file_location('record_csv', SCRIPT)
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


class FakePort:
    def __init__(self, rows):
        self.rows = iter(rows)

    def read_until(self, *args):
        time.sleep(0.002)
        return next(self.rows, b'1.00,2.00,9.80\r\n')


class RecorderTests(unittest.TestCase):
    def test_numeric_validation(self):
        self.assertEqual(rec.csv_row(b' 1.00, -2,9.8\r\n'), '1.00,-2,9.8\n')
        for raw in [b'booting\n', b'1,2\n', b'1,2,3,4\n', b'NaN,0,1\n', b'1,inf,2\n', b'\xff,1,2\n']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                rec.csv_row(raw)

    def test_split_rows_survive_timeouts(self):
        lines = rec.Lines(FakePort([b'1.', b'', b'0,2.0,9.8\n']))
        self.assertIsNone(lines.read())
        self.assertIsNone(lines.read())
        self.assertEqual(lines.read(), b'1.0,2.0,9.8\n')
        with self.assertRaises(ValueError):
            rec.Lines(FakePort([b'x' * 1025])).read()

    def test_safe_port_selection(self):
        a = SimpleNamespace(device='COM3', vid=123)
        b = SimpleNamespace(device='COM4', vid=456)
        other = SimpleNamespace(device='Bluetooth', vid=None)
        self.assertEqual(rec.choose_port([a, other], None), 'COM3')
        self.assertEqual(rec.choose_port([a, b], 'COM4'), 'COM4')
        for ports in [[], [other], [a, b]]:
            with self.assertRaises(ValueError):
                rec.choose_port(ports, None)

    def test_startup_excluded_and_previous_take_preserved(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            out = Path(tmp) / 'wave.csv'
            count = rec.capture(FakePort([b'ESP-ROM boot\n', b'0,0,9.8\n']), out, .03, countdown=0)
            data = out.read_bytes()
            self.assertGreater(count, 2)
            self.assertEqual(data, b'1.00,2.00,9.80\n' * count)
            with self.assertRaises(ValueError):
                rec.capture(FakePort([]), out, .03, countdown=0)
            self.assertEqual(out.read_bytes(), data)

    def test_bad_take_not_silently_shortened(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            out = Path(tmp) / 'bad.csv'
            with self.assertRaises(ValueError):
                rec.capture(FakePort([b'0,0,9.8\n', b'1,2,3\n', b'boot reset\n']), out, .03, countdown=0)
            self.assertFalse(out.exists())
            with self.assertRaises(ValueError):
                rec.capture(FakePort([b'not the sketch\n'] * 100), out, .03, countdown=0, startup_timeout=.01)
            self.assertFalse(out.exists())

    def test_interrupted_take_removed(self):
        class Interrupted(FakePort):
            def read_until(self, *args):
                value = super().read_until(*args)
                if value == b'interrupt':
                    raise KeyboardInterrupt
                return value
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            out = Path(tmp) / 'cancelled.csv'
            with self.assertRaises(KeyboardInterrupt):
                rec.capture(Interrupted([b'1,2,3\n', b'interrupt']), out, .03, countdown=0)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
