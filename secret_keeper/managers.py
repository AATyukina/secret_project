from django.db import models

from hashlib import sha512
from uuid import uuid4
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class SecretManager(models.Manager):
    def create_secret(self, user_access_key: str, secret: str) -> None:
        """
        Creates a new row for the secret.
        params:
            user_access_key - a new key generated for the user access to the secret;
            secret - not encoded str - an actual secret user entered;
        raises:
            Exception if constrains are not satisfied

        Steps:
            1) UUID generated;
            2) UUID encodes to create a key to symmetric encryption of the secret;
            3) Secret encrypts using key;
            4) Hash access key;
            4) Saving data to the database;
        """
        uuid = self._generate_uuid()
        encrypted_secret = self._encrypt_secret(uuid, secret)
        hashed_access_key = self._hash_access_key(user_access_key)
        self.create(
            uuid=uuid,
            secret=encrypted_secret,
            access_key=hashed_access_key
        )

    def return_secret(self, user_access_key: str) -> str:
        """
        Returns a secret for the user_access_key
        params:
            user_access_key - a key generated user passed;
        raises:
            NotSecretFoundException

        Steps:
            1) Hash user_access_key;
            2) Get row for user_access_key;
            3) UUID encodes to create a key to symmetric encryption of the secret;
            4) Secret decrypts using key;
            5) Return decrypted secret;
        """
        hashed_access_key = self._hash_access_key(user_access_key)
        try:
            secret_row = self.get(access_key=hashed_access_key)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise NotSecretFoundException("Incorrect secret or multiple secrets found!")
        decrypted_secret = self._decrypt_secret(secret_row.uuid, secret_row.secret)
        return decrypted_secret

    # helper methods
    @staticmethod
    def _generate_uuid() -> str:
        return uuid4().hex

    def _encrypt_secret(self, uuid: str, secret: str) -> str:
        key = self._generate_key(bytes(uuid, "utf8"))
        enc_message = Fernet(key).encrypt(secret.encode())
        return enc_message.decode()

    def _decrypt_secret(self, uuid: str, secret: str) -> str:
        key = self._generate_key(bytes(uuid, "utf8"))
        decrypt_message = Fernet(key).decrypt(secret.encode()).decode()
        return decrypt_message

    @staticmethod
    def _generate_key(uuid: bytes) -> bytes:
        """Returns 32 url-safe base64-encoded bytes generated based on uuid"""
        return urlsafe_b64encode(uuid)

    @staticmethod
    def _hash_access_key(access_key: str) -> str:
        return sha512(bytes(access_key, "utf8")).hexdigest()


class NotSecretFoundException(Exception):
    pass
