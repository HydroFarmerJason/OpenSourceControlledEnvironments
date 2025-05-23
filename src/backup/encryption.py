"""Backup encryption utilities."""
from __future__ import annotations

import os
from typing import Optional

try:
    from cryptography.fernet import Fernet
except ImportError:  # pragma: no cover - handle missing dependency
    Fernet = None


class BackupEncryption:
    """Encrypt and decrypt backup files using Fernet."""

    def __init__(self, key_path: str = "backup.key") -> None:
        self.key_path = key_path
        self.key = self._load_or_generate_key()
        self.cipher: Optional[Fernet] = Fernet(self.key) if Fernet else None

    def _load_or_generate_key(self) -> bytes:
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                return f.read()
        if Fernet is None:
            raise RuntimeError("cryptography library is required for encryption")
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as f:
            f.write(key)
        return key

    def encrypt_backup(self, backup_path: str) -> str:
        if self.cipher is None:
            raise RuntimeError("Encryption unavailable: cryptography not installed")
        with open(backup_path, "rb") as file:
            encrypted = self.cipher.encrypt(file.read())
        enc_path = f"{backup_path}.enc"
        with open(enc_path, "wb") as file:
            file.write(encrypted)
        os.remove(backup_path)
        return enc_path

    def decrypt_backup(self, encrypted_path: str, output_path: str) -> str:
        if self.cipher is None:
            raise RuntimeError("Decryption unavailable: cryptography not installed")
        with open(encrypted_path, "rb") as file:
            decrypted = self.cipher.decrypt(file.read())
        with open(output_path, "wb") as file:
            file.write(decrypted)
        return output_path
