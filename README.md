# Embedded Programming 2 — starter project

Everything you need to start each lab. **Fork** it once, clone your fork, and
each session swap the active sketch and (later) drop in your trained model.

This fork is your **individual** work all semester. From session 3 your team
also makes its own separate repository — that is where the project lives.

**Board:** ESP32-S3-DevKitC-1 · **Framework:** Arduino · **Tool:** PlatformIO (in VS Code)

---

## Quick start

1. Install **VS Code** + the **PlatformIO IDE** extension. Wait for it to finish
   downloading its toolchain, then restart.
2. **File → Open Folder →** this project.
3. Bottom blue bar: **✓ Build**, **→ Upload**, **🔌 Serial Monitor**.
   Or in the PlatformIO terminal: `pio run -t upload && pio device monitor`

The board that ships in this repo is **Session 1's blink + hello**. Flash it
first to prove your whole toolchain works.

> **The LED:** this board has no simple on/off LED — it has one addressable RGB
> LED on **GPIO38** (check the silkscreen: ours reads `RGB@IO38`). The blink
> uses it, but the real proof is the **serial "hello"**, which always works.

> **GPIO2 is a test signal, not a mistake.** `setup()` starts a 1 kHz square
> wave on GPIO2 and leaves it running. It's there for the oscilloscope block in
> session 1 — probe it and you'll find a wave in seconds. The LED pin carries
> pulses for only ~30 µs at a time, which is a much harder first capture.

---

## How the project is organised

| Path | What |
|---|---|
| `src/main.cpp` | The **active** sketch that gets built + flashed. |
| `examples/` | Per-session reference sketches — **copy one into `src/main.cpp`** to use it. |
| `include/` | Headers (e.g. `test_images.h` for session 6). |
| `lib/` | Libraries — **drop your Edge Impulse model here** (session 4). |
| `tools/` | Helper scripts (record/plot CSV, image → C array). |
| `platformio.ini` | The build recipe (board, libraries, flags). **Don't prune it** — see Notes. |
| `report-template.md` | The final project report skeleton — copy it into your team repo (session 10). |

PlatformIO only builds `src/` + `lib/`, so the files in `examples/` sit safely
out of the build until you copy one in.

---

## Get a new example from the course starter

1. In VS Code, **save all files, commit your changes, and push** to your fork.
2. On GitHub, open **your fork** on `main`: **Sync fork → Update branch**.
3. Back in VS Code, open **Source Control → … → Pull** (on `main`).
4. Check that `examples/session02_address_probe.cpp`, `tools/record_csv.py` and `tools/plot_csv.py` have appeared.

**Sync fork updates GitHub; Pull updates your laptop.** If either step reports
conflicts, ask the teacher; keep your own work. The probe is also available in
Moodle as a backup, so you can continue the lab while resolving a sync problem.

---

## Session by session

- **Session 1 — first flash:** flash `src/main.cpp` as-is (blink + hello).
  - Homework on real hardware? Copy `examples/session01_plain_led.cpp` → `src/main.cpp` and wire a plain LED on **GPIO40** (long leg → 220–330 Ω resistor → GPIO40, short leg → GND). Session 2 reuses the same pin.
