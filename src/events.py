"""
This file contains python definitions of events which mirror those found in the move contracts

  assembly   : AssemblyCreatedEvent
  character  : CharacterCreatedEvent
  gate       : GateCreatedEvent, GateLinkedEvent, GateUnlinkedEvent,
               JumpEvent, ExtensionAuthorizedEvent
  killmail   : KillmailCreatedEvent
  storage_unit: StorageUnitCreatedEvent, ExtensionAuthorizedEvent
  turret     : TurretCreatedEvent, PriorityListUpdatedEvent,
               ExtensionAuthorizedEvent
  network_node: NetworkNodeCreatedEvent
  fuel       : FuelEvent, FuelEfficiencySetEvent, FuelEfficiencyRemovedEvent
  inventory  : ItemMintedEvent, ItemBurnedEvent, ItemDepositedEvent,
               ItemWithdrawnEvent, ItemDestroyedEvent
  status     : StatusChangedEvent
  metadata   : MetadataChangedEvent

"""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Self
from datetime import datetime, timezone
from enum import Enum


@dataclass(kw_only=True)
class EventBase(object):
    module: str = "undefined"
    event_type: str = "undefined"
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

    def to_str(self) -> str:
        """As a string, single line"""
        return str(self.__class__)



# ---------------------------------------------------------------------------
# Shared primitive types (mirror Move structs)
# ---------------------------------------------------------------------------

class LossType(str, Enum):
    """ From killmail.move """
    SHIP      = "SHIP"
    STRUCTURE = "STRUCTURE"
    UNKNOWN   = "UNKNOWN"

    @classmethod
    def from_rpc(cls, raw) -> Self:
        if isinstance(raw, str):
            return cls[raw] if raw in cls._member_map_ else cls.UNKNOWN
        if isinstance(raw, dict):
            key = raw.get('variant', None)
            return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


@dataclass(kw_only=True)
class TenantItemId:
    item_id: int
    tenant: str

    @classmethod
    def from_rpc(cls, raw) -> Self:
        if not isinstance(raw, dict):
            return cls(0, "")
        return cls(
            item_id=int(raw.get("item_id", 0)),
            tenant=str(raw.get("tenant", 0)),
        )

    def __str__(self) -> str:
        return f"{self.item_id}@{self.tenant}"

    def __hash__(self):
        # Return a hash of an internal immutable value
        return hash(f"{self.tenant}::{self.item_id}")

def _ts(raw_event: dict) -> Optional[datetime]:
    ts = raw_event.get("timestampMs")
    if ts:
        return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
    return None

def _tx(raw_event: dict) -> str:
    return raw_event.get("id", {}).get("txDigest", "")

def _cp(raw_event: dict) -> int:
    return int(raw_event.get("checkpoint", 0))


# ---------------------------------------------------------------------------
# Per-module event definitions
# ---------------------------------------------------------------------------


# ---- status ----------------------------------------------------------------

class AssemblyStatusValue(str, Enum):
    """ From status.move Status enum """
    NULL    = "NULL"
    OFFLINE = "OFFLINE"
    ONLINE  = "ONLINE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_rpc(cls, raw) -> Self:
        if isinstance(raw, str):
            return cls[raw] if raw in cls._member_map_ else cls.UNKNOWN
        if isinstance(raw, dict):
            key = raw.get('variant', None)
            return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


class StatusAction(str, Enum):
    """ From status.move Action enum """
    ANCHORED   = "ANCHORED"
    ONLINE     = "ONLINE"
    OFFLINE    = "OFFLINE"
    UNANCHORED = "UNANCHORED"
    UNKNOWN    = "UNKNOWN"

    @classmethod
    def from_rpc(cls, raw) -> Self:
        if isinstance(raw, str):
            return cls[raw] if raw in cls._member_map_ else cls.UNKNOWN
        if isinstance(raw, dict):
            key = raw.get('variant', None)
            return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


@dataclass(kw_only=True)
class StatusChangedEvent(EventBase):
    module: str = "status"
    event_type: str = "StatusChangedEvent"
    assembly_id:  str
    assembly_key: TenantItemId
    status:       AssemblyStatusValue
    action:       StatusAction

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            status       = AssemblyStatusValue.from_rpc(f.get("status")),
            action       = StatusAction.from_rpc(f.get("action")),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly_id={self.assembly_id} "
            f"key={self.assembly_key} "
            f"status={self.status.value} "
            f"action={self.action.value}"
        )

