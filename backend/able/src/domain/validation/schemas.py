from src.domain.canvas.schemas import Edge
from src.common.utils.response.schemas import ImmutableBaseModel

class ValidateCanvasRequest(ImmutableBaseModel):
    blocks: list[int]
    edges: list[Edge]

class ValidateCanvasResponse(ImmutableBaseModel):
    has_cycle: bool
    cycle_blocks: list[int] | None