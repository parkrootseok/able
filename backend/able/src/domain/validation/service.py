from collections import defaultdict, deque
from typing import Tuple
from src.domain.canvas.schemas import Edge


def check_cycle(blocks: list[int], edges: list[Edge]) -> Tuple[bool, list[int]]:
    adj_blocks = defaultdict(list)
    in_degree = defaultdict(int)

    for edge in edges:
        adj_blocks[edge.source].append(edge.target)
        in_degree[edge.target] += 1

    queue = deque([block for block in blocks if in_degree[block] == 0])
    visited_count = 0

    while queue:
        node = queue.popleft()
        visited_count += 1
        for adj_block in adj_blocks.pop(node, []):
            in_degree[adj_block] -= 1
            if in_degree[adj_block] == 0:
                queue.append(adj_block)

    if visited_count != len(blocks):
        cycle_blocks = [block for block in blocks if in_degree[block] > 0]
        return True, cycle_blocks

    return False, []