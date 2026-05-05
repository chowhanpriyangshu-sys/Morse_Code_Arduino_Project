# 📡 Optical Morse Code Communication System

> Transmit text wirelessly via a blinking LED and decode it in real time using a webcam and Python.

---

## 🗂️ Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Hardware Requirements](#hardware-requirements)
- [Wiring Diagram](#wiring-diagram)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Timing Protocol](#timing-protocol)
- [Morse Code Reference](#morse-code-reference)
- [Configuration & Tuning](#configuration--tuning)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

This project implements a **complete end-to-end optical Morse code communication system** across two devices:

1. **Transmitter** — An Arduino Uno paired with an HC-05 Bluetooth module receives ASCII text from a smartphone, converts it to Morse code, and blinks an LED accordingly.
2. **Receiver** — A Python script captures the LED via a webcam, processes each frame with OpenCV, measures blink durations, and decodes the Morse back into readable ASCII text in real time.

The system is self-contained, requires no network infrastructure, and works across line-of-sight distances limited only by camera resolution and LED brightness.

---

## System Architecture

```
┌──────────────────┐     Bluetooth (UART)     ┌───────────────────────────┐
│  Smartphone      │ ────────────────────────▶ │  Arduino Uno + HC-05      │
│  (BT Terminal)   │                           │  ● Receives ASCII string  │
└──────────────────┘                           │  ● Converts → Morse code  │
                                               │  ● Blinks LED on Pin 13   │
                                               └────────────┬──────────────┘
                                                            │  Optical (LED blink)
                                                            ▼
                                               ┌───────────────────────────┐
                                               │  Webcam + Python/OpenCV   │
                                               │  ● Captures LED flashes   │
                                               │  ● Thresholds brightness  │
                                               │  ● Measures ON/OFF timing │
                                               │  ● Decodes Morse → ASCII  │
                                               │  ● Displays result live   │
                                               └───────────────────────────┘
```

---

## Project Structure

```
optical-morse/
│
├── morse_transmitter.ino     # Arduino firmware (upload to Uno)
├── morse_receiver.py         # Python decoder (run on PC/laptop)
├── calibration_guide.md      # Detailed calibration instructions
└── README.md                 # This file
```

---

## Hardware Requirements

| Component | Quantity | Notes |
|---|---|---|
| Arduino Uno (or compatible) | 1 | Any ATmega328P board works |
| HC-05 Bluetooth Module | 1 | HC-06 also works (slave mode) |
| LED (any colour) | 1 | Bright red or white recommended |
| Resistor 220Ω | 1 | Current limiting for LED |
| Resistor 1kΩ | 1 | Voltage divider (HC-05 RX protection) |
| Resistor 2kΩ | 1 | Voltage divider (HC-05 RX protection) |
| Breadboard + jumper wires | — | Standard prototyping kit |
| USB cable (Arduino) | 1 | For programming and power |
| Webcam | 1 | Built-in laptop cam works fine |
| Smartphone | 1 | Any with Bluetooth; iOS or Android |

---

## Wiring Diagram

```
Arduino Pin 13 ──── 220Ω ──── LED(+)
                              LED(-) ──── GND

Arduino Pin 2 (SoftSerial RX) ◀──── HC-05 TX
Arduino Pin 3 (SoftSerial TX) ────▶ [Voltage Divider] ────▶ HC-05 RX

Voltage Divider Detail:
  Arduino Pin 3 ──── 1kΩ ──┬──── HC-05 RX
                            │
                           2kΩ
                            │
                           GND

HC-05 VCC ──── Arduino 5V
HC-05 GND ──── Arduino GND
```

> ⚠️ **Important:** The HC-05 RX pin operates at 3.3V logic. Connecting Arduino's 5V TX directly **will damage the module** over time. Always use the voltage divider.

---

## Software Requirements

### Arduino Side
- [Arduino IDE](https://www.arduino.cc/en/software) v1.8+ or Arduino IDE 2.x
- Built-in library: `SoftwareSerial` (included with Arduino IDE — no installation needed)

### Python Side
- Python 3.8 or higher
- OpenCV for Python

```bash
pip install opencv-python
```

### Smartphone
- Any Bluetooth serial terminal app, for example:
  - **Android:** [Serial Bluetooth Terminal](https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal)
  - **iOS:** [Bluetooth Terminal](https://apps.apple.com/app/bluetooth-terminal/id1058693037)

---

## Installation

### Step 1 — Upload Arduino Firmware

1. Open `morse_transmitter.ino` in the Arduino IDE.
2. Select **Board:** `Arduino Uno` and the correct **Port**.
3. Click **Upload**.
4. Open **Serial Monitor** at 9600 baud — you should see:
   ```
   Morse Transmitter ready. Send text via BT app.
   ```

### Step 2 — Pair HC-05 via Bluetooth

1. Power the Arduino (USB or external).
2. On your smartphone, scan for Bluetooth devices.
3. Pair with **HC-05** (default PIN: `1234` or `0000`).
4. Open your BT terminal app and connect to HC-05.

### Step 3 — Run the Python Receiver

```bash
python morse_receiver.py
```

A window will open showing the thresholded camera feed. Point it at the LED.

---

## Usage

1. **Start** `morse_receiver.py` on your PC. Position the webcam so the LED fills a small region of the frame.
2. **Open** the BT terminal app on your phone and connect to HC-05.
3. **Type** any text (letters + digits + spaces) and send it.
4. **Watch** the LED blink and the decoded text appear in the OpenCV window.
5. Press **`q`** in the OpenCV window to quit.

### Example

Send via BT app:
```
HELLO WORLD
```

Arduino Serial Monitor output:
```
TX: HELLO WORLD
TX complete.
```

Python terminal output:
```
  [PULSE] ON for 0.198s → '.'  buffer: '.'
  [PULSE] ON for 0.598s → '-'  buffer: '.-'
  ...
  [DECODE] '....' → 'H'
  [DECODE] '.'    → 'E'
  [DECODE] '.-..' → 'L'
  [DECODE] '.-..' → 'L'
  [DECODE] '---'  → 'O'
  [DECODE] (word gap) → SPACE
  ...
── Final decoded message ──────────────────────
HELLO WORLD
```

---

## Timing Protocol

All timing is derived from a single base unit **T = 200 ms**.

| Element | Duration | LED State |
|---|---|---|
| Dot | 1T = 200 ms | HIGH |
| Dash | 3T = 600 ms | HIGH |
| Intra-character gap | 1T = 200 ms | LOW |
| Inter-character gap | 3T = 600 ms | LOW |
| Word gap | 7T = 1400 ms | LOW |

### Why these ratios?

This follows the ITU-R standard Morse code timing specification. The 1:3:7 ratio for symbol/character/word gaps gives the receiver enough separation to classify transitions unambiguously even at ≥30 FPS with debouncing.

### Tolerance Windows (Python decoder)

| Measurement | Tolerance |
|---|---|
| Dot/Dash classification | ±80 ms |
| Character gap | ±150 ms |
| Word gap | ±150 ms |

---

## Morse Code Reference

### Letters

| Letter | Code | | Letter | Code | | Letter | Code |
|---|---|---|---|---|---|---|---|
| A | `.-` | | J | `.---` | | S | `...` |
| B | `-...` | | K | `-.-` | | T | `-` |
| C | `-.-.` | | L | `.-..` | | U | `..-` |
| D | `-..` | | M | `--` | | V | `...-` |
| E | `.` | | N | `-.` | | W | `.--` |
| F | `..-.` | | O | `---` | | X | `-..-` |
| G | `--.` | | P | `.--.` | | Y | `-.--` |
| H | `....` | | Q | `--.-` | | Z | `--..` |
| I | `..` | | R | `.-.` | | | |

### Digits

| Digit | Code | | Digit | Code |
|---|---|---|---|---|
| 0 | `-----` | | 5 | `.....` |
| 1 | `.----` | | 6 | `-....` |
| 2 | `..---` | | 7 | `--...` |
| 3 | `...--` | | 8 | `---..` |
| 4 | `....-` | | 9 | `----.` |

---

## Configuration & Tuning

### Key constants in `morse_receiver.py`

| Constant | Default | Effect |
|---|---|---|
| `T` | `0.200` | Base timing unit — **must match Arduino** |
| `THRESHOLD` | `240` | Pixel brightness cutoff (0–255) |
| `MIN_BRIGHT_PIX` | `30` | Minimum bright pixels to consider LED ON |
| `BRIGHTNESS_WINDOW` | `5` | Moving-average window (frames) |
| `DEBOUNCE_FRAMES` | `2` | Frames before state change accepted |

### Threshold Tuning Procedure

1. Run `morse_receiver.py` with LED **off**.
2. Note the `Bright px (avg)` value displayed at the bottom of the window.
3. Turn LED **on** (manually bridge Pin 13 to 5V or upload a blink sketch briefly).
4. Note the new `Bright px (avg)` value.
5. Set `THRESHOLD` to a value that clearly separates the two states.

### Lighting Recommendations

| Environment | Recommended THRESHOLD |
|---|---|
| Dark room | 200–210 |
| Normal indoor lighting | 230–245 |
| Bright window nearby | 245–250 + use a shroud |
| Direct sunlight | Not recommended — use a tube/shroud |

### Increasing Robustness

- **Cardboard tube:** Slide a 5–10 cm tube over the webcam lens pointing at the LED. This blocks almost all ambient light and dramatically improves reliability.
- **Disable auto-exposure:** Add to `morse_receiver.py` after `cap = cv2.VideoCapture(0)`:
  ```python
  cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
  cap.set(cv2.CAP_PROP_EXPOSURE, -6)
  ```
- **Slow down:** If decoding is unreliable, increase `T` to `300` in **both** files. Remember to re-upload the Arduino sketch.

---

## How It Works

### Arduino Side

1. `SoftwareSerial` receives a text string terminated by `\n` from the HC-05.
2. The string is normalised to uppercase.
3. Each character is looked up in the Morse dictionary.
4. The LED is toggled HIGH/LOW with `delay()` calls matching the timing table.
5. After each character, a 3T inter-character gap is applied (correcting for the 1T already added by the last symbol).

### Python Side

1. Each frame is converted to grayscale and binary-thresholded.
2. Bright pixel count is smoothed over a 5-frame moving average.
3. A debounce filter requires the state to persist for ≥2 frames.
4. On each confirmed transition, `time.time()` measures the duration of the previous state.
5. **ON durations** are classified as dot or dash.
6. **OFF durations** are classified as intra-char (ignored), inter-char (decode buffer), or word (decode + space).
7. After 7T + 300 ms of silence, any remaining buffer is flushed automatically.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| No BT connection | Wrong baud rate | Confirm HC-05 is set to 9600 baud |
| LED never blinks | Wiring issue | Check Pin 13 → 220Ω → LED → GND |
| `?` in decoded output | Timing mismatch | Increase `T`, or reduce ambient light |
| Receiver misses characters | Camera FPS too low | Increase `T` to 300 ms |
| Constant false triggers | Ambient light too high | Lower `THRESHOLD`, use cardboard tube |
| First character always wrong | State machine cold start | Add a 1-second LED-off delay before TX |
| Entire message garbled | `T` mismatch between files | Ensure both files use identical `T` |

---

## Known Limitations

- **Line of sight required** — the webcam must have a direct, unobstructed view of the LED.
- **One-way only** — the system transmits in a single direction. Full duplex would require a second LED + webcam pair in reverse.
- **No error correction** — a misclassified symbol produces a wrong character with no way to detect it.
- **Limited character set** — only A–Z and 0–9 are supported. Punctuation is silently dropped.
- **FPS dependency** — frame rates below ~20 FPS will cause reliable decoding to fail at the default T=200ms. Increase T to compensate.

---

## Future Enhancements

- [ ] **Punctuation support** — add `.,?!/` and common symbols to both dictionaries
- [ ] **Adaptive timing** — measure actual frame rate and auto-adjust tolerance windows
- [ ] **Audio feedback** — play a beep on dot/dash detection for debugging
- [ ] **GUI control panel** — Tkinter or PyQt slider for THRESHOLD and T at runtime
- [ ] **Bidirectional mode** — second Arduino + LED pair for full-duplex communication
- [ ] **Error detection** — add a parity character at the end of each word
- [ ] **Laser pointer TX** — swap LED for a laser module for long-range transmission

---


*Built with Arduino C++ · Python 3 · OpenCV*
