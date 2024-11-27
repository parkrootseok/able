from src.domain.block.schemas import Block
from src.common.utils.response.schemas import ImmutableBaseModel

class CanvasBlock(Block):
    id: str
    position: str

class Edge(ImmutableBaseModel):
    id: str
    source: str
    target: str

class Canvas(ImmutableBaseModel):
    blocks: list[CanvasBlock] = []
    edges: list[Edge] = []

class GetCanvasResponse(ImmutableBaseModel):
    canvas: Canvas

class SaveCanvasRequest(ImmutableBaseModel):
    canvas: Canvas
    thumbnail: str