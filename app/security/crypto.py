import os
import hmac
import hashlib
from typing import Iterable, Optional, Dict, Type

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import event
from sqlalchemy.orm import Mapper

_FERNET: Optional[Fernet] = None

def _fernet() -> Fernet:
    global _FERNET
    if _FERNET is None:
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise RuntimeError("ENCRYPTION_KEY missing in environment")
        if isinstance(key, str):
            key = key.encode("utf-8")
        _FERNET = Fernet(key)
    return _FERNET

def encrypt(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and value.startswith("gAAAA"):
        return value
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        return value

def blind_index(value: Optional[str]) -> Optional[str]:
    """Index aveugle non réversible pour recherche/unique (égalité exacte).
       Normalise en lower + trim.
    """
    if value is None:
        return None
    secret = os.getenv("BLIND_INDEX_KEY")
    if not secret:
        raise RuntimeError("BLIND_INDEX_KEY missing in environment")
    normalized = value.strip().lower().encode("utf-8")
    return hmac.new(secret.encode("utf-8"), normalized, hashlib.sha256).hexdigest()

def register_encryption(
    model: Type,
    fields: Iterable[str],
    blind_index_map: Optional[Dict[str, str]] = None,
):
    """
    Branche le chiffrement transparent sur un modèle donné.
    - fields: noms d’attributs (colonnes) à chiffrer
    - blind_index_map: mapping { 'email': 'email_bidx', ... } pour conserver une recherche/unique
    """
    blind_index_map = blind_index_map or {}

    @event.listens_for(model, "before_insert")
    def _before_insert(mapper: Mapper, connection, target):
        for attr in fields:
            val = getattr(target, attr, None)
            setattr(target, attr, encrypt(val))
        for source_attr, bidx_attr in blind_index_map.items():
            setattr(target, bidx_attr, blind_index(getattr(target, source_attr, None)))

    @event.listens_for(model, "before_update")
    def _before_update(mapper: Mapper, connection, target):
        for attr in fields:
            val = getattr(target, attr, None)
            setattr(target, attr, encrypt(val))
        for source_attr, bidx_attr in blind_index_map.items():
            setattr(target, bidx_attr, blind_index(getattr(target, source_attr, None)))

    @event.listens_for(model, "load")
    def _after_load(target, context):
        for attr in fields:
            val = getattr(target, attr, None)
            setattr(target, attr, decrypt(val))
