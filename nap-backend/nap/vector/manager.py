from nap.common.conf import CONF
from nap.vector.drivers.chromadb import ChromadbDriver


def get_vector_driver():
    if CONF.vector.driver == "chromadb":
        return ChromadbDriver()

    raise Exception(f"{CONF.vector.driver} is not supported")
