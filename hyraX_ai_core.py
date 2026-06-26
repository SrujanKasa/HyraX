"""
HyraX AI Core
=============
Central AI brain for the HyraX ecosystem.
Connects all HyraX gadgets (Device 1, Device 2, Device 3) under one unified intelligence.

Architecture:
  - HyraXCore: Singleton AI orchestrator
    - DeviceConnector: Abstract interface each gadget implements
      - EventBus: Lightweight pub/sub for cross-device messaging
        - IntentEngine: NLP/LLM-powered intent parser
        """

from __future__ import annotations

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("HyraX.Core")


# ---------------------------------------------------------------------------
# Enums & Constants
# ---------------------------------------------------------------------------
class DeviceType(Enum):
      DEVICE_1 = "device_1"   # e.g. Smart Display
    DEVICE_2 = "device_2"   # e.g. Wearable Band
    DEVICE_3 = "device_3"   # e.g. Smart Speaker


class EventType(Enum):
      VOICE_INPUT     = auto()
      SENSOR_DATA     = auto()
      AI_RESPONSE     = auto()
      COMMAND         = auto()
      STATUS_UPDATE   = auto()
      SYNC_REQUEST    = auto()
      ERROR           = auto()


HYRAХ_VERSION = "1.0.0"
ECOSYSTEM_ID  = "HyraX-Ecosystem"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class HyraXEvent:
      """Immutable event that travels across the HyraX EventBus."""
      event_type: EventType
      source_device: DeviceType
      payload: Dict[str, Any]
      event_id: str         = field(default_factory=lambda: str(uuid4()))
      timestamp: float      = field(default_factory=time.time)

    def to_json(self) -> str:
              return json.dumps({
                            "event_id":     self.event_id,
                            "event_type":   self.event_type.name,
                            "source":       self.source_device.value,
                            "payload":      self.payload,
                            "timestamp":    self.timestamp,
              })


@dataclass
class AIResponse:
      """Structured response produced by the IntentEngine."""
      intent: str
      reply_text: str
      actions: List[Dict[str, Any]] = field(default_factory=list)
      confidence: float             = 1.0
      target_devices: List[DeviceType] = field(default_factory=list)


# ---------------------------------------------------------------------------
# EventBus – pub/sub backbone
# ---------------------------------------------------------------------------
class EventBus:
      """
          Lightweight async publish-subscribe bus.
              Devices subscribe to event types; the AI core publishes responses.
                  """

    def __init__(self) -> None:
              self._subscribers: Dict[EventType, List[Callable]] = {e: [] for e in EventType}
              self._history: List[HyraXEvent] = []

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
              self._subscribers[event_type].append(handler)
              logger.debug(f"Subscribed {handler.__qualname__} to {event_type.name}")

    async def publish(self, event: HyraXEvent) -> None:
              self._history.append(event)
              logger.info(f"[EventBus] {event.source_device.value} → {event.event_type.name}")
              handlers = self._subscribers.get(event.event_type, [])
              await asyncio.gather(*(self._call(h, event) for h in handlers))

    @staticmethod
    async def _call(handler: Callable, event: HyraXEvent) -> None:
              result = handler(event)
              if asyncio.iscoroutine(result):
                            await result

          def get_history(self, limit: int = 50) -> List[HyraXEvent]:
                    return self._history[-limit:]


