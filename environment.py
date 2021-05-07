import numpy as np
import random
import copy

from configuration import *

cal_data_amount = lambda flow_cost, resolution: flow_cost / resolution
# cal_tran_time = lambda data_amount, band_width, propagation_daley:  data_amount/band_width + propagation_daley
cal_compute_time = lambda data_amout, power: data_amout / power


class Env(object):
    def __init__(self, flows_set, networks_set, controllers_set):
        self.flows_set = flows_set.copy()
        self.networks_set = networks_set.copy()
        self.controllers_set = controllers_set.copy()

        self.flows, self.controllers, self.remain_flows_index = [], [], []
        self.f_i = 0
        self.init()

    def init(self):
        # initialize
        i = random.randint(0, len(self.flows_set) - 1)
        self.flows, self.controllers = self.flows_set[i], self.controllers_set[i].copy()
        self.remain_flows_index = list(range(CONSIDER_TASKS - 1, len(self.flows)))

        self.f_i = 0
        flow_inf = np.array([self.flows[0], self.flows[0], self.flows[0]])
        return [flow_inf, self.controllers]

    def get_consider_flows(self):
        if self.f_i == len(self.flows): return None
        if self.f_i == 0: return np.array([self.flows[0], self.flows[0], self.flows[0]])
        if self.f_i == 1: return np.array([self.flows[0], self.flows[1], self.flows[1]])
        return np.array([self.flows[self.f_i - 2], self.flows[self.f_i - 1], self.flows[self.f_i]])  # CONSIDER_FLOWS =3

    @staticmethod
    def cal_accuracy(resolution):
        best_resolution = 120
        noise = np.random.uniform(0.01, 0.1)
        return 0.85 * (resolution / best_resolution) + noise

    @staticmethod
    def state2info(s, a):
        flow_cost = s[FLOW][-1][FLOW_COST]
        controller_index = a[TARGET_CONTROLLER]
        power, storage = s[CONTROLLER][a[TARGET_CONTROLLER]][COMPUTING_POWER], s[CONTROLLER][a[TARGET_CONTROLLER]][
            STORAGE]
        # bandwidth, delay =
        resolution = RESOLUTIONS[a[RESOLUTION]]
        return flow_cost, power, storage, resolution

    @staticmethod
    def cal_reward(s, a):
        [flow_cost, power, storage, resolution] = Env.state2info(s, a)
        data_amount = cal_data_amount(flow_cost, resolution)
        calcul_time = cal_compute_time(data_amount, power)
        times = calcul_time
        accuracy = Env.cal_accuracy(resolution)

        alpha = 0.7
        beta = 1 - alpha
        reward = alpha * ((flow_cost - times) / flow_cost) + beta * ((accuracy - accuracy_demand) / accuracy_demand)
        if times < flow_cost and accuracy > accuracy_demand: reward += 1
        if reward < -5:
            print(reward)
        return reward, [times, flow_cost, accuracy, accuracy_demand]