# ---- assembly --------------------------------------------------------------

@dataclass(kw_only=True)
class AssemblyCreatedEvent(EventBase):
    module: str = "assembly"
    event_type: str = "AssemblyCreatedEvent"
    assembly_id:    str
    assembly_key:   TenantItemId
    owner_cap_id:   str
    type_id:        int
    # envelope

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            owner_cap_id = f.get("owner_cap_id", ""),
            type_id      = int(f.get("type_id", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly_id={self.assembly_id} "
            f"key={self.assembly_key} "
            f"owner_cap={self.owner_cap_id} "
            f"type_id={self.type_id}"
        )

# ---- character -------------------------------------------------------------

@dataclass(kw_only=True)
class CharacterCreatedEvent(EventBase):
    module: str = "character"
    event_type: str = "CharacterCreatedEvent"
    character_id:      str
    key:               TenantItemId
    tribe_id:          int
    character_address: str

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            character_id      = f.get("character_id", ""),
            key               = TenantItemId.from_rpc(f.get("key", {})),
            tribe_id          = int(f.get("tribe_id", 0)),
            character_address = f.get("character_address", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"character_id={self.character_id} "
            f"key={self.key} "
            f"tribe_id={self.tribe_id} "
            f"address={self.character_address}"
        )

# ---- gate ------------------------------------------------------------------

@dataclass(kw_only=True)
class GateCreatedEvent(EventBase):
    module: str = "gate"
    event_type: str = "GateCreatedEvent"
    assembly_id:   str
    assembly_key:  TenantItemId
    owner_cap_id:  str
    type_id:       int
    location_hash: str
    status:        AssemblyStatusValue

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            owner_cap_id = f.get("owner_cap_id", ""),
            type_id      = int(f.get("type_id", 0)),
            location_hash= str(f.get("location_hash", "")),
            status       = AssemblyStatusValue.from_rpc(f.get("status")),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly_id={self.assembly_id} "
            f"key={self.assembly_key} "
            f"owner_cap={self.owner_cap_id} "
            f"type_id={self.type_id} "
            f"location={self.location_hash} "
            f"status={self.status}"
        )

@dataclass(kw_only=True)
class GateLinkedEvent(EventBase):
    module: str = "gate"
    event_type: str = "GateLinkedEvent"
    source_gate_id:        str
    source_gate_key:       TenantItemId
    destination_gate_id:   str
    destination_gate_key:  TenantItemId

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            source_gate_id       = f.get("source_gate_id", ""),
            source_gate_key      = TenantItemId.from_rpc(f.get("source_gate_key", {})),
            destination_gate_id  = f.get("destination_gate_id", ""),
            destination_gate_key = TenantItemId.from_rpc(f.get("destination_gate_key", {})),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"src={self.source_gate_key} ({self.source_gate_id}) "
            f"-> dst={self.destination_gate_key} ({self.destination_gate_id})"
        )

@dataclass(kw_only=True)
class GateUnlinkedEvent(EventBase):
    module: str = "gate"
    event_type: str = "GateUnlinkedEvent"
    source_gate_id: str
    source_gate_key: TenantItemId
    destination_gate_id:   str
    destination_gate_key:  TenantItemId

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            source_gate_id       = f.get("source_gate_id", ""),
            source_gate_key      = TenantItemId.from_rpc(f.get("source_gate_key", {})),
            destination_gate_id  = f.get("destination_gate_id", ""),
            destination_gate_key = TenantItemId.from_rpc(f.get("destination_gate_key", {})),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"src={self.source_gate_key} ({self.source_gate_id}) "
            f"-x dst={self.destination_gate_key} ({self.destination_gate_id})"
        )

@dataclass(kw_only=True)
class JumpEvent(EventBase):
    module: str = "gate"
    event_type: str = "JumpEvent"
    source_gate_id:        str
    source_gate_key:       TenantItemId
    destination_gate_id:   str
    destination_gate_key:  TenantItemId
    character_id:          str
    character_key:         TenantItemId

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            source_gate_id       = f.get("source_gate_id", ""),
            source_gate_key      = TenantItemId.from_rpc(f.get("source_gate_key", {})),
            destination_gate_id  = f.get("destination_gate_id", ""),
            destination_gate_key = TenantItemId.from_rpc(f.get("destination_gate_key", {})),
            character_id         = f.get("character_id", ""),
            character_key        = TenantItemId.from_rpc(f.get("character_key", {})),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"character={self.character_key} ({self.character_id}) "
            f"src={self.source_gate_key} ({self.source_gate_id}) "
            f"-> dst={self.destination_gate_key} ({self.destination_gate_id})"
        )

