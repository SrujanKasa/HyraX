# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: HyraX AI Wrist Device

HyraX is a personal AI ecosystem centered on a wrist-worn device. The project has three layers:
- **Dashboard** — browser-based control center (`dashboard/index.html`)
- **Firmware** — to be written for the wrist device MCU (not yet in repo)
- **Hardware CAD** — OpenSCAD case design (`Old design CAD/hyrax_case.scad`)

## Environment Constraints

- **No Node.js, no Python** on the dev machine. No build step or package manager.
- Dashboard is a **single standalone HTML file** using CDN scripts (Three.js r128 from cdnjs).
- Dev server is a PowerShell HTTP listener defined in `.claude/launch.json`, serving on **port 5500**.
- To preview: `mcp__Claude_Preview__preview_start` with name `"HyraX Dashboard"`, or just open `dashboard/index.html` directly in Chrome/Edge.

## Dashboard Architecture (`dashboard/index.html`)

All UI, logic, and state live in one file. Key sections (marked with `// ═══` comments):

| Section | What it does |
|---|---|
| `THREE.JS BG` | Animated particle field + wireframe icosahedron + orbit rings. Togglable via `toggle3D()`. |
| `DEVICE DRAWER` | Slides in from the right when the HyraX Band dock slot is clicked. Contains stats, OLED preview, device controls, quick actions. |
| `DEVICE DOCK` | Fixed bottom bar — clickable device slots (wrist band + future device placeholders). |
| `AI HERO` | Central panel: Hyra orb, audio waveform strip, chat interface. |
| `SIMULATION` | `startSim()` auto-fires if no physical device. Drives all live stats via `setInterval`. |
| `DEVICE CONNECTION` | `connectDevice()` — tries `navigator.serial.requestPort()` (WebSerial), falls back to sim. |
| `OLED` | `drawOLED(mode)` renders to a `<canvas>` scaled 2× (renders at 384×192, displayed at 192×96). Modes: `clock`, `vitals`, `ai`. Redraws every 500 ms. |
| `WAVEFORM` | Real mic via `getUserMedia` + `AnalyserNode`, or animated sine simulation. |
| `ECOSYSTEM MINI` | Small animated node-graph canvas in the right panel. `requestAnimationFrame` loop. |
| `CHAT` | Stateless — `aiReplies[]` array rotates. No backend. Future: wire to Claude API. |
| `MEMORY` | DOM-only. Future: persist to `localStorage` or IndexedDB. |

## Hardware Stack

| Component | Role | Interface |
|---|---|---|
| RP2040 (USB-C board) | Main MCU | USB Serial (115200 baud) |
| MAX4466 mic breakout | Voice input | Analog |
| MAX98357A I2S amp | Audio output | I2S |
| SSD1306 OLED 128×64 | Display | I2C |
| TP4056 USB-C charger | Battery charging | — |
| 602030 LiPo 500mAh | Power | — |
| 15mm round speaker | Audio output | — |

Expected JSON from firmware over USB serial: `{"batt":85,"temp":28.5,"mic":-42,"hr":72}`

## CAD Design

`Old design CAD/hyrax_case.scad` — OpenSCAD. Set `part = "shell" | "diffuser" | "back" | "preview"` at the top.  
Key dimensions: 45 mm OD, 2 mm wall, 16 mm shell height, 32 mm display bezel.  
STL exports: `hyrax_shell.stl`, `hyrax_back.stl`, `hyrax_diffuser.stl`.

## WebSerial Protocol

The dashboard connects to the RP2040 at 115200 baud. `parseDeviceLine()` parses newline-delimited JSON. Each JSON key maps directly to a stat field. Unknown lines are printed to the connection log as-is.

## Planned Next Steps (not yet built)

- MicroPython firmware for RP2040 (serial JSON output + voice pipeline)
- Claude API integration for real AI chat responses
- IndexedDB persistence for memory bank
- OTA firmware flash from dashboard
