import json

from django.core.cache import cache
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes
from web3.utils.datastructures import AttributeDict


def get_event_abi(abi, event_name):
    """Helper function that extracts the event abi from the given abi.

    Args:
        abi (dict): the contract abi
        event_name (str): the event name

    Returns:
        dict: the event specific abi
    """
    for entry in abi:
        if 'name' in entry.keys() and entry['name'] == event_name and \
                entry['type'] == "event":
            return entry
    raise ValueError(
        'Event `{}` not found in the contract abi'.format(event_name))


def event_topic_from_contract_abi(abi, event_name):
    if isinstance(abi, str):
        abi = json.loads(abi)

    event_abi = get_event_abi(abi, event_name)
    event_topic = event_abi_to_log_topic(event_abi)
    return event_topic.hex()


def refresh_cache_update_value(update_required=False):
    from .models import CACHE_UPDATE_KEY
    cache.set(CACHE_UPDATE_KEY, update_required)


class Singleton(type):
    """Simple singleton implementation."""

    _instances = {}

    def __call__(cls, *args, **kwargs):  # noqa: N805
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        elif isinstance(obj, AttributeDict):
            return dict(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8').rstrip('\u0000')
        return super().default(obj)
