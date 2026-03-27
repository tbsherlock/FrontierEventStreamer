import logging
from typing import Optional

import src.events as events
from src.scanner import WorldScanner
from dataclasses import dataclass
from typing import Self

from src.events import EventBase, KillmailCreatedEvent


@dataclass(kw_only=True)
class EnrichedKillmailCreatedEvent(KillmailCreatedEvent):
    module: str = "enriched"
    event_type: str = "EnrichedKillmailCreatedEvent"
    killer_name: str
    victim_name: str
    reported_by_name: str
    solar_system_name: str

    @classmethod
    def from_rpc(cls, r: dict) -> Self:
        raise Exception("not implemented")

    def to_str(self) -> str:
        return (
            f"killer={self.killer_name} "
            f"victim={self.victim_name} "
            f"loss_type={self.loss_type.value} "
            f"solar_system={self.solar_system_name} "
            f"reported_by={self.reported_by_name}"
        )


item_db = dict()  # Key is assembly_key 'TenantItemId(item_id=2112000056, tenant='utopia')'


async def scan_chain(scanner:WorldScanner) -> None:
    logging.info("Enricher begin chain scanner")
    all_events = await scanner.scan_module(module="character")
    for event in all_events:
        update_item_db(event)
    logging.info("Enricher completed chain scanner")


def update_item_db(evt: events.EventBase) -> None:
    match evt:
        case events.CharacterCreatedEvent():
            #print("CharacterCreatedEvent: ", evt)
            data_key = evt.key
            data_entry = item_db.get(data_key, {})
            data_entry['character_id'] = evt.character_id
            data_entry['key'] = evt.key
            data_entry['tribe_id'] = evt.tribe_id
            data_entry['character_address'] = evt.tribe_id
            item_db[data_key] = data_entry
        case events.MetadataChangedEvent():
            #print("MetadataChangedEvent: ", evt)
            data_key = evt.assembly_key
            data_entry = item_db.get(data_key, {})
            data_entry['name'] = evt.name
            data_entry['description'] = evt.description
            data_entry['url'] = evt.url
            item_db[data_key] = data_entry
        case _:
            pass


def enrich_event(evt: events.EventBase) -> Optional[events.EventBase]:
    match evt:
        case events.KillmailCreatedEvent():
            revt = EnrichedKillmailCreatedEvent(
                key=evt.key,
                killer_id=evt.killer_id,
                victim_id=evt.victim_id,
                reported_by_character_id=evt.reported_by_character_id,
                loss_type=evt.loss_type,
                kill_timestamp=evt.kill_timestamp,
                solar_system_id=evt.solar_system_id,
                killer_name=item_db.get(evt.killer_id, "UNKNOWN"),
                victim_name=item_db.get(evt.victim_id, "UNKNOWN"),
                reported_by_name=item_db.get(evt.reported_by_character_id, "UNKNOWN"),
                solar_system_name=item_db.get(evt.solar_system_id, "UNKNOWN"),

            )
            print("enhanced KillmailCreatedEvent: ", revt)
            return revt

    return None
