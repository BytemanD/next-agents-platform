from nap.common.conf import CONF
from nap.storage.drivers.fs import FSDriver


def get_storage_driver():
    if CONF.storage.driver == "fs":
        return FSDriver()

    raise Exception(f"storage {CONF.storage.driver} is not supported")
