import copy

import torch


def fedavg(w_locals, weights=None):
    w_avg = copy.deepcopy(w_locals[0])
    # 权重相同
    if weights is None:
        with torch.no_grad():
            for k in w_avg.keys():
                for i in range(1, len(w_locals)):
                    w_avg[k] += w_locals[i][k]
                w_avg[k] = torch.true_divide(w_avg[k], len(w_locals))
    # 权重不同
    else:
        sum_weight = sum(weights)
        with torch.no_grad():
            for k in w_avg.keys():
                w_avg[k] = 0.0
                for i in range(len(w_locals)):
                    w_avg[k] += w_locals[i][k] * weights[i]
                w_avg[k] = torch.true_divide(w_avg[k], sum_weight)

    return w_avg