- **Session 2 — sensor + data:**
  - Wire the MPU-6050: **3V3 → VCC, GND → GND, GPIO8 → SDA, GPIO9 → SCL** *(power off while wiring)*.
  - Copy `examples/session02_i2c_scanner.cpp` → `src/main.cpp`, flash → find `0x68`.
  - Copy `examples/session02_mpu_read.cpp` → `src/main.cpp` → read motion, sanity-check gravity on Z.
  - Debug: copy `examples/session02_address_probe.cpp` → `src/main.cpp`. Change `REQUEST_ADDRESS` **0x68 → 0x69 → 0x68**, uploading each time; compare **ACK → NACK → ACK** with the wires connected. Restore the motion sketch afterwards.
  - Analog first: copy `examples/session02_pot_read.cpp` → `src/main.cpp` → turn the knob, watch the number sweep.
  - Record CSVs: `python tools/record_csv.py wave_01.csv` (see setup below).
    Wait for **GO**, perform one activity until **STOP**; it saves ten seconds automatically.
    **Commit and push the CSVs** — you need them in session 3.
  - Plot and compare your recordings with `tools/plot_csv.py` (instructions below).
  - **Homework — tilt switches, knob dims:** combine `examples/session02_knob_dims_led.cpp` with `examples/session02_mpu_read.cpp` in one `src/main.cpp` (one setup/loop). Choose an axis and an acceleration threshold: pointing up enables the LED, held sideways/down switches it off. While enabled, the pot sets brightness; while disabled it stays off. `raw / 16` is fine.
    Test the three stationary poses and two knob settings. Add three comments: axis/threshold, observed readings, one testing surprise. Commit and push `FINAL: tilt switches, knob dims`; submit its link and your AI-use line in Moodle. Flicker reduction is optional; no perceptual brightness curve is required.
