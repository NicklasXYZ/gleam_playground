from typing import Union
from fastapi import HTTPException
import json
import os

def get_secret(seret_name: str) -> str:
    secret = None
    # Read kubernetes secrets from the default directory secrets directory
    # mounted by OpenFaaS
    # TODO: Error handling... In case a certain secret is not present...
    with open(f"/var/openfaas/secrets/{seret_name}") as f:
        secret = f.read()
    return secret


def check_api_key(x_api_key: str, api_key: Union[None, str]) -> None:
    # Check the API key if it is present and thus required
    if api_key:
        if x_api_key != api_key:
            raise HTTPException(
                status_code = 401,
                detail = 'Unauthorized. Wrong API key.',
            )


def load_cors(PATH: Union[None, str] = None) -> dict:
    if PATH is None:
        PATH = './common/cors_config.json'
    data = {}
    try: 
        with open(PATH) as f:
            data = json.loads(f.read())
        return data
    except FileNotFoundError:
        pass
    return data


def str_to_bool_or_none(s: str) -> Union[None, bool]:
    """ Convert a string to a boolean value.
    Args:
        s (str): A string.

    Returns:
        (bool or None): True if the string has boolean value True. False if the string
            has boolean value False. Otherwise None.  
    """
    s = s.strip() # Strip whitespace
    if s.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif s.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        return None