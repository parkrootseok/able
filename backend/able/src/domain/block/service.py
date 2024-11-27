import logging

from src.domain.block.enums import BlockType
from src.domain.block.exceptions import BlockNotFoundException
from src.domain.block.schemas import Block
from src.common.utils.logger.utils import get_logger
from src.common.utils.file.utils import get_file, get_directory
from src.common.utils.file.path_manager import PathManager
from src.common.utils import str_to_json

logger = get_logger(__name__, level=logging.DEBUG)
path_manager = PathManager()

def find_blocks_by_type(block_type: BlockType) -> list[Block]:

    block_type_dir_path = path_manager.get_block_path(block_type)
    logger.info(f"Searching for blocks of type '{block_type.value}' in {block_type_dir_path}")

    blocks_path = get_directory(block_type_dir_path)
    # if not blocks_path:
    #     raise BlockNotFoundException(f"No blocks found in directory for type '{block_type.value}'")

    blocks = []
    for block_path in blocks_path:

        if block_path.suffix != ".json":
            logger.warning(f"Skipping non-JSON file: {block_path}")
            continue

        logger.debug(f"Checking path: {block_path}")
        data = get_file(block_path)
        blocks.append(Block(**str_to_json(data)))

    return blocks

def search(keyword: str) -> Block:

    types_dir = get_directory(path_manager.blocks_path)

    for type_dir in types_dir:
        blocks_path = get_directory(type_dir)

        if type_dir.name == "data":
            continue

        for block_path in blocks_path:
            logger.debug(f"Checking path: {block_path}")
            if block_path.name == f"{keyword}.json":
                block_data = get_file(block_path)
                return Block(**str_to_json(block_data))

    raise BlockNotFoundException(keyword)