"""
Run PyTorch Soft Actor Critic on HalfCheetahEnv.

NOTE: You need PyTorch 0.3 or more (to have torch.distributions)
"""
import numpy as np
import random
import gym
import rlkit.rltorch.pytorch_util as ptu
from rlkit.envs.wrappers import NormalizedBoxEnv
from rlkit.launchers.launcher_util import setup_logger
from rlkit.rltorch.sac.policies import TanhGaussianPolicy
from rlkit.rltorch.sac.virel import Virel
from rlkit.rltorch.networks import FlattenMlp
import sys


def experiment(variant):
    env = NormalizedBoxEnv(gym.make(variant['env']))
    obs_dim = int(np.prod(env.observation_space.shape))
    action_dim = int(np.prod(env.action_space.shape))

    net_size = variant['net_size']
    qf = FlattenMlp(
        hidden_sizes=[net_size, net_size],
        input_size=obs_dim + action_dim,
        output_size=1,
    )
    vf = FlattenMlp(
        hidden_sizes=[net_size, net_size],
        input_size=obs_dim,
        output_size=1,
    )
    policy = TanhGaussianPolicy(
        hidden_sizes=[net_size, net_size],
        obs_dim=obs_dim,
        action_dim=action_dim,
    )
    algorithm = Virel(
        env=env,
        policy=policy,
        qf=qf,
        vf=vf,
        **variant['algo_params']
    )
    algorithm.to(ptu.device)
    algorithm.train()

if __name__ == "__main__":
    variant = dict(
        algo_params=dict(
            num_epochs=int(sys.argv[2]),
            num_steps_per_epoch=1000,
            num_steps_per_eval=1000,
            batch_size=128,
            max_path_length=999,
            discount=0.99,
            reward_scale=float(sys.argv[3]),

            soft_target_tau=0.001,
            policy_lr=3E-4,
            qf_lr=3E-4,
            vf_lr=3E-4,
        ),
        net_size=300,
        env=sys.argv[1],
        algo_name="virel",
        algo_seed=int(sys.argv[5]),
    )
    seed=int(sys.argv[5])
    random.seed(seed)
    np.random.seed(seed)
    name = "virel_" + "_" + sys.argv[1] + "_" + sys.argv[5] + "_" + sys.argv[3] + "_" + sys.argv[6]
    setup_logger(name, variant=variant)
    ptu.set_gpu_mode(True)
    experiment(variant)