@dataclass(kw_only=True)
class ExtensionAuthorizedEvent(EventBase):
    """Shared by gate, storage_unit and turret modules."""
    module: str = "undefined"
    event_type: str = "ExtensionAuthorizedEvent"
    assembly_id:        str
    assembly_key:       TenantItemId
    extension_type:     Any
    previous_extension: Any
    owner_cap_id:       str

    @classmethod
    def from_rpc(cls, r: dict, module: str) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            module             = module,
            assembly_id        = f.get("assembly_id", ""),
            assembly_key       = TenantItemId.from_rpc(f.get("assembly_key", {})),
            extension_type     = f.get("extension_type"),
            previous_extension = f.get("previous_extension"),
            owner_cap_id       = f.get("owner_cap_id", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly_id={self.assembly_id} "
            f"key={self.assembly_key} "
            f"extension_type={self.extension_type} "
            f"previous={self.previous_extension} "
            f"owner_cap={self.owner_cap_id}"
        )

# ---- killmail --------------------------------------------------------------

@dataclass(kw_only=True)
class KillmailCreatedEvent(EventBase):
    module: str = "killmail"
    event_type: str = "KillmailCreatedEvent"
    key:                      TenantItemId
    killer_id:                TenantItemId
    victim_id:                TenantItemId
    reported_by_character_id: TenantItemId
    loss_type:                LossType
    kill_timestamp:           int
    solar_system_id:          TenantItemId

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            key                      = TenantItemId.from_rpc(f.get("key", {})),
            killer_id                = TenantItemId.from_rpc(f.get("killer_id", {})),
            victim_id                = TenantItemId.from_rpc(f.get("victim_id", {})),
            reported_by_character_id = TenantItemId.from_rpc(f.get("reported_by_character_id", {})),
            loss_type                = LossType.from_rpc(f.get("loss_type")),
            kill_timestamp           = int(f.get("kill_timestamp", 0)),
            solar_system_id          = TenantItemId.from_rpc(f.get("solar_system_id", {})),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"killer={self.killer_id} "
            f"victim={self.victim_id} "
            f"loss_type={self.loss_type.value} "
            f"solar_system={self.solar_system_id} "
            f"reported_by={self.reported_by_character_id}"
        )

# ---- storage_unit ----------------------------------------------------------

@dataclass(kw_only=True)
class StorageUnitCreatedEvent(EventBase):
    module: str = "storage_unit"
    event_type: str = "StorageUnitCreatedEvent"
    storage_unit_id: str
    assembly_key:    TenantItemId
    owner_cap_id:    str
    type_id:         int
    max_capacity:    int
    location_hash:   str
    status:          Any

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            storage_unit_id = f.get("storage_unit_id", ""),
            assembly_key    = TenantItemId.from_rpc(f.get("assembly_key", {})),
            owner_cap_id    = f.get("owner_cap_id", ""),
            type_id         = int(f.get("type_id", 0)),
            max_capacity    = int(f.get("max_capacity", 0)),
            location_hash   = str(f.get("location_hash", "")),
            status          = f.get("status"),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"storage_unit_id={self.storage_unit_id} "
            f"key={self.assembly_key} "
            f"owner_cap={self.owner_cap_id} "
            f"type_id={self.type_id} "
            f"max_capacity={self.max_capacity} "
            f"location={self.location_hash} "
            f"status={self.status}"
        )

# ---- turret ----------------------------------------------------------------

