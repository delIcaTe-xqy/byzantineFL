该项目为刘智远师兄论文eppfl方案的实验在原项目Security-Preserving Federated Learning via Byzantine-Sensitive Triplet Distance基础上的实验版本。包括以下几篇论文的复现：
Communication-Efficient Learning of Deep Networks from Decentralized Data ([McMahan, Brendan, et al. AISTATS 2017](https://proceedings.mlr.press/v54/mcmahan17a/mcmahan17a.pdf))
Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent ([Blanchard, Peva, et al. NIPS 2017](https://proceedings.neurips.cc/paper/2017/file/f4b9ec30ad9f68f89b29639786cb62ef-Paper.pdf))

Byzantine-Robust Distributed Learning: Towards Optimal Statistical Rates ([Yin, Dong, et al. ICML 2018](https://proceedings.mlr.press/v80/yin18a))

 Local Model Poisoning Attacks to Byzantine-Robust Federated Learning  ([Fang, Minghong, et al. USENIX 2020](https://arxiv.org/abs/1911.11815))

 The Hidden Vulnerability of Distributed Learning in Byzantium ([El Mahdi El Mhamdi, et al.](https://proceedings.mlr.press/v80/mhamdi18a/mhamdi18a.pdf))

 PEFL: A Privacy-Enhanced Federated Learning Scheme for Big Data Analytics ([Jiale Zhang, et al.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9014272))


# Security-Preserving Federated Learning via Byzantine-Sensitive Triplet Distance

This is an official implementation of the following paper:
> Youngjoon Lee, Sangwoo Park, and Joonhyuk Kang.
**[Security-Preserving Federated Learning via Byzantine-Sensitive Triplet Distance](https://arxiv.org/abs/2210.16519)**  
_submitted in ICASSP 2023_.

## Requirements
The implementation runs on

```bash docker.sh```

Additionally, please install the required packages as below

```pip install tensorboard medmnist```

## Byzantine attacks
This paper considers the following poisoning attacks
- Targeted model poisoning ([Bhagoji, Arjun Nitin, et al. ICML 2019](https://arxiv.org/abs/1811.12470)): Targeted model poisoning attack for federated learning
- MPAF ([Xiaoyu Cao, Neil Zhenqiang Gong. CVPR Workshop 2022](https://arxiv.org/abs/2203.08669)): Untargeted model poisoning attack for federated learning

## Byzantine-Robust Aggregation Techniques
This paper considers the following Byzantine-Robust aggregation techniques
- Vanilla ([McMahan, Brendan, et al. AISTATS 2017](https://proceedings.mlr.press/v54/mcmahan17a/mcmahan17a.pdf))
- Krum ([Blanchard, Peva, et al. NIPS 2017](https://proceedings.neurips.cc/paper/2017/file/f4b9ec30ad9f68f89b29639786cb62ef-Paper.pdf))
- Trimmed-mean ([Yin, Dong, et al. ICML 2018](https://proceedings.mlr.press/v80/yin18a))
- Fang ([Fang, Minghong, et al. USENIX 2020](https://arxiv.org/abs/1911.11815))
- Bulyan （[El Mahdi El Mhamdi, et al.](https://proceedings.mlr.press/v80/mhamdi18a/mhamdi18a.pdf)）
- PEFL ([Jiale Zhang, et al.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9014272))

## Dataset
- Blood cell classification dataset ([Andrea Acevedo, Anna Merino, et al. Data in Brief 2020](https://www.sciencedirect.com/science/article/pii/S2352340920303681))

## Experiments
Without Byzantine attacks experiment runs on

```bash execute/run0.sh```

Impact of Byzantine percentage runs on

```bash execute/run1.sh```

Impact of non-iid degree runs on

```bash execute/run2.sh```

## Acknowledgements
Referred http://doi.org/10.5281/zenodo.4321561
