"""Deterministic, immutable resolution packets for a future private runtime.

No football distribution is invented here. The caller must supply a calibrated
distribution from the shared football kernel, which is not implemented yet.
Never expose packet contents, weights, seeds or private journal data to a coach.
"""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
from typing import Protocol


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


@dataclass(frozen=True)
class Packet:
    event_id: str
    procedure_version: str
    payload: bytes = field(repr=False)

    @classmethod
    def freeze(cls, event_id, procedure_version, *, snapshot, inputs, modifiers, weights):
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError('A canonical event ID is required')
        if not isinstance(procedure_version, str) or not procedure_version.strip():
            raise ValueError('A procedure version is required')
        if not snapshot or not isinstance(snapshot, str):
            raise ValueError('A frozen source-snapshot reference is required')
        if not weights or any(not isinstance(k, str) or not k for k in weights):
            raise ValueError('Outcome names are required')
        if any(type(v) is not int or v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
            raise ValueError('Weights must be nonnegative integers with positive total')
        divisor = math.gcd(*weights.values())
        normalized = {k: v//divisor for k, v in sorted(weights.items())}
        if sum(normalized.values()).bit_length() > 256:
            raise ValueError('Distribution exceeds supported integer range')
        body = dict(event_id=event_id, procedure_version=procedure_version,
                    snapshot=snapshot, inputs=inputs, modifiers=modifiers, weights=normalized)
        return cls(event_id, procedure_version, canonical(body))

    @property
    def digest(self):
        return hashlib.sha256(self.payload).hexdigest()


class PrivateJournal(Protocol):
    """A production adapter must enforce durable, atomic, access-isolated writes.

    freeze_once atomically persists and closes the packet before returning.
    An existing event returns its original bytes, including after a restart.
    close_result is idempotent and refuses a different result for that event.
    Caller assertions or a local ignored directory do not satisfy this contract.
    """
    def freeze_once(self, event_id: str, payload: bytes) -> bytes: ...
    def close_result(self, event_id: str, packet_digest: str, outcome: str) -> str: ...


class PacketConflict(ValueError):
    pass


def resolve(packet: Packet, career_seed: bytes, journal: PrivateJournal) -> str:
    """Resolve only after packet closure. This is not a game-facing entry point."""
    if not isinstance(career_seed, bytes) or len(career_seed) < 32:
        raise ValueError('A securely generated, privately persisted career seed is required')
    body = json.loads(packet.payload)
    # Verify bytes rather than trusting direct construction of the frozen dataclass.
    rebuilt = Packet.freeze(body['event_id'], body['procedure_version'],
                            snapshot=body['snapshot'], inputs=body['inputs'],
                            modifiers=body['modifiers'], weights=body['weights'])
    if rebuilt != packet:
        raise ValueError('Packet is not in canonical form')
    seed_context = canonical([packet.event_id, packet.procedure_version])
    event_seed = hmac.new(career_seed, seed_context, hashlib.sha256).digest()
    # The derived seed is part of the private frozen journal envelope. A changed
    # career seed cannot choose a new result after an interrupted first attempt.
    envelope = canonical(dict(packet=body, event_seed=event_seed.hex()))
    if journal.freeze_once(packet.event_id, envelope) != envelope:
        raise PacketConflict('Event is already frozen with different inputs or seed')
    weights = body['weights']
    total = sum(weights.values())
    # Rejection sampling avoids modulo bias; counter is deterministic, not discretionary.
    byte_count = (total.bit_length() + 7)//8
    if byte_count > 32:
        raise ValueError('Distribution exceeds supported integer range')
    universe = 1 << (8*byte_count)
    limit = universe - universe % total
    counter = 0
    while True:
        digest = hmac.new(event_seed, canonical(['draw', counter]), hashlib.sha256).digest()
        draw = int.from_bytes(digest[:byte_count], 'big')
        if draw < limit:
            draw %= total
            break
        counter += 1
    for outcome, weight in sorted(weights.items()):
        if draw < weight:
            stored = journal.close_result(packet.event_id, hashlib.sha256(envelope).hexdigest(), outcome)
            if stored != outcome:
                raise PacketConflict('Stored result conflicts with deterministic replay')
            return outcome
        draw -= weight
    raise AssertionError('Distribution exhausted')
