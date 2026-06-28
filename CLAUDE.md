# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: HyraX — One AI. Three Devices. One Ecosystem.

HyraX is a unified AI ecosystem for smart wearable/ambient gadgets. The hub repo contains:
- **`hyraX_ai_core.py`** — Python AI orchestrator (the "brain")
- **`dashboard/index.html`** — Browser-based control center
- **`Old design CAD/`** — OpenSCAD wrist case design + STL exports

Planned satellite repos: `HyraX-Device1` (Smart Display), `HyraX-Device2` (Wearable Band), `HyraX-Device3` (Smart Speaker).

---

## Python AI Core (`hyraX_ai_core.py`)

Async Python (3.10+). No external dependencies beyond stdlib in the current stub; real usage adds an LLM SDK.

**Architecture — four nested layers:**

```
HyraXCore (singleton orchestrator)
└── EventBus (async pub/sub backbone)
└── IntentEngine (LLM/NLP wrapper)
└── DeviceConnector (abstract interface per gadget)
```

| Class | Role |
|---|---|
| `HyraXCore` | Singleton. Registers devices, routes `handle_input()` through `IntentEngine`, dispatches actions via `_dispatch_actions()`, publishes `AI_RESPONSE` events. |
| `EventBus` | Pub/sub. `subscribe(EventType, handler)` + `async publish(HyraXEvent)`. History capped at 50. |
| `IntentEngine` | LLM wrapper. `_call_llm()` is the swap point — replace the stub with Anthropic/OpenAI/Gemini SDK. `_infer_intent()` keyword-matches to 6 intents. |
| `DeviceConnector` | ABC. Each gadget implements `connect()`, `disconnect()`, `send_command()`, `read_sensors()`. Calls `emit()` to put events on the bus. |
| `StubDevice` | Simulates any device for testing without hardware. |

**Entry point for bootstrap:**
```python
core = create_hyraX_ecosystem(api_key="sk-...")  # wires 3 StubDevices
await core.start()
response = await core.handle_input("Play jazz", DeviceType.DEVICE_2)
await core.stop()
```

**Device types:** `DEVICE_1` = Smart Display · `DEVICE_2` = Wearable Band · `DEVICE_3` = Smart Speaker

**Event types:** `VOICE_INPUT` · `SENSOR_DATA` · `AI_RESPONSE` · `COMMAND` · `STATUS_UPDATE` · `SYNC_REQUEST` · `ERROR`

**Plugging in a real LLM:** replace `IntentEngine._call_llm()`. The Anthropic SDK call would be:
```python
import anthropic
client = anthropic.Anthropic(api_key=self._api_key)
msg = client.messages.create(model="claude-sonnet-4-6", max_tokens=1024,
    system=self.SYSTEM_PROMPT, messages=self._context)
return msg.content[0].text
```

**Known issue:** `hyraX_ai_core.py` has inconsistent indentation (mixed 2-space/6-space blocks from the original file). Fix before running: `python -m py_compile hyraX_ai_core.py`.

---

## Dashboard (`dashboard/index.html`)

Single standalone HTML file — no build step, no Node.js, no Python. CDN: Three.js r128.

**Served via** PowerShell HTTP listener on **port 5500** (`.claude/launch.json`). Open with `mcp__Claude_Preview__preview_start` name `"HyraX Dashboard"`, or open the file directly in Chrome/Edge.

**Layout:** 3-row grid — `nav (54px) | main (AI hero + right panel) | dock (130px)`.

Key JS sections (marked `// ═══`):

| Section | Notes |
|---|---|
| `THREE.JS BG` | Particle field + icosahedron + rings. `toggle3D()` kills the RAF loop. |
| `DEVICE DRAWER` | Slides in from right when dock slot is clicked. `openDrawer()` / `closeDrawer()`. |
| `DEVICE DOCK` | Bottom bar. HyraX Band slot + 3 future placeholder slots. |
| `SIMULATION` | `startSim()` — `setInterval` at 1 s driving all stats. Auto-fires when WebSerial unavailable. |
| `DEVICE CONNECTION` | `connectDevice()` tries `navigator.serial.requestPort()` (Chrome/Edge only), falls back to sim. |
| `OLED` | `drawOLED(mode)` on a 384×192 canvas displayed at 192×96 (2× pixel scale). Modes: `clock`/`vitals`/`ai`. |
| `WAVEFORM` | Real mic via `getUserMedia` + `AnalyserNode`; animated sine fallback. |
| `CHAT` | Stateless `aiReplies[]` rotation. Wire to `hyraX_ai_core.py` or Claude API for real responses. |

**WebSerial protocol** (115200 baud, newline-delimited JSON from RP2040):
```json
{"batt": 85, "temp": 28.5, "mic": -42, "hr": 72}
```

---

## Hardware (Wearable Band — Device 2)

| Component | Role | Interface |
|---|---|---|
| RP2040 (USB-C) | MCU | USB Serial @ 115200 |
| MAX4466 | Microphone | Analog ADC |
| MAX98357A | I2S audio amp | I2S |
| SSD1306 128×64 | OLED display | I2C |
| TP4056 | LiPo charger | USB-C |
| 602030 500 mAh LiPo | Power | — |
| 15 mm speaker | Audio output | — |

---

## CAD (`Old design CAD/hyrax_case.scad`)

OpenSCAD — set `part = "shell" | "diffuser" | "back" | "preview"` at top of file.
Key dims: 45 mm OD · 2 mm wall · 16 mm height · 32 mm display bezel.
STL exports already committed: `hyrax_shell.stl`, `hyrax_back.stl`, `hyrax_diffuser.stl`.

---

## Roadmap (from README)

- [ ] Real LLM integration in `IntentEngine._call_llm()`
- [ ] RP2040 MicroPython firmware (serial JSON + voice pipeline)
- [ ] `HyraX-Device1/2/3` satellite repos
- [ ] `ecosystem.yaml` shared config
- [ ] Persistent cross-device AI memory (IndexedDB in dashboard; shared store in core)
- [ ] OTA firmware flash from dashboard
- [ ] Mobile companion app
