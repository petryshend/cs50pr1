import os
import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from user import User

from pprint import pprint

class UserService:
    SALT_LENGTH = 32
    HASH_ITERATIONS = 100000

    def __init__(self):
        engine = create_engine(os.getenv("DATABASE_URL"))
        self.db = scoped_session(sessionmaker(bind=engine))

    def user_exists(self, user: User):
        query = 'SELECT FROM users WHERE email = :email'
        res = self.db.execute(query, {'email': user.email})
        return res.rowcount > 0

    def insert(self, user: User) -> User:
        query = """
        INSERT INTO users (email, password, salt)
        VALUES (:email, :password, :salt)
        RETURNING id
        """
        encoded, salt = self.encode(user.password)
        res = self.db.execute(query, {'email': user.email, 'password': encoded, 'salt': salt})
        user.id = res.first()[0]
        self.db.commit()
        return user

    def encode(self, password: str):
        salt = os.urandom(self.SALT_LENGTH)
        encoded = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            self.HASH_ITERATIONS
        )

        return (encoded.hex(), salt.hex())

    def verify(self, password, encoded, salt) -> bool:

        new_encoded = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode(),
            self.HASH_ITERATIONS
        )


        pprint(salt.encode())
        pprint(encoded)
        pprint(new_encoded.hex())

        return encoded == new_encoded.hex()