@dataclass(kw_only=True)
class TurretCreatedEvent(EventBase):
    module: str = "turret"
    event_type: str = "TurretCreatedEvent"
    turret_id:    str
    turret_key:   TenantItemId
    owner_cap_id: str
    type_id:      int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            turret_id    = f.get("turret_id", ""),
            turret_key   = TenantItemId.from_rpc(f.get("turret_key", {})),
            owner_cap_id = f.get("owner_cap_id", ""),
            type_id      = int(f.get("type_id", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"turret_id={self.turret_id} "
            f"key={self.turret_key} "
            f"owner_cap={self.owner_cap_id} "
            f"type_id={self.type_id}"
        )

@dataclass(kw_only=True)
class PriorityListUpdatedEvent(EventBase):
    module: str = "turret"
    event_type: str = "PriorityListUpdatedEvent"
    turret_id:     str
    priority_list: list   # raw list of TargetCandidate dicts

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            turret_id     = f.get("turret_id", ""),
            priority_list = f.get("priority_list", []),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        count = len(self.priority_list)
        entries = ", ".join(str(e) for e in self.priority_list[:5])
        suffix = f", +{count - 5} more" if count > 5 else ""
        return f"turret_id={self.turret_id} priority_list=[{entries}{suffix}] ({count} entries)"

# ---- network_node ----------------------------------------------------------

@dataclass(kw_only=True)
class NetworkNodeCreatedEvent(EventBase):
    module: str = "network_node"
    event_type: str = "NetworkNodeCreatedEvent"
    network_node_id:       str
    assembly_key:          TenantItemId
    owner_cap_id:          str
    type_id:               int
    fuel_max_capacity:     int
    fuel_burn_rate_in_ms:  int
    max_energy_production: int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            network_node_id       = f.get("network_node_id", ""),
            assembly_key          = TenantItemId.from_rpc(f.get("assembly_key", {})),
            owner_cap_id          = f.get("owner_cap_id", ""),
            type_id               = int(f.get("type_id", 0)),
            fuel_max_capacity     = int(f.get("fuel_max_capacity", 0)),
            fuel_burn_rate_in_ms  = int(f.get("fuel_burn_rate_in_ms", 0)),
            max_energy_production = int(f.get("max_energy_production", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"network_node_id={self.network_node_id} "
            f"key={self.assembly_key} "
            f"owner_cap={self.owner_cap_id} "
            f"type_id={self.type_id} "
            f"fuel_max={self.fuel_max_capacity} "
            f"burn_rate={self.fuel_burn_rate_in_ms}ms "
            f"max_energy={self.max_energy_production}"
        )

# ---- fuel ------------------------------------------------------------------

class FuelAction(str, Enum):
    """ From fuel.move Action enum """
    DEPOSITED       = "DEPOSITED"
    WITHDRAWN       = "WITHDRAWN"
    BURNING_STARTED = "BURNING_STARTED"
    BURNING_STOPPED = "BURNING_STOPPED"
    BURNING_UPDATED = "BURNING_UPDATED"
    DELETED         = "DELETED"
    UNKNOWN         = "UNKNOWN"

    @classmethod
    def from_rpc(cls, raw) -> Self:
        if isinstance(raw, str):
            return cls[raw] if raw in cls._member_map_ else cls.UNKNOWN
        if isinstance(raw, dict):
            key = raw.get('variant', None)
            return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


@dataclass(kw_only=True)
class FuelEvent(EventBase):
    module: str = "fuel"
    event_type: str = "FuelEvent"
    assembly_id:  str
    assembly_key: TenantItemId
    type_id:      int
    old_quantity: int
    new_quantity: int
    is_burning:   bool
    action:       FuelAction

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            type_id      = int(f.get("type_id", 0)),
            old_quantity = int(f.get("old_quantity", 0)),
            new_quantity = int(f.get("new_quantity", 0)),
            is_burning   = bool(f.get("is_burning", False)),
            action       = FuelAction.from_rpc(f.get("action")),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly_id={self.assembly_id} "
            f"key={self.assembly_key} "
            f"type_id={self.type_id} "
            f"qty={self.old_quantity} -> {self.new_quantity} "
            f"burning={self.is_burning} "
            f"action={self.action.value}"
        )

@dataclass(kw_only=True)
class FuelEfficiencySetEvent(EventBase):
    module: str = "fuel"
    event_type: str = "FuelEfficiencySetEvent"
    fuel_type_id: int
    efficiency:   int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            fuel_type_id = int(f.get("fuel_type_id", 0)),
            efficiency   = int(f.get("efficiency", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return f"fuel_type_id={self.fuel_type_id} efficiency={self.efficiency}"

@dataclass(kw_only=True)
class FuelEfficiencyRemovedEvent(EventBase):
    module: str = "fuel"
    event_type: str = "FuelEfficiencyRemovedEvent"
    fuel_type_id: int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            fuel_type_id = int(f.get("fuel_type_id", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return f"fuel_type_id={self.fuel_type_id}"

# ---- inventory -------------------------------------------------------------

@dataclass(kw_only=True)
class ItemMintedEvent(EventBase):
    module: str = "inventory"
    event_type: str = "ItemMintedEvent"
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            character_id = f.get("character_id", ""),
            character_key= TenantItemId.from_rpc(f.get("character_key", {})),
            item_id      = int(f.get("item_id", 0)),
            type_id      = int(f.get("type_id", 0)),
            quantity     = int(f.get("quantity", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly={self.assembly_key} ({self.assembly_id}) "
            f"character={self.character_key} ({self.character_id}) "
            f"item_id={self.item_id} type_id={self.type_id} qty={self.quantity}"
        )

@dataclass(kw_only=True)
class ItemBurnedEvent(EventBase):
    module: str = "inventory"
    event_type: str = "ItemBurnedEvent"
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            character_id = f.get("character_id", ""),
            character_key= TenantItemId.from_rpc(f.get("character_key", {})),
            item_id      = int(f.get("item_id", 0)),
            type_id      = int(f.get("type_id", 0)),
            quantity     = int(f.get("quantity", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly={self.assembly_key} ({self.assembly_id}) "
            f"character={self.character_key} ({self.character_id}) "
            f"item_id={self.item_id} type_id={self.type_id} qty={self.quantity}"
        )

@dataclass(kw_only=True)
class ItemDepositedEvent(EventBase):
    module: str = "inventory"
    event_type: str = "ItemDepositedEvent"
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            character_id = f.get("character_id", ""),
            character_key= TenantItemId.from_rpc(f.get("character_key", {})),
            item_id      = int(f.get("item_id", 0)),
            type_id      = int(f.get("type_id", 0)),
            quantity     = int(f.get("quantity", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly={self.assembly_key} ({self.assembly_id}) "
            f"character={self.character_key} ({self.character_id}) "
            f"item_id={self.item_id} type_id={self.type_id} qty={self.quantity}"
        )

@dataclass(kw_only=True)
class ItemWithdrawnEvent(EventBase):
    module: str = "inventory"
    event_type: str = "ItemWithdrawnEvent"
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            character_id = f.get("character_id", ""),
            character_key= TenantItemId.from_rpc(f.get("character_key", {})),
            item_id      = int(f.get("item_id", 0)),
            type_id      = int(f.get("type_id", 0)),
            quantity     = int(f.get("quantity", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly={self.assembly_key} ({self.assembly_id}) "
            f"character={self.character_key} ({self.character_id}) "
            f"item_id={self.item_id} type_id={self.type_id} qty={self.quantity}"
        )

@dataclass(kw_only=True)
class ItemDestroyedEvent(EventBase):
    module: str = "inventory"
    event_type: str = "ItemDestroyedEvent"
    assembly_id:  str
    assembly_key: TenantItemId
    item_id:      int
    type_id:      int
    quantity:     int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            item_id      = int(f.get("item_id", 0)),
            type_id      = int(f.get("type_id", 0)),
            quantity     = int(f.get("quantity", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly={self.assembly_key} ({self.assembly_id}) "
            f"item_id={self.item_id} type_id={self.type_id} qty={self.quantity}"
        )

# ---- metadata --------------------------------------------------------------

@dataclass(kw_only=True)
class MetadataChangedEvent(EventBase):
    module: str = "metadata"
    event_type: str = "MetadataChangedEvent"
    assembly_id:  str
    assembly_key: TenantItemId
    name:         str
    description:  str
    url:          str

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            name         = f.get("name", ""),
            description  = f.get("description", ""),
            url          = f.get("url", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"assembly_id={self.assembly_id} "
            f"key={self.assembly_key} "
            f"name={self.name!r} "
            f"description={self.description!r} "
            f"url={self.url}"
        )

# ---- energy ----------------------------------------------------------------

@dataclass(kw_only=True)
class StartEnergyProductionEvent(EventBase):
    module: str = "energy"
    event_type: str = "StartEnergyProductionEvent"
    energy_source_id: str
    current_energy_production: int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            energy_source_id=f.get("energy_source_id", ""),
            current_energy_production=int(f.get("current_energy_production", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"energy_source_id={self.energy_source_id} "
            f"current_energy_production={self.current_energy_production}"
        )


@dataclass(kw_only=True)
class StopEnergyProductionEvent(EventBase):
    module: str = "energy"
    event_type: str = "StopEnergyProductionEvent"
    energy_source_id: str

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            energy_source_id=f.get("energy_source_id", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return f"energy_source_id={self.energy_source_id}"

@dataclass(kw_only=True)
class EnergyReservedEvent(EventBase):
    module: str = "energy"
    event_type: str = "EnergyReservedEvent"
    energy_source_id: str
    assembly_type_id: int
    energy_reserved: int
    total_reserved_energy: int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            energy_source_id=f.get("energy_source_id", ""),
            assembly_type_id=int(f.get("assembly_type_id", 0)),
            energy_reserved=int(f.get("energy_reserved", 0)),
            total_reserved_energy=int(f.get("total_reserved_energy", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"energy_source_id={self.energy_source_id} "
            f"assembly_type_id={self.assembly_type_id} "
            f"reserved={self.energy_reserved} "
            f"total_reserved={self.total_reserved_energy}"
        )


@dataclass(kw_only=True)
class EnergyReleasedEvent(EventBase):
    module: str = "energy"
    event_type: str = "EnergyReleasedEvent"
    energy_source_id: str
    assembly_type_id: int
    energy_released: int
    total_reserved_energy: int

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            energy_source_id=f.get("energy_source_id", ""),
            assembly_type_id=int(f.get("assembly_type_id", 0)),
            energy_released=int(f.get("energy_released", 0)),
            total_reserved_energy=int(f.get("total_reserved_energy", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"energy_source_id={self.energy_source_id} "
            f"assembly_type_id={self.assembly_type_id} "
            f"released={self.energy_released} "
            f"total_reserved={self.total_reserved_energy}"
        )

# ---- access ----------------------------------------------------------------

@dataclass(kw_only=True)
class OwnerCapCreatedEvent(EventBase):
    module: str = "access"
    event_type: str = "OwnerCapCreatedEvent"
    owner_cap_id: str
    authorized_object_id: str

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            owner_cap_id=f.get("owner_cap_id", ""),
            authorized_object_id=f.get("authorized_object_id", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"owner_cap_id={self.owner_cap_id} "
            f"authorized_object_id={self.authorized_object_id}"
        )


@dataclass(kw_only=True)
class OwnerCapTransferred(EventBase):
    module: str = "access"
    event_type: str = "OwnerCapTransferred"
    owner_cap_id: str
    authorized_object_id: str
    previous_owner: str
    owner: str


    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            owner_cap_id=f.get("owner_cap_id", ""),
            authorized_object_id=f.get("authorized_object_id", ""),
            previous_owner=f.get("previous_owner", ""),
            owner=f.get("owner", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )

    def to_str(self) -> str:
        return (
            f"owner_cap_id={self.owner_cap_id} "
            f"authorized_object_id={self.authorized_object_id} "
            f"from={self.previous_owner} -> to={self.owner}"
        )

# Maps  (module_name, struct_name)  →  parser callable

def _ext_parser(module: str):
    """Factory to create an ExtensionAuthorizedEvent parser bound to a module."""
    return lambda r: ExtensionAuthorizedEvent.from_rpc(r, module)


""" module_name, event_name -> Callable factory """
EVENT_REGISTRY: dict[tuple[str, str], Callable] = {
    # assembly.move
    ("assembly",     "AssemblyCreatedEvent"):     AssemblyCreatedEvent.from_rpc,
    ("assembly",     "OwnerCapCreatedEvent"):     OwnerCapCreatedEvent.from_rpc,
    ("assembly",     "StatusChangedEvent"):     StatusChangedEvent.from_rpc,
    ("assembly",     "MetadataChangedEvent"):     MetadataChangedEvent.from_rpc,
    ("assembly",     "EnergyReservedEvent"):     EnergyReservedEvent.from_rpc,
    ("assembly",     "EnergyReleasedEvent"):     EnergyReleasedEvent.from_rpc,
    # character.move
    ("character",    "CharacterCreatedEvent"):     CharacterCreatedEvent.from_rpc,
    ("character",    "OwnerCapCreatedEvent"):     OwnerCapCreatedEvent.from_rpc,
    ("character",    "MetadataChangedEvent"):     MetadataChangedEvent.from_rpc,
    # gate.move
    ("gate",         "GateCreatedEvent"):          GateCreatedEvent.from_rpc,
    ("gate",         "GateLinkedEvent"):           GateLinkedEvent.from_rpc,
    ("gate",         "GateUnlinkedEvent"):         GateUnlinkedEvent.from_rpc,
    ("gate",         "JumpEvent"):                 JumpEvent.from_rpc,
    ("gate",         "ExtensionAuthorizedEvent"):  _ext_parser("gate"),
    ("gate",         "StatusChangedEvent"): StatusChangedEvent.from_rpc,
    ("gate",         "MetadataChangedEvent"): MetadataChangedEvent.from_rpc,
    # killmail.move
    ("killmail",     "KillmailCreatedEvent"):      KillmailCreatedEvent.from_rpc,
    # storage_unit.move
    ("storage_unit", "StorageUnitCreatedEvent"):   StorageUnitCreatedEvent.from_rpc,
    ("storage_unit", "ExtensionAuthorizedEvent"):  _ext_parser("storage_unit"),
    ("storage_unit", "OwnerCapCreatedEvent"):   OwnerCapCreatedEvent.from_rpc,
    ("storage_unit", "StatusChangedEvent"):   StatusChangedEvent.from_rpc,
    ("storage_unit", "MetadataChangedEvent"):   MetadataChangedEvent.from_rpc,
    ("storage_unit", "ItemBurnedEvent"):   ItemBurnedEvent.from_rpc,
    ("storage_unit", "ItemMintedEvent"):   ItemMintedEvent.from_rpc,
    ("storage_unit", "EnergyReleasedEvent"):   EnergyReleasedEvent.from_rpc,
    ("storage_unit", "EnergyReservedEvent"):   EnergyReservedEvent.from_rpc,
    # turret.move
    ("turret",        "TurretCreatedEvent"):        TurretCreatedEvent.from_rpc,
    ("turret",        "PriorityListUpdatedEvent"):  PriorityListUpdatedEvent.from_rpc,
    ("turret",        "ExtensionAuthorizedEvent"):  _ext_parser("turret"),
    ("turret",        "StatusChangedEvent"):        StatusChangedEvent.from_rpc,
    ("turret",        "EnergyReservedEvent"):        EnergyReservedEvent.from_rpc,
    ("turret",        "EnergyReleasedEvent"):        EnergyReleasedEvent.from_rpc,
    ("turret",        "OwnerCapCreatedEvent"):        OwnerCapCreatedEvent.from_rpc,
    ("turret",        "MetadataChangedEvent"):        MetadataChangedEvent.from_rpc,
    # network_node.move
    ("network_node",  "NetworkNodeCreatedEvent"):   NetworkNodeCreatedEvent.from_rpc,
    ("network_node",  "FuelEvent"): FuelEvent.from_rpc,
    ("network_node",  "OwnerCapCreatedEvent"): OwnerCapCreatedEvent.from_rpc,
    ("network_node",  "StatusChangedEvent"): StatusChangedEvent.from_rpc,
    ("network_node",  "MetadataChangedEvent"): MetadataChangedEvent.from_rpc,
    ("network_node",  "StartEnergyProductionEvent"): StartEnergyProductionEvent.from_rpc,
    ("network_node",  "StopEnergyProductionEvent"): StopEnergyProductionEvent.from_rpc,
    # fuel.move
    ("fuel",          "FuelEvent"):                 FuelEvent.from_rpc,
    ("fuel",          "FuelEfficiencySetEvent"):    FuelEfficiencySetEvent.from_rpc,
    ("fuel",          "FuelEfficiencyRemovedEvent"):FuelEfficiencyRemovedEvent.from_rpc,
    # inventory.move
    ("inventory",     "ItemMintedEvent"):           ItemMintedEvent.from_rpc,
    ("inventory",     "ItemBurnedEvent"):           ItemBurnedEvent.from_rpc,
    ("inventory",     "ItemDepositedEvent"):        ItemDepositedEvent.from_rpc,
    ("inventory",     "ItemWithdrawnEvent"):        ItemWithdrawnEvent.from_rpc,
    ("inventory",     "ItemDestroyedEvent"):        ItemDestroyedEvent.from_rpc,
    # status.move
    ("status",        "StatusChangedEvent"):        StatusChangedEvent.from_rpc,
    # metadata.move
    ("metadata",      "MetadataChangedEvent"):      MetadataChangedEvent.from_rpc,

}