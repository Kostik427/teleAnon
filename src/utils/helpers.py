import hashlib

def hash_user_id(user_id: int) -> str:
    return hashlib.sha256(str(user_id).encode()).hexdigest()

def generate_chat_id(user1: int, user2: int) -> int:
    return user1 * 1_000_000 + user2 if user1 < user2 else user2 * 1_000_000 + user1