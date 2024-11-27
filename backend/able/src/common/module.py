import torch
import torch.nn as nn

class TensorConcatenator(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, *args, dim = 0) -> torch.Tensor:
        return torch.cat(args, dim=dim)

class TensorAdder(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, *args):
        result = 0
        for arg in args:
            result += arg
        return result

class TensorStacker(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, *args, dim = 0) -> torch.Tensor:
        return torch.stack(args, dim=dim)

class TensorMatrixMultiplier(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, t1, t2) -> torch.Tensor:
        return torch.matmul(t1, t2)