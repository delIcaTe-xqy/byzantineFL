import copy

import torch
import torch.nn.functional as F
import torch.nn as nn
from torchvision.models import resnet18
import numpy as np
import random

from utils.test import test_img
from src.aggregation import fedavg


def euclid(v1, v2):
    diff = v1 - v2
    return torch.matmul(diff, diff.T)


def multi_vectorization(w_locals, args):
    vectors = copy.deepcopy(w_locals)

    for i, v in enumerate(vectors):
        for name in v:
            v[name] = v[name].reshape([-1]).to(args.device)
        vectors[i] = torch.cat(list(v.values()))

    return vectors


def single_vectorization(w_glob, args):
    vector = copy.deepcopy(w_glob)
    for name in vector:
        vector[name] = vector[name].reshape([-1]).to(args.device)

    return torch.cat(list(vector.values()))


def pairwise_distance(w_locals, args):
    vectors = multi_vectorization(w_locals, args)
    distance = torch.zeros([len(vectors), len(vectors)]).to(args.device)

    for i, v_i in enumerate(vectors):
        for j, v_j in enumerate(vectors[i:]):
            distance[i][j + i] = distance[j + i][i] = euclid(v_i, v_j)

    return distance


def _krum_create_distances(w_locals):
    distances = dict(dict)
    for i in range(len(w_locals)):
        for j in range(i):
            distances[i][j] = distances[j][i] = np.linalg.norm(w_locals[i] - w_locals[j])
    return distances


