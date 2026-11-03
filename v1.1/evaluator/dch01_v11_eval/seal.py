"""Secret seeds, commitments and evaluator-only storage.

The code of this package is public. What the agent must not know is the seed of a
sealed run, because seed plus code rebuilds every answer. A commitment is the
SHA-256 fingerprint of the seed and of the gold, written before any agent runs, so
that anyone can later check the answer key was fixed in advance.
"""
from __future__ import annotations
import hashlib,json,os,secrets
from pathlib import Path

SEED_BITS=128


def new_seed()->int:
    # 128 random bits: far too many to guess by trying seeds against the record ids in a view.
    return secrets.randbits(SEED_BITS)


def sha256_bytes(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def seed_commitment(seed:int)->str:
    return sha256_bytes(f'dch01-v11-seed:{seed}'.encode())


def gold_commitment(seed:int,gold_bytes:bytes)->str:
    return sha256_bytes(f'dch01-v11-gold:{seed}:'.encode()+gold_bytes)


def jsonl_bytes(items)->bytes:
    return b''.join((json.dumps(x,sort_keys=True)+'\n').encode() for x in items)


def make_private_dir(base:Path,name:str)->Path:
    """Create a directory only its owner (the evaluator account) can enter."""
    base=Path(base);base.mkdir(parents=True,exist_ok=True)
    os.chmod(base,0o700)  # even the names of past runs are not the agent's business
    path=base/name
    path.mkdir(mode=0o700)
    os.chmod(path,0o700)  # mkdir mode is filtered by umask; set it explicitly
    return path


def write_private(path:Path,data:bytes):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data)


def commitment_record(seed:int,gold_bytes:bytes,views_bytes:bytes,sealed:bool)->dict:
    return {'protocol':'1.1-draft','sealed':sealed,
            'seed_commitment_sha256':seed_commitment(seed),
            # Salted with the seed: without the seed, nobody can test guesses about gold against this hash.
            'evaluator_gold_commitment_sha256':gold_commitment(seed,gold_bytes),
            'agent_views_sha256':sha256_bytes(views_bytes),
            'how_to_check':'After the seed is revealed, sha256 of the text dch01-v11-seed:<seed> must equal seed_commitment_sha256, '
                           'and sha256 of dch01-v11-gold:<seed>: followed by the bytes of gold.jsonl must equal evaluator_gold_commitment_sha256.'}
