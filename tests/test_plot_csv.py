"""Run from the repository root: python -m unittest discover -s tests"""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'plot_csv.py'
spec = importlib.util.spec_from_file_location('plot_csv', SCRIPT)
plot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plot)


class PlotCsvTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_windows_and_utf8_encodings(self):
        for encoding in ('utf-8', 'utf-8-sig', 'utf-16'):
            path = self.root / (encoding + '.csv')
            path.write_bytes('0,0,9.8\r\n1,-2,9.7\r\n'.encode(encoding))
            self.assertEqual(plot.read_csv(path), [(0., 0., 9.8), (1., -2., 9.7)])

    def test_bad_rows_are_rejected_with_line_number(self):
        for bad in ('booting...', '1,2', '1,2,3,4', 'NaN,0,0', 'inf,0,0', ''):
            path = self.root / 'bad.csv'
            path.write_text('1,2,3\n' + bad + '\n1,2,3\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'line 2'):
                plot.read_csv(path)

    def test_empty_or_single_reading_is_rejected(self):
        for data in ('', '1,2,3\n'):
            path = self.root / 'short.csv'
            path.write_text(data)
            with self.assertRaisesRegex(ValueError, 'at least two'):
                plot.read_csv(path)

    def test_report_calculates_magnitude_ranges_and_escapes_names(self):
        report = plot.make_report([(Path('<sensor>.csv'), [(0,0,0), (3,4,0)])], 50)
        self.assertIn('&lt;sensor&gt;.csv', report)
        self.assertNotIn('<sensor>.csv', report)
        self.assertIn('<td>3.000</td><td>4.000</td><td>0.000</td><td>5.000</td>', report)
        self.assertIn('assuming 50 Hz', report)
        self.assertIn('does not measure the actual recording rate', report)
        self.assertEqual(report.count('<svg '), 4)

    def test_cli_glob_preserves_inputs_and_writes_offline_report(self):
        paths = [self.root / name for name in ('wave_01.csv', 'wave_02.csv')]
        for path in paths:
            path.write_bytes(b'0,0,9.8\n1,2,9.7\n')
        before = [p.read_bytes() for p in paths]
        result = subprocess.run([sys.executable, str(SCRIPT), 'wave_*.csv'], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = (self.root / 'plots/motion.html').read_text()
        self.assertIn('Reading index', report)
        self.assertIn('wave_02.csv', report)
        self.assertNotIn('src="http', report)
        self.assertEqual(before, [p.read_bytes() for p in paths])

    def test_cli_rejects_invalid_rates_and_output_csv(self):
        path = self.root / 'input.csv'
        path.write_text('1,2,3\n4,5,6\n')
        original = path.read_bytes()
        for flags in (['--rate', '0'], ['--rate', 'nan'], ['--rate', '-5'], ['-o', str(path)]):
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)] + flags, cwd=self.root, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
