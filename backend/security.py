import bcrypt

def hash(password):
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return str(hashed, 'utf-8')
    except Exception as e:
        return e

def match_passwords(password, hash):
    if bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8')):
        return True
    return False