# ---------------------------------------------------------------------------
# Abstract Device Connector
# ---------------------------------------------------------------------------
class DeviceConnector(ABC):
      """
          Every HyraX gadget must implement this interface.
              The AI core talks to all devices through this contract.
                  """

    def __init__(self, device_type: DeviceType, bus: EventBus) -> None:
              self.device_type = device_type
              self._bus        = bus
              self._online     = False
              self._metadata: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    @abstractmethod
    async def connect(self) -> bool:
              """Establish connection to the physical/virtual device."""

    @abstractmethod
    async def disconnect(self) -> None:
              """Gracefully shut down the device connection."""

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------
    @abstractmethod
    async def send_command(self, command: Dict[str, Any]) -> bool:
              """Push a command to the device (e.g. play audio, show text)."""

    @abstractmethod
    async def read_sensors(self) -> Dict[str, Any]:
              """Pull the latest sensor / status data from the device."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def emit(self, event_type: EventType, payload: Dict[str, Any]) -> None:
              event = HyraXEvent(
                            event_type=event_type,
                            source_device=self.device_type,
                            payload=payload,
              )
              await self._bus.publish(event)

    @property
    def is_online(self) -> bool:
              return self._online

    def __repr__(self) -> str:
              status = "ONLINE" if self._online else "OFFLINE"
              return f"<DeviceConnector {self.device_type.value} [{status}]>"


# ---------------------------------------------------------------------------
# Intent Engine (LLM wrapper)
# ---------------------------------------------------------------------------
class IntentEngine:
      """
          Wraps any LLM / NLP backend to understand user intent and
              produce structured AIResponse objects.

                  Swap `_call_llm` to plug in OpenAI, Anthropic, Gemini, or a local model.
                      """

    SYSTEM_PROMPT = (
              "You are HyraX, an advanced AI assistant embedded in a smart gadget ecosystem. "
              "You control multiple devices (smart display, wearable, smart speaker) under one brain. "
              "Be concise, helpful, and context-aware."
    )

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o") -> None:
              self._api_key = api_key
              self._model   = model
              self._context: List[Dict[str, str]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def process(self, user_input: str, source: DeviceType) -> AIResponse:
              logger.info(f"[IntentEngine] Processing input from {source.value}: '{user_input}'")
              self._context.append({"role": "user", "content": user_input})

        raw = await self._call_llm(user_input)

        self._context.append({"role": "assistant", "content": raw})
        return self._parse_response(raw, user_input)

    # ------------------------------------------------------------------
    # LLM call – replace with your provider SDK
    # ------------------------------------------------------------------
    async def _call_llm(self, prompt: str) -> str:
              """
                      Stub implementation.
                              Replace with real SDK call, e.g.:
                                          import openai
                                                      client = openai.AsyncOpenAI(api_key=self._api_key)
                                                                  completion = await client.chat.completions.create(
                                                                                  model=self._model,
                                                                                                  messages=[{"role":"system","content":self.SYSTEM_PROMPT}] + self._context,
                                                                                                              )
                                                                                                                          return completion.choices[0].message.content
                                                                                                                                  """
              await asyncio.sleep(0.05)   # simulate network latency
        return f"[HyraX stub] Understood: '{prompt}'. Action dispatched to all devices."

    # ------------------------------------------------------------------
    # Response parser
    # ------------------------------------------------------------------
    def _parse_response(self, raw: str, original_input: str) -> AIResponse:
              intent = self._infer_intent(original_input)
              return AIResponse(
                  intent=intent,
                  reply_text=raw,
                  actions=self._build_actions(intent),
                  target_devices=list(DeviceType),
              )

    @staticmethod
    def _infer_intent(text: str) -> str:
              text = text.lower()
              if any(w in text for w in ("play", "music", "song")):
                            return "media_play"
                        if any(w in text for w in ("weather", "temperature", "forecast")):
                                      return "weather_query"
                                  if any(w in text for w in ("remind", "alarm", "timer")):
                                                return "set_reminder"
                                            if any(w in text for w in ("light", "dim", "bright")):
                                                          return "control_lights"
                                                      if any(w in text for w in ("status", "health", "battery")):
                                                                    return "device_status"
                                                                return "general_query"

    @staticmethod
    def _build_actions(intent: str) -> List[Dict[str, Any]]:
              action_map: Dict[str, List[Dict[str, Any]]] = {
                  "media_play":    [{"action": "play_audio",    "device": DeviceType.DEVICE_3.value}],
                  "weather_query": [{"action": "show_weather",  "device": DeviceType.DEVICE_1.value}],
                  "set_reminder":  [{"action": "set_alarm",     "device": DeviceType.DEVICE_2.value}],
                  "control_lights":[{"action": "adjust_lights", "device": "broadcast"}],
                  "device_status": [{"action": "status_report", "device": "broadcast"}],
                  "general_query": [{"action": "reply_text",    "device": "broadcast"}],
    }
        return action_map.get(intent, [])


# ---------------------------------------------------------------------------
# HyraX Core – singleton orchestrator
# ---------------------------------------------------------------------------
class HyraXCore:
      """
          The central nervous system of the HyraX ecosystem.

              Usage:
                      core = HyraXCore(api_key="sk-...")
                              core.register_device(MySmartDisplay())
                                      core.register_device(MyWearable())
                                              core.register_device(MySpeaker())
                                                      await core.start()
                                                              response = await core.handle_input("Play some jazz", DeviceType.DEVICE_2)
                                                                  """

    _instance: Optional[HyraXCore] = None   # singleton guard

    def __new__(cls, *args, **kwargs) -> HyraXCore:
              if cls._instance is None:
                            cls._instance = super().__new__(cls)
                        return cls._instance

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o") -> None:
              if hasattr(self, "_initialized"):
                            return
                        self._initialized = True

        self.bus           = EventBus()
        self.intent_engine = IntentEngine(api_key=api_key, model=model)
        self._devices: Dict[DeviceType, DeviceConnector] = {}
        self._running = False

        # Wire up core event handlers
        self.bus.subscribe(EventType.VOICE_INPUT,  self._on_voice_input)
        self.bus.subscribe(EventType.SENSOR_DATA,  self._on_sensor_data)
        self.bus.subscribe(EventType.ERROR,        self._on_error)

        logger.info(f"HyraXCore v{HYRAХ_VERSION} initialised | ecosystem: {ECOSYSTEM_ID}")

    # ------------------------------------------------------------------
    # Device management
    # ------------------------------------------------------------------
    def register_device(self, device: DeviceConnector) -> None:
              self._devices[device.device_type] = device
        logger.info(f"Device registered: {device}")

    def get_device(self, device_type: DeviceType) -> Optional[DeviceConnector]:
              return self._devices.get(device_type)

    def all_devices(self) -> List[DeviceConnector]:
              return list(self._devices.values())

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def start(self) -> None:
              logger.info("HyraXCore starting up…")
        results = await asyncio.gather(
                      *(d.connect() for d in self._devices.values()),
                      return_exceptions=True,
        )
        for device, result in zip(self._devices.values(), results):
                      if isinstance(result, Exception):
                                        logger.error(f"Failed to connect {device}: {result}")
else:
                logger.info(f"{device} connected: {result}")
          self._running = True
        logger.info("HyraXCore is ONLINE — all devices active.")

    async def stop(self) -> None:
              logger.info("HyraXCore shutting down…")
        await asyncio.gather(*(d.disconnect() for d in self._devices.values()))
        self._running = False
        logger.info("HyraXCore OFFLINE.")

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    async def handle_input(
              self,
              user_input: str,
              source: DeviceType,
    ) -> AIResponse:
              """
                      Process natural-language input from any device and dispatch
                              actions back to the relevant gadgets.
                                      """
        if not self._running:
                      raise RuntimeError("HyraXCore is not running. Call await core.start() first.")

        response = await self.intent_engine.process(user_input, source)
        await self._dispatch_actions(response)
        return response

    # ------------------------------------------------------------------
    # Action dispatcher
    # ------------------------------------------------------------------
    async def _dispatch_actions(self, response: AIResponse) -> None:
              tasks = []
        for action in response.actions:
                      target = action.get("device")
                      if target == "broadcast":
                                        for device in self._devices.values():
                                                              tasks.append(device.send_command(action))
                      else:
                                        try:
                                                              dt = DeviceType(target)
                                                              if dt in self._devices:
                                                                                        tasks.append(self._devices[dt].send_command(action))
                                        except ValueError:
                                                              logger.warning(f"Unknown device target: {target}")

                                if tasks:
                      await asyncio.gather(*tasks, return_exceptions=True)

        # Broadcast AI response event to all subscribers
        await self.bus.publish(HyraXEvent(
                      event_type=EventType.AI_RESPONSE,
                      source_device=DeviceType.DEVICE_1,  # core uses Device 1 as default origin
                      payload={"intent": response.intent, "reply": response.reply_text},
        ))

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------
    async def _on_voice_input(self, event: HyraXEvent) -> None:
              text = event.payload.get("text", "")
        if text:
                      await self.handle_input(text, event.source_device)

    def _on_sensor_data(self, event: HyraXEvent) -> None:
              logger.debug(f"[SensorData] {event.source_device.value}: {event.payload}")

    def _on_error(self, event: HyraXEvent) -> None:
              logger.error(f"[DeviceError] {event.source_device.value}: {event.payload}")

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
              return {
                            "version":   HYRAХ_VERSION,
                            "ecosystem": ECOSYSTEM_ID,
                            "running":   self._running,
                            "devices": {
                                              dt.value: d.is_online
                                              for dt, d in self._devices.items()
                            },
                            "event_history_count": len(self.bus.get_history()),
              }


# ---------------------------------------------------------------------------
# Demo stub devices (for testing without real hardware)
# ---------------------------------------------------------------------------
class StubDevice(DeviceConnector):
      """
          Generic stub that simulates any HyraX gadget.
              Replace with real hardware drivers in production.
                  """

    async def connect(self) -> bool:
              await asyncio.sleep(0.1)
        self._online = True
        logger.info(f"[StubDevice] {self.device_type.value} connected (simulated).")
        return True

    async def disconnect(self) -> None:
              self._online = False
        logger.info(f"[StubDevice] {self.device_type.value} disconnected.")

    async def send_command(self, command: Dict[str, Any]) -> bool:
              logger.info(f"[StubDevice] {self.device_type.value} executing: {command}")
        await asyncio.sleep(0.02)
        return True

    async def read_sensors(self) -> Dict[str, Any]:
              return {"device": self.device_type.value, "battery": 85, "signal": "strong"}


# ---------------------------------------------------------------------------
# Quick-start helper
# ---------------------------------------------------------------------------
def create_hyraX_ecosystem(api_key: Optional[str] = None) -> HyraXCore:
      """
          Bootstrap a fully wired HyraX ecosystem with stub devices.
              Replace StubDevice instances with real hardware connectors.

                  Example:
                          import asyncio
                                  from hyraX_ai_core import create_hyraX_ecosystem, DeviceType

                                          async def main():
                                                      core = create_hyraX_ecosystem(api_key="sk-...")
                                                                  await core.start()
                                                                              response = await core.handle_input("What's the weather today?", DeviceType.DEVICE_1)
                                                                                          print(response.reply_text)
                                                                                                      await core.stop()
                                                                                                      
                                                                                                              asyncio.run(main())
                                                                                                                  """
    core = HyraXCore(api_key=api_key)
    bus  = core.bus

    core.register_device(StubDevice(DeviceType.DEVICE_1, bus))
    core.register_device(StubDevice(DeviceType.DEVICE_2, bus))
    core.register_device(StubDevice(DeviceType.DEVICE_3, bus))

    return core


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
      async def _demo():
                core = create_hyraX_ecosystem()
        await core.start()

        print("\n=== HyraX Ecosystem Status ===")
        print(json.dumps(core.status(), indent=2))

        inputs = [
                      ("Play some chill jazz", DeviceType.DEVICE_2),
                      ("What's the weather forecast?", DeviceType.DEVICE_1),
                      ("Set a reminder for 8 AM tomorrow", DeviceType.DEVICE_3),
                      ("Show battery status", DeviceType.DEVICE_1),
        ]

        print("\n=== Processing Commands ===")
        for text, source in inputs:
                      response = await core.handle_input(text, source)
            print(f"\n[{source.value}] '{text}'")
            print(f"  Intent  : {response.intent}")
            print(f"  Reply   : {response.reply_text}")
            print(f"  Actions : {response.actions}")

        await core.stop()

    asyncio.run(_demo())
