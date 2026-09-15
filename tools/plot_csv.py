#!/usr/bin/env python3
"""Plot EP2 x,y,z CSV recordings in an offline HTML report (Python 3.8+ only).

    python tools/plot_csv.py wave_01.csv shake_01.csv idle_01.csv
    python tools/plot_csv.py "wave_*.csv" --rate 50

Open plots/motion.html in your browser. No extra packages, network or account.
Rows must contain exactly three finite numbers in m/s^2, with no header.
Without timestamps, --rate gives an ASSUMED time axis, not measured timing.
The original CSV files are never changed. Run --help for options.
"""
import argparse
import csv
import glob
import html
import io
import math
from pathlib import Path

COLORS = ("#b52463", "#176fa6", "#16815b", "#9b5b00", "#7547ad", "#333333")


def read_csv(path):
    raw = path.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    try:
        text = raw.decode(encoding)
    except UnicodeError as exc:
        raise ValueError("{}: save the file as UTF-8, then retry".format(path.name)) from exc
    rows = []
    for number, fields in enumerate(csv.reader(io.StringIO(text)), 1):
        try:
            if len(fields) != 3:
                raise ValueError()
            values = tuple(float(field) for field in fields)
            if not all(math.isfinite(value) for value in values):
                raise ValueError()
            # Also ensure the magnitude and plotted ranges can be represented.
            if not math.isfinite(math.hypot(*values)):
                raise ValueError()
        except ValueError as exc:
            raise ValueError("{}: line {} must contain exactly three finite numbers (x,y,z). "
                             "Remove headers, boot messages, blank or incomplete rows; "
                             "no rows were silently discarded.".format(path.name, number)) from exc
        rows.append(values)
    if len(rows) < 2:
        raise ValueError("{}: need at least two readings to draw a trace".format(path.name))
    return rows


def make_report(recordings, rate):
    # Every panel and file uses the same vertical scale. Magnitude includes gravity.
    series = []
    for path, rows in recordings:
        channels = [[row[i] for row in rows] for i in range(3)]
        channels.append([math.hypot(*row) for row in rows])
        series.append((path.name, channels))
    low = min(0, min(min(channel) for _, channels in series for channel in channels))
    high = max(0, max(max(channel) for _, channels in series for channel in channels))
    span = high - low
    if not math.isfinite(span):
        raise ValueError("Values are too large to plot; check the CSV units and numbers")
    padding = max(span * .08, .1)
    low, high = low - padding, high + padding
    if not math.isfinite(high - low):
        raise ValueError("Values are too large to plot; check the CSV units and numbers")
    longest = max(len(rows) for _, rows in recordings) - 1
    x_end = longest / rate if rate else longest
    if not math.isfinite(x_end):
        raise ValueError("Rate is too small to produce a finite time axis")
    x_label = "Estimated time (s), assuming {:g} Hz".format(rate) if rate else "Reading index (first reading = 0)"
    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EP2 motion recordings</title><style>
