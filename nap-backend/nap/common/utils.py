import bcrypt


def hashpw(content: str):
    return bcrypt.hashpw(content.encode(), bcrypt.gensalt())
