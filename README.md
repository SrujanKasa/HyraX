# HyraX

**One AI. Three Devices. One Ecosystem.**

HyraX is a unified AI-powered branding ecosystem for smart tech gadgets. All devices run on a single intelligent core that understands context, routes commands, and keeps every gadget in sync.

---

## Ecosystem Overview

The **HyraX AI Core** (`hyraX_ai_core.py`) is the central intelligence. It connects all three gadgets under one brain:

- **Device 1** — Smart Display
- - **Device 2** — Wearable Band
  - - **Device 3** — Smart Speaker
   
    - Each device is a separate repository that registers as a `DeviceConnector` to the core.
   
    - ---

    ## AI Core — Key Concepts

    **HyraXCore** — Singleton orchestrator. One instance manages all registered devices, parses natural-language input, and dispatches actions to the right gadget.

    **DeviceConnector** — Abstract interface every HyraX gadget must implement. The AI core talks to all hardware through this contract.

    **EventBus** — Async pub/sub backbone. Devices publish sensor data and voice input; the core publishes AI responses and commands.

    **IntentEngine** — LLM/NLP wrapper. Maps natural language to structured intents and device actions. Plug in OpenAI, Anthropic, Gemini, or a local model.

    ---

    ## Quick Start

    ```python
    import asyncio
    from hyraX_ai_core import create_hyraX_ecosystem, DeviceType

    async def main():
        core = create_hyraX_ecosystem(api_key="YOUR_API_KEY")
        await core.start()
        response = await core.handle_input(
            "Play some chill music",
            source=DeviceType.DEVICE_2  # command from the wearable
        )
        print(response.reply_text)
        await core.stop()

    asyncio.run(main())
    ```

    ---

    ## Roadmap

    - [ ] Device 1 — Smart Display (UI + voice feedback)
    - [ ] - [ ] Device 2 — Wearable Band (health sensors + haptics)
    - [ ] - [ ] Device 3 — Smart Speaker (audio I/O + wake-word)
    - [ ] - [ ] `ecosystem.yaml` shared config
    - [ ] - [ ] OTA updates across all devices
    - [ ] - [ ] Persistent cross-device AI memory
    - [ ] - [ ] Mobile companion app
   
    - [ ] ---
   
    - [ ] ## Ecosystem Repositories
   
    - [ ] | Repository | Role | Status |
    - [ ] |---|---|---|
    - [ ] | `HyraX` (this repo) | AI Core / Hub | Active |
    - [ ] | `HyraX-Device1` | Smart Display | Coming soon |
    - [ ] | `HyraX-Device2` | Wearable Band | Coming soon |
    - [ ] | `HyraX-Device3` | Smart Speaker | Coming soon |
   
    - [ ] ---
   
    - [ ] *HyraX — Built for the future of connected gadgets.*
