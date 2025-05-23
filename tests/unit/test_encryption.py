import os
import pytest

pytest.importorskip("cryptography")

from src.backup.encryption import BackupEncryption


@pytest.fixture
def tmp_file(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("secret")
    return file_path


def test_encrypt_and_decrypt(tmp_file, tmp_path):
    enc = BackupEncryption(key_path=tmp_path / "key.key")
    encrypted_path = enc.encrypt_backup(str(tmp_file))
    assert os.path.exists(encrypted_path)

    output = tmp_path / "output.txt"
    enc.decrypt_backup(encrypted_path, str(output))
    assert output.read_text() == "secret"