- **Session 3 — train:** upload your CSVs to Edge Impulse and train. *(We install the Edge Impulse CLI together in the lab if we need the live data forwarder — don't fight with it at home.)*
- **Session 4 — deploy:** export your model as an **Arduino library**, unzip into `lib/`, then work from `examples/session04_deploy.cpp` (edit the `#include` to your project's header).
- **Session 5 — security:** copy `examples/session05_plant_secret.cpp` → `src/main.cpp`, flash, then dump the flash and find your secret (see that file's header).
- **Session 6 — vision:** clone the Edge Impulse project linked in Moodle, train it, deploy it, and feed it a baked-in test image from `include/test_images.h`. Then push the resolution until the board gives up and record where — `ceiling.md`, `FINAL: my ceiling`.
- **Session 7 — platform:** your team's platform sentence goes in your **team** repo's `README`.
- **Sessions 8–10 — project:** the project lives in your **team** repo, not this fork. Copy `report-template.md` across when you write the report (2 pages max).

---

## Record your session-2 CSV files

First **Sync fork → Update branch**, then **Pull** in VS Code to get
`tools/record_csv.py`. Upload `examples/session02_mpu_read.cpp` as `src/main.cpp`,
connect through the board's **UART** USB socket, and **close Serial Monitor**.

In VS Code, open **PlatformIO (ant icon) → Quick Access → Miscellaneous →
PlatformIO Core CLI**. From your project folder:

```bash
python tools/record_csv.py wave_01.csv
```

Wait for the countdown and **GO**, then wave continuously until **STOP**.
The script records **10 seconds at 115200 baud** and saves three columns
(x,y,z in m/s²) as UTF-8, without a header. Repeat with `shake_01.csv` and
`idle_01.csv`; choose a new number for each additional take. **Do not add `>`**:
this script writes the file itself. `pio device monitor` is an interactive
viewer; redirecting it is not the recording workflow.

**Python/`pio` not found, or “pyserial is missing”?** PlatformIO IDE includes
its own Python and pyserial. A regular terminal may use another Python or
lack `pio` on PATH. Use the Core CLI above, or these default-install paths
from your project folder; no second installation is needed:

Windows **PowerShell**:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\python.exe" tools/record_csv.py wave_01.csv
```

**Mac/Linux**:

```bash
~/.platformio/penv/bin/python tools/record_csv.py wave_01.csv
```

If the PlatformIO menu is missing, enable/install the **PlatformIO IDE**
extension and let its setup finish. Custom installations may use another path.

- **Port selection:** one detected USB serial port is selected automatically.
  Otherwise run `python tools/record_csv.py --list-ports`, then specify it:
  `python tools/record_csv.py wave_01.csv --port COM3` (example Windows port).
  On Mac use the listed `/dev/cu.…` path. Use the same Python prefix as above
  if needed. Listing ports does not open them.
- **Port busy / no readings:** close other monitors; check the UART cable,
  uploaded sketch and port. On Windows, a missing COM port may need the
  [CP210x driver](https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers).
- **Existing filename:** the script refuses to overwrite it, even if it is
  empty from an earlier failed command. Use another take number.
- **Bad/interrupted take:** startup text is ignored before GO. During the take,
  malformed data or a one-second silence is an error; Ctrl+C also cancels.
  The newly created incomplete file is removed, and you can retry. Previously
  saved files are never removed. Wait for **“STOP. Saved … rows”** for success.
- **Inspect and plot:** expect a few hundred rows. The script does not resample
  or add timestamps; ten seconds of capture does not guarantee exactly 500 rows
  or prove regular timing. `--seconds 20` changes the duration if needed.

---

## Plot your session-2 CSV files

In the **PlatformIO Core CLI** opened above, from your project folder, run:

```bash
python tools/plot_csv.py wave_01.csv shake_01.csv idle_01.csv
```

Open **`plots/motion.html` in your web browser**. Python 3.8+ is enough; there
are no extra packages to install and the report works offline. Use the same
Core CLI terminal for Python. If `python` is still not found, use the bundled
interpreter (default installation paths):

- Windows PowerShell: `& "$env:USERPROFILE\.platformio\penv\Scripts\python.exe" tools/plot_csv.py wave_01.csv`
- Mac/Linux: `~/.platformio/penv/bin/python tools/plot_csv.py wave_01.csv`

Add the other CSV filenames to compare multiple recordings. Pair up if the
installation itself is broken instead of spending the investigation repairing it.

The report shows **X, Y, Z and acceleration magnitude** on a common vertical
scale. Click a filename to hide/show its traces. The table reports each
signal’s **range (maximum minus minimum)** across the whole file, in m/s².
Magnitude includes gravity: it is about 9.8 m/s² at rest, not zero.

- Use **one or several file paths**; quoted patterns such as `"wave_*.csv"` work
  too. Example: `python tools/plot_csv.py wave_01.csv wave_rotated_01.csv`.
- The horizontal axis counts readings. Add **`--rate 50`** for estimated seconds
  at an assumed 50 Hz. The CSV has no timestamps; this cannot verify the actual
  rate. Separate recordings start at their own first reading, not a shared time.
- Files must contain **three finite numbers per row, no header**. UTF-8 and
  BOM-marked Windows UTF-16 are accepted. An invalid row gives its filename and
  line number; fix the CSV and rerun. The script never silently discards rows or
  edits the recordings. Save cleaned CSVs as UTF-8 for next session.
- Rerunning replaces the generated report. **Keep and commit your CSVs**;
  `plots/` is ignored because reports can be regenerated.

**Choose one investigation after saving your core files:**

1. **See the activity:** predict differences between wave/shake/idle. Find a
   visible clue in the plots, then show where it becomes ambiguous.
2. **Rotate the grip:** repeat the same wave with the board rotated in your hand.
   Save a new file and compare axes versus magnitude. Keep the changed grip noted.
3. **Test a rule:** choose a Z-range threshold for idle versus wave from your
   original files. Test it, unchanged, on a fresh slower wave and idle recording
   of similar duration. Explain a wrong decision or propose a harder test.

These are optional investigations, not extra graded submissions. A rule that
separates two whole files is not yet a live motion detector. Keep fresh takes
separate for testing next session.

---

## Wiring: MPU-6050 (GY-521)

| MPU-6050 | ESP32-S3 |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 8 |
| SCL | GPIO 9 |

*(If your board's I²C defaults differ, change the pins in the session-2 sketches.)*

---

## Notes

- **Don't "simplify" `platformio.ini`.** The octal-flash lines
  (`board_build.flash_mode = opi`, `board_build.arduino.memory_type = opi_opi`)
  and `-D BOARD_HAS_PSRAM` are **required** on our boards, not optional extras.
  Take them out and the board doesn't just lose PSRAM — it panics in a boot loop
  before your code runs:
  `assert failed: do_core_init startup.c:328 (flash_ret == ESP_OK)`.
  This has already caught us once. The file is commented; read it, don't prune it.
- **Can't upload / can't dump flash?** Hold **BOOT**, tap **RESET**, release,
  then retry — that forces download mode.
