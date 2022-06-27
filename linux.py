import os
import config
from hashlib import sha1


def hash_string(string: str) -> str:
    return sha1(string.encode()).hexdigest()


def auth(user: str, password: str) -> bool:
    if user not in config.USERS:
        return False

    if config.USERS[user] != hash_string(password):
        return False

    return True


def get_files(path: str) -> dict:
    files = {}

    for file in sorted(os.listdir(path), key=lambda f: os.path.isfile(f'{path}/{f}')):
        key = file if os.path.isfile(f'{path}/{file}') else f'📁 {file}'
        files[key] = f'{config.PROTOCOL}://{config.DOMAIN}/linux{path}/{file}'

    return files


def parse_path(path: str) -> tuple[str, str]:
    return f'/{path}', f"/{'/'.join(path.split('/')[:-1])}"
