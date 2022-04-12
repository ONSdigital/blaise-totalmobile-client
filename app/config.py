import os
from dataclasses import dataclass


@dataclass
class Config:
    user: str
    password_hash: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            user=os.getenv("TOTALMOBILE_USER", ""),
            password_hash=os.getenv("TOTALMOBILE_PASSWORD_HASH", ""),
        )
