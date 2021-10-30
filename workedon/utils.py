import hashlib
import uuid


def get_unique_hash():
    unique_id = str(uuid.uuid4()).encode('utf-8')
    return hashlib.sha1(unique_id).hexdigest()
