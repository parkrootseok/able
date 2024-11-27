from typing import Any
from src.domain.block.enums import BlockType, ArgType
from src.common.utils.response.schemas import ImmutableBaseModel

class Arg(ImmutableBaseModel):
    name: str
    value: Any
    type: ArgType
    is_required: bool

class Block(ImmutableBaseModel):
    name: str
    type: BlockType
    args: list[Arg]

class BlockResponse(ImmutableBaseModel):
    block: Block

class BlocksResponse(ImmutableBaseModel):
    blocks: list[Block]