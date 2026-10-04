"""Public A-C owner schedule and honest deterministic seed metadata; no I/O."""
from __future__ import annotations
import re
from a4_protocol_reference import owner_and_seed

VERSION = 'm1-public-owner-interface-v1'
MAP_VERSION = 'm1-blind-noise-template-v1'
A4_OWNERS = tuple(f'thesis:owner:{i:02d}' for i in range(16))


def validate_seed_metadata(decimal, hexadecimal):
    if (type(decimal) is not str or not re.fullmatch(r'0|[1-9][0-9]*', decimal)
            or type(hexadecimal) is not str or not re.fullmatch(r'[0-9a-f]{16}', hexadecimal)):
        raise ValueError('Canonical exact uint64 decimal/hex strings required')
    value = int(decimal)
    if not 0 <= value < 2**64 or value != int(hexadecimal, 16):
        raise ValueError('Uint64 seed overflow or representations disagree')
    return value


def source_schedule(source_uid):
    owner, wrong, seed = owner_and_seed(source_uid)
    result = dict(owner_interface_version=VERSION, map_version=MAP_VERSION,
                  owner=owner, wrong_owner=wrong,
                  seed_uint64_decimal=str(seed), seed_uint64_hex=f'{seed:016x}',
                  schedule_seed_role='metadata_only_not_consumed_by_ac_e2e',
                  scientific_embedding_seed=None, execution_phase_seed=0,
                  execution_rng_policy='fresh_phase_zero_resume_restores_saved_rng')
    validate_seed_metadata(result['seed_uint64_decimal'], result['seed_uint64_hex'])
    return result


def invoke_deterministic_embed(embed, source, source_uid, frozen_configuration):
    """Schedule uint64 stays in receipts; method has no stochastic seed input."""
    schedule = source_schedule(source_uid)
    output = embed(source, schedule['owner'], frozen_configuration)
    return output, schedule
