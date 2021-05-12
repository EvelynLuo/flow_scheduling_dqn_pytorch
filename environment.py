import numpy as np
import random
import copy

from configuration import *

cal_data_amount = lambda power, resolution: resolution * power
cal_tran_time = lambda data_amount, band_width, propagation_daley: data_amount / band_width + propagation_daley
cal_compute_time = lambda data_amout, power: data_amout / power


class Env(object):
    def __init__(self, flows_set, networks_set, controllers_set):
        self.flows_set = flows_set.copy()  # flows[flow_index][FLOW_COST]
        self.networks_set = networks_set.copy()  # networks[controller_index][BAND_WIDTH | PROPAGATION_DELAY]
        self.controllers_set = controllers_set.copy()  # controllers[controller_index][COMPUTING_POWER | STORAGE]

        self.flows, self.networks, self.controllers, self.remain_tasks_index = [], [], [], []
        self.t_i = 0
        self.init()

    def init(self):
        # initialize
        i = random.randint(0, len(self.flows_set) - 1)
        self.flows, self.controllers, self.networks = self.flows_set[i], self.controllers_set[i].copy(), \
                                                      self.networks_set[i].copy()
        self.remain_flows_index = list(range(CONSIDER_TASKS - 1, len(self.flows)))

        self.t_i = 0
        flow_inf = np.array([self.flows[0], self.flows[0], self.flows[0]])
        return [flow_inf, self.networks[self.t_i], self.controllers]

    def get_consider_flows(self):
        if self.t_i == len(self.flows): return None
        if self.t_i == 0: return np.array([self.flows[0], self.flows[0], self.flows[0]])
        if self.t_i == 1: return np.array([self.flows[0], self.flows[1], self.flows[1]])
        return np.array([self.flows[self.t_i - 2], self.flows[self.t_i - 1], self.flows[self.t_i]])  # CONSIDER_FLOWS =3

    @staticmethod
    def cal_accuracy(power, resolution):
        best_pr, best_resolution = 120, 120
        noise = np.random.uniform(0.01, 0.1)
        return 0.25 * (power / best_pr) + 0.6 * (resolution / best_resolution) + noise

    @staticmethod
    def state2info(s, a):
        flow_cost = s[FLOW][-1][FLOW_COST]
        controller_index = a[TARGET_CONTROLLER]
        power, storage = s[CONTROLLER][a[TARGET_CONTROLLER]][COMPUTING_POWER], s[CONTROLLER][a[TARGET_CONTROLLER]][
            STORAGE]
        bandwidth, delay = s[NETWORK][controller_index][BAND_WIDTH], s[NETWORK][controller_index][PROPAGATION_DELAY]
        resolution = RESOLUTIONS[a[RESOLUTION]]
        return flow_cost, power, storage, bandwidth, delay, resolution

    @staticmethod
    def cal_reward(s, a):
        [flow_cost, power, storage, bandwidth, delay, resolution] = Env.state2info(s, a)
        data_amount = cal_data_amount(power, resolution)
        tran_time = cal_tran_time(data_amount, bandwidth, delay)
        calcul_time = cal_compute_time(data_amount, power)
        times = tran_time + calcul_time
        accuracy = Env.cal_accuracy(resolution)

        alpha = 0.7
        beta = 1 - alpha
        reward = alpha * ((flow_cost - times) / flow_cost) + beta * ((accuracy - power) / power)
        if times < flow_cost and accuracy > power: reward += 1
        if reward < -5:
            print(reward)
        return reward, [times, flow_cost, accuracy, power]

    def step(self, s, a, is_update=True):
        [flow_cost, power, storage, bandwidth, delay, resolution] = Env.state2info(s, a)
        reward, [times, flow_cost, accuracy, power] = Env.cal_reward(s, a)

        # if update env to get next_state in rl
        if is_update:
            # nor_use_bw = nor(bit_rate, self.max_n[BAND_WIDTH], self.min_n[BAND_WIDTH])
            for n in self.networks:
                for d in n:
                    d[BAND_WIDTH] -= power
                    if d[BAND_WIDTH] < 0:
                        d[BAND_WIDTH] = 0.01
            # choose next_task from remain unprocessed task
            self.t_i += 1
            if self.t_i == len(self.tasks):
                return [], reward, True, [times, flow_cost, accuracy, power]
            next_task = self.get_consider_tasks()
            next_state = [next_task, self.networks[self.t_i], self.controllers]
            return next_state, reward, False, [times, flow_cost, accuracy, power]
        else:
            return reward, [times, flow_cost, accuracy, power]

    @staticmethod
    def intrinsic_reward(s, g, a):
        #
        [flow_cost, power, storage, bandwidth, delay, resolution] = Env.state2info(s, a)
        data_amount = cal_data_amount(power, resolution)
        tran_time = cal_tran_time(data_amount, bandwidth, delay)
        calcul_time = cal_compute_time(data_amount, power)
        times = tran_time + calcul_time
        accuracy = Env.cal_accuracy(resolution)

        alpha = 0.8
        beta = 1 - alpha
        reward = alpha * ((flow_cost - times) / flow_cost) + beta * ((accuracy - power) / power)
        return reward


if __name__ == "__main__":
    flows = np.load(r'data\flows.npy')
    controllers = np.load(r'data\controllers.npy')
    networks = np.load(r'data\networks.npy')
    env = Env(flows, networks, controllers)
