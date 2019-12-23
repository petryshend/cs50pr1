import os
import hashlib
import binascii

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from params import DATABASE_URL
from user import User


class UserService:
    SALT_LENGTH = 64
    HASH_ITERATIONS = 100000

    def __init__(self):
        engine = create_engine(os.getenv(DATABASE_URL))
        self.db = scoped_session(sessionmaker(bind=engine))

    def get_by_email(self, email: str) -> bool:
        query = 'SELECT user_id, email, password FROM users WHERE email = :email'
        res = self.db.execute(query, {'email': email})
        row = res.fetchone()
        if not row:
            return None
        user = User(row['email'], row['password'])
        user.id = row['user_id']
        return user

    def insert(self, user: User) -> User:
        query = """
        INSERT INTO users (email, password)
        VALUES (:email, :password)
        RETURNING user_id
        """
        hashed = self.hash_password(user.password)
        res = self.db.execute(query, {'email': user.email, 'password': hashed})
        user.id = res.first()[0]
        self.db.commit()
        return user

    def hash_password(self, password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                      salt, self.HASH_ITERATIONS)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def verify_password(self, stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:self.SALT_LENGTH]
        stored_password = stored_password[self.SALT_LENGTH:]
        pwdhash = hashlib.pbkdf2_hmac('sha512',
                                      provided_password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      self.HASH_ITERATIONS)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password
