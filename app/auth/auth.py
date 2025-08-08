import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

# -------------------- PASSWORD HASH----------

def hash_password(plain_password: str) -> str:
    """
    Hash un mot de passe en texte clair à l'aide de bcrypt.

    Args:
        plain_password (str): Le mot de passe en texte clair à hasher.

    Returns:
        str: Le mot de passe hashé sous forme de chaîne de caractères.
    """
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe en texte clair correspond au mot de passe hashé.

    Args:
        plain_password (str): Le mot de passe en texte clair à vérifier.
        hashed_password (str): Le mot de passe hashé à comparer.

    Returns:
        bool: True si le mot de passe en texte clair correspond au hash, sinon False.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# -------------------- JWT Token --------------------


def create_token(user_id: int) -> str:
    """
    Crée un token JWT pour un utilisateur donné.

    Args:
        user_id (int): L'ID de l'utilisateur pour lequel générer le token.

    Returns:
        str: Le token JWT généré.
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str):
    """
    Décode un token JWT et retourne l'ID de l'utilisateur.

    Args:
        token (str): Le token JWT à décoder.

    Returns:
        int | None: L'ID de l'utilisateur si le token est valide, sinon None.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_token(token: str) -> dict:
    """
    Vérifie la validité d'un token JWT. Si valide, retourne l'ID de l'utilisateur.

    Args:
        token (str): Le token JWT à vérifier.

    Raises:
        jwt.ExpiredSignatureError: Si le token a expiré.
        jwt.InvalidTokenError: Si le token est invalide.

    Returns:
        int: L'ID de l'utilisateur si le token est valide.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Le token a expiré.")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Token invalide.")
