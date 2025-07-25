import logging
from dotenv import load_dotenv

from stables.utils.logging import setup_logging
from stables.data import load_yield_pool
from stables.config import local_pg_config

logger = logging.getLogger(__name__)
setup_logging()
load_dotenv()
from stables.config import ybs_tokens


def llama_ybs():

    pg_config = local_pg_config
    for key, value in ybs_tokens.items():
        # print(key, value["defillama_pool_id"])
        load_yield_pool(
            pool_id=value["defillama_pool_id"],
            pool_name=key,
            pg_config=pg_config,
        )


if __name__ == "__main__":
    llama_ybs()
