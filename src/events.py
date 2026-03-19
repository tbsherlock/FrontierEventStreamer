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
            for key in raw:
                return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


@dataclass
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

# ---- assembly --------------------------------------------------------------

@dataclass
class AssemblyCreatedEvent:
    assembly_id:    str
    assembly_key:   TenantItemId
    owner_cap_id:   str
    type_id:        int
    # envelope
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- character -------------------------------------------------------------

@dataclass
class CharacterCreatedEvent:
    character_id:      str
    key:               TenantItemId
    tribe_id:          int
    character_address: str
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- gate ------------------------------------------------------------------

@dataclass
class GateCreatedEvent:
    assembly_id:   str
    assembly_key:  TenantItemId
    owner_cap_id:  str
    type_id:       int
    location_hash: str
    status:        Any
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            assembly_id  = f.get("assembly_id", ""),
            assembly_key = TenantItemId.from_rpc(f.get("assembly_key", {})),
            owner_cap_id = f.get("owner_cap_id", ""),
            type_id      = int(f.get("type_id", 0)),
            location_hash= str(f.get("location_hash", "")),
            status       = f.get("status"),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


@dataclass
class GateLinkedEvent:
    source_gate_id:        str
    source_gate_key:       TenantItemId
    destination_gate_id:   str
    destination_gate_key:  TenantItemId
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class GateUnlinkedEvent:
    source_gate_id: str
    source_gate_key: TenantItemId
    destination_gate_id:   str
    destination_gate_key:  TenantItemId
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class JumpEvent:
    source_gate_id:        str
    source_gate_key:       TenantItemId
    destination_gate_id:   str
    destination_gate_key:  TenantItemId
    character_id:          str
    character_key:         TenantItemId
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class ExtensionAuthorizedEvent:
    """Shared by gate, storage_unit and turret modules."""
    module:             str          # which module emitted this
    assembly_id:        str
    assembly_key:       TenantItemId
    extension_type:     Any
    previous_extension: Any
    owner_cap_id:       str
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- killmail --------------------------------------------------------------

@dataclass
class KillmailCreatedEvent:
    key:                      TenantItemId
    killer_id:                TenantItemId
    victim_id:                TenantItemId
    reported_by_character_id: TenantItemId
    loss_type:                LossType
    kill_timestamp:           int
    solar_system_id:          TenantItemId
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- storage_unit ----------------------------------------------------------

@dataclass
class StorageUnitCreatedEvent:
    storage_unit_id: str
    assembly_key:    TenantItemId
    owner_cap_id:    str
    type_id:         int
    max_capacity:    int
    location_hash:   str
    status:          Any
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- turret ----------------------------------------------------------------

@dataclass
class TurretCreatedEvent:
    turret_id:    str
    turret_key:   TenantItemId
    owner_cap_id: str
    type_id:      int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class PriorityListUpdatedEvent:
    turret_id:     str
    priority_list: list   # raw list of TargetCandidate dicts
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            turret_id     = f.get("turret_id", ""),
            priority_list = f.get("priority_list", []),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


# ---- network_node ----------------------------------------------------------

@dataclass
class NetworkNodeCreatedEvent:
    network_node_id:       str
    assembly_key:          TenantItemId
    owner_cap_id:          str
    type_id:               int
    fuel_max_capacity:     int
    fuel_burn_rate_in_ms:  int
    max_energy_production: int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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
            for key in raw:
                return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


@dataclass
class FuelEvent:
    assembly_id:  str
    assembly_key: TenantItemId
    type_id:      int
    old_quantity: int
    new_quantity: int
    is_burning:   bool
    action:       FuelAction
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class FuelEfficiencySetEvent:
    fuel_type_id: int
    efficiency:   int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            fuel_type_id = int(f.get("fuel_type_id", 0)),
            efficiency   = int(f.get("efficiency", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


@dataclass
class FuelEfficiencyRemovedEvent:
    fuel_type_id: int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            fuel_type_id = int(f.get("fuel_type_id", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


# ---- inventory -------------------------------------------------------------

@dataclass
class ItemMintedEvent:
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class ItemBurnedEvent:
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class ItemDepositedEvent:
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class ItemWithdrawnEvent:
    assembly_id:   str
    assembly_key:  TenantItemId
    character_id:  str
    character_key: TenantItemId
    item_id:       int
    type_id:       int
    quantity:      int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


@dataclass
class ItemDestroyedEvent:
    assembly_id:  str
    assembly_key: TenantItemId
    item_id:      int
    type_id:      int
    quantity:     int
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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
            for key in raw:
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
            for key in raw:
                return cls[key] if key in cls._member_map_ else cls.UNKNOWN
        return cls.UNKNOWN


@dataclass
class StatusChangedEvent:
    assembly_id:  str
    assembly_key: TenantItemId
    status:       AssemblyStatusValue
    action:       StatusAction
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- metadata --------------------------------------------------------------

@dataclass
class MetadataChangedEvent:
    assembly_id:  str
    assembly_key: TenantItemId
    name:         str
    description:  str
    url:          str
    tx_digest: str = ""; checkpoint: int = 0; emitted_at: Optional[datetime] = None

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


# ---- energy ----------------------------------------------------------------

@dataclass
class StartEnergyProductionEvent:
    energy_source_id: str
    current_energy_production: int
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            energy_source_id=f.get("energy_source_id", ""),
            current_energy_production=int(f.get("current_energy_production", 0)),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


@dataclass
class StopEnergyProductionEvent:
    energy_source_id: str
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            energy_source_id=f.get("energy_source_id", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


@dataclass
class EnergyReservedEvent:
    energy_source_id: str
    assembly_type_id: int
    energy_reserved: int
    total_reserved_energy: int
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

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


@dataclass
class EnergyReleasedEvent:
    energy_source_id: str
    assembly_type_id: int
    energy_released: int
    total_reserved_energy: int
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

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


# ---- access ----------------------------------------------------------------

@dataclass
class OwnerCapCreatedEvent:
    owner_cap_id: str
    authorized_object_id: str
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        f = r.get("parsedJson", {})
        return cls(
            owner_cap_id=f.get("owner_cap_id", ""),
            authorized_object_id=f.get("authorized_object_id", ""),
            tx_digest=_tx(r), checkpoint=_cp(r), emitted_at=_ts(r),
        )


@dataclass
class OwnerCapTransferred:
    owner_cap_id: str
    authorized_object_id: str
    previous_owner: str
    owner: str
    tx_digest: str = ""
    checkpoint: int = 0
    emitted_at: Optional[datetime] = None

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