body{font:17px system-ui,sans-serif;color:#202020;background:#fafafa;max-width:1100px;margin:30px auto;padding:0 20px}
h1{margin-bottom:8px}h2{margin:25px 0 8px;font-size:21px}p{line-height:1.5}svg{display:block;width:100%;background:white;border:1px solid #ddd;border-radius:8px}
label{display:inline-block;margin:0 20px 10px 0;cursor:pointer}input{margin-right:8px}table{width:100%;border-collapse:collapse;background:white;font-variant-numeric:tabular-nums}th,td{text-align:left;padding:9px;border-bottom:1px solid #ddd}th{background:#eee}.small{color:#555;font-size:14px}.table-scroll{overflow:auto}
</style><h1>Compare your motion recordings</h1>
<p>X, Y and Z show acceleration along the board’s axes. <strong>Magnitude</strong> combines them: √(x² + y² + z²). It includes gravity and is about 9.8 m/s² at rest.</p>''']
    timing = ("The time axis assumes {:g} readings/s. These files have no timestamps: "
              "this does not measure the actual recording rate or timing regularity.".format(rate)
              if rate else "The horizontal axis counts readings. Add --rate 50 for an estimated time axis; the files do not contain timestamps.")
    parts.append('<p class="small">{} All panels share one vertical scale. Traces start at their own first reading; separate takes are not synchronised. No smoothing or resampling.</p>'.format(html.escape(timing)))
    parts.append('<div aria-label="Visible recordings">')
    for i, (name, _) in enumerate(series):
        color = COLORS[i % len(COLORS)]
        parts.append('<label style="color:{}"><input type="checkbox" checked data-series="{}">{}</label>'.format(color, i, html.escape(name)))
    parts.append('</div>')
    left, top, width, height = 76, 20, 954, 150
    for channel_index, title in enumerate(("X acceleration", "Y acceleration", "Z acceleration", "Magnitude (includes gravity)")):
        parts.append('<h2>{} · m/s²</h2><svg viewBox="0 0 1060 230" role="img" aria-label="{}"><g font-family="Arial" font-size="13" fill="#444">'.format(title, title))
        for tick in range(5):
            y = top + height * tick / 4
            value = high - (high - low) * tick / 4
            parts.append('<path d="M{},{} H{}" stroke="#e1e1e1"/><text x="{}" y="{}" text-anchor="end">{:.3g}</text>'.format(left, y, left+width, left-10, y+4, value))
        for tick in range(6):
            x = left + width * tick / 5
            parts.append('<path d="M{},{} V{}" stroke="#eee"/><text x="{}" y="194" text-anchor="middle">{:.3g}</text>'.format(x, top, top+height, x, x_end*tick/5))
        for i, (name, channels) in enumerate(series):
            commands = []
            for j, value in enumerate(channels[channel_index]):
                x = left + width*j/longest
                y = top + height*(high-value)/(high-low)
                commands.append('{}{:.2f},{:.2f}'.format('M' if j == 0 else 'L', x, y))
            parts.append('<path data-trace="{}" d="{}" fill="none" stroke="{}" stroke-width="1.7"><title>{}</title></path>'.format(i, ' '.join(commands), COLORS[i % len(COLORS)], html.escape(name)))
        parts.append('<text x="553" y="220" text-anchor="middle">{}</text></g></svg>'.format(html.escape(x_label)))
    parts.append('''<h2>Compare a number: range = maximum − minimum</h2>
<p class="small">Ranges use the whole recording and can be dominated by one spike. Compare takes of similar length. These are observations, not model accuracy scores.</p>
<div class="table-scroll"><table><thead><tr><th>Recording</th><th>Rows</th><th>X range</th><th>Y range</th><th>Z range</th><th>Magnitude range</th></tr></thead><tbody>''')
    for name, channels in series:
        cells = ''.join('<td>{:.3f}</td>'.format(max(c)-min(c)) for c in channels)
        parts.append('<tr><td>{}</td><td>{}</td>{}</tr>'.format(html.escape(name), len(channels[0]), cells))
    parts.append('''</tbody></table></div><p class="small">All ranges in m/s². Input files are unchanged. This report works offline; you can regenerate it after recording more takes.</p>
<script>document.querySelectorAll('[data-series]').forEach(input=>input.addEventListener('change',()=>{document.querySelectorAll('[data-trace="'+input.dataset.series+'"]').forEach(trace=>trace.style.display=input.checked?'':'none');}));</script></html>''')
    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='+', help='CSV paths or quoted patterns such as "wave_*.csv"')
    parser.add_argument('--rate', type=float, help='assumed readings/s for an estimated time axis; default: reading index')
    parser.add_argument('-o', '--output', type=Path, default=Path('plots/motion.html'), help='HTML report to write (default: plots/motion.html); replaces an earlier report')
    args = parser.parse_args()
    if args.rate is not None and (not math.isfinite(args.rate) or args.rate <= 0):
        parser.error('--rate must be a finite positive number')
    if args.output.suffix.lower() != '.html':
        parser.error('--output must end in .html (the original CSVs are never overwritten)')
    paths = []
    seen = set()
    for pattern in args.files:
        matches = [pattern] if Path(pattern).is_file() else sorted(glob.glob(pattern))
        if not matches:
            parser.error('no files match {!r}; run from your project folder or give the full path'.format(pattern))
        for match in matches:
            path = Path(match)
            resolved = path.resolve()
            if resolved not in seen:
                paths.append(path)
                seen.add(resolved)
    if args.output.resolve() in seen:
        parser.error('the output must not be one of your input files')
    try:
        recordings = [(path, read_csv(path)) for path in paths]
        report = make_report(recordings, args.rate)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding='utf-8')
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(1, 'Could not plot: {}\n'.format(exc))
    print('Wrote {}. Open this file in your browser.'.format(args.output.resolve()))
    print('Compared {} recording(s); input CSV files were not changed.'.format(len(recordings)))


if __name__ == '__main__':
    main()