def medians(tensors, args):
    m, n = len(tensors), len(tensors[0])
    sort_degrees, _ = torch.sort(tensors, 0)
    if m % 2 == 1:
        med = copy.deepcopy(sort_degrees[m // 2])
    else:
        med = copy.deepcopy(sort_degrees[m // 2 - 1] + sort_degrees[m // 2]) / 2
    return med


def get_pe_weight(tensor1, tensor2):
    rho = torch.corrcoef(torch.stack((tensor1, tensor2), dim=0))[0][1]
    return max(0, np.log((1 + rho) / (1 - rho)) - 0.5)


def epp_distances(w_locals, med, args):
    distances = torch.zeros(len(w_locals)).to(args.device)
    for i, w_i in enumerate(w_locals):
        distances[i] = euclid(w_i, med)
    return distances


def reverse_sort_and_index(origin, args):
    target = torch.zeros(len(origin)).to(args.device)
    for index, enum_i in enumerate(origin):
        target[enum_i] = index
    return target


def get_eppCC(distance_table, mark_table, parts):
    if parts == 1:
        return 1
    rho = 1 - 6 * torch.sum(euclid(distance_table[0:parts], mark_table[0:parts])) / (parts ** 3 - parts)
    return rho


def get_epp_weight(distance_table, mark_table, parts, args):
    users_count = len(distance_table)
    weights = torch.zeros(users_count).to(args.device)
    shuffle_table = list(range(0, users_count))
    random.shuffle(shuffle_table)
    part_of_distance_table = torch.zeros(parts).to(args.device)
    part_of_mark_table = torch.zeros(parts).to(args.device)
    for i in range(0, users_count, parts):
        end = i + parts
        if end > users_count:
            end = users_count
        for j in range(end - i):
            index = shuffle_table[i + j]
            part_of_distance_table[j] = distance_table[index]
            part_of_mark_table[j] = mark_table[index]
        _, dt = torch.sort(part_of_distance_table[0:end - i])
        _, mt = torch.sort(part_of_mark_table[0:end - i])
        part_of_distance_table = reverse_sort_and_index(dt, args)
        part_of_mark_table = reverse_sort_and_index(mt, args)
        rho = get_eppCC(part_of_distance_table, part_of_mark_table, end - i)
        for j in range(end - i):
            index = shuffle_table[i + j]
            mark_table[index] = max(0, mark_table[index] + 0.1 * rho)
            weights[index] = mark_table[index]

    return weights


def krum(w_locals, corrupted_count, args, distance=None):
    n = len(w_locals) - corrupted_count

    if distance is None:
        distance = pairwise_distance(w_locals, args)
    sorted_idx = distance.sum(dim=0).argsort()[: n]

    chosen_idx = int(sorted_idx[0])

    return copy.deepcopy(w_locals[chosen_idx]), chosen_idx


def trimmed_mean(w_locals, corrupted_count, args):
    n = len(w_locals) - 2 * corrupted_count

    distance = pairwise_distance(w_locals, args)

    distance = distance.sum(dim=1)
    med = distance.median()
    _, chosen = torch.sort(abs(distance - med))
    chosen = chosen[: n]

    return fedavg([copy.deepcopy(w_locals[int(i)]) for i in chosen])


def fang(w_locals, dataset_val, corrupted_count, args):
    loss_impact = {}
    net_a = resnet18(num_classes=args.num_classes)
    net_b = copy.deepcopy(net_a)

    for i in range(len(w_locals)):
        tmp_w_locals = copy.deepcopy(w_locals)
        w_a = trimmed_mean(tmp_w_locals, corrupted_count, args)
        tmp_w_locals.pop(i)
        w_b = trimmed_mean(tmp_w_locals, corrupted_count, args)

        net_a.load_state_dict(w_a)
        net_b.load_state_dict(w_b)

        _, loss_a = test_img(net_a.to(args.device), dataset_val, args)
        _, loss_b = test_img(net_b.to(args.device), dataset_val, args)

        loss_impact.update({i: loss_a - loss_b})

    sorted_loss_impact = sorted(loss_impact.items(), key=lambda item: item[1])
    filterd_clients = [sorted_loss_impact[i][0] for i in range(len(w_locals) - corrupted_count)]

    return fedavg([copy.deepcopy(w_locals[i]) for i in filterd_clients])


def bulyan(w_locals, corrupted_count, args):
    users_count = len(w_locals)
    assert users_count >= 4 * corrupted_count + 3
    set_size = users_count - 2 * corrupted_count
    selection_set = []

    distances = pairwise_distance(w_locals, args)
    while len(selection_set) < set_size:
        _, currently_selected = krum(w_locals, corrupted_count, args, distances)
        selection_set.append(w_locals[currently_selected])

        # remove the selected from next iterations:
        distances = distances[torch.arange(distances.size(0)) != currently_selected]
        distances = torch.einsum('ij->ji', [distances])
        distances = distances[torch.arange(distances.size(0)) != currently_selected]
        distances = torch.einsum('ij->ji', [distances])

    return trimmed_mean(np.array(selection_set), corrupted_count, args)


def pefl(w_locals, args):
    users_count = len(w_locals)
    vectors = multi_vectorization(w_locals, args)
    tensors = torch.tensor([item.cpu().detach().numpy() for item in vectors]).to(args.device)
    med = medians(tensors, args)
    weights = torch.zeros(users_count).to(args.device)
    for i in range(users_count):
        weights[i] = get_pe_weight(med, tensors[i])

    return fedavg(w_locals, weights)


def eppfl(w_locals, mark_table, args):
    parts = 4
    users_count = len(w_locals)
    vectors = multi_vectorization(w_locals, args)
    tensors = torch.tensor([item.cpu().detach().numpy() for item in vectors]).to(args.device)
    med = medians(tensors, args)
    distance = epp_distances(tensors, med, args)
    _, dis_indices = torch.sort(distance, -1, True)
    distance_table = reverse_sort_and_index(dis_indices, args)
    if sum(mark_table) == 0:
        start, end = 0.499, 0.501
        step = (end - start) / users_count
        for i in range(users_count):
            mark_table[dis_indices[i]] = start + i * step
    weights = get_epp_weight(distance_table, mark_table, parts, args)

    return fedavg(w_locals, weights)


def triplet_distance(w_locals, global_net, args):
    score = torch.zeros([args.num_clients, args.num_clients]).to(args.device)
    dummy_data = torch.empty(args.ds, 3, 28, 28).uniform_(0, 1).to(args.device)
    net1 = resnet18(num_classes=args.num_classes).to(args.device)
    net2 = copy.deepcopy(net1).to(args.device)
    import ipdb
    ipdb.set_trace()
    anchor = nn.Sequential(*list(global_net.children())[:-1])(dummy_data).squeeze()

    for i, w_i in enumerate(w_locals):
        net1.load_state_dict(w_i)
        pro1 = nn.Sequential(*list(net1.children())[:-1])(dummy_data).squeeze()
        for j, w_j in enumerate(w_locals[i:]):
            net2.load_state_dict(w_j)
            pro2 = nn.Sequential(*list(net2.children())[:-1])(dummy_data).squeeze()

            score[i][j + i] = score[j + i][i] = F.binary_cross_entropy_with_logits(pro1,
                                                                                   anchor) + F.binary_cross_entropy_with_logits(
                pro2, anchor)

    return score


def dummy_contrastive_aggregation(w_locals, c, global_net, args):
    n = len(w_locals) - c

    score = triplet_distance(copy.deepcopy(w_locals), global_net, args)

    sorted_idx = score.sum(dim=0).argsort()[: n]

    return fedavg([copy.deepcopy(w_locals[int(i)]) for i in sorted_idx])
