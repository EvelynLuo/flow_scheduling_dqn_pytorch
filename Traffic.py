import numpy as np

from configuration import *


class Traffic:
    def __init__(self, nodes_num):
        self.nodes_num = nodes_num

    def exp_traffic(self):
        # get the random samples of exponential distribution and return the samples of numpy array.
        a = np.random.exponential(scale=100, size=self.nodes_num)
        b = np.random.exponential(scale=100, size=self.nodes_num)

        T = np.outer(a, b)

        np.fill_diagonal(T, -1)

        # 算力值范围最小0.1 泊松分布
        T[T != -1] = np.asarray(np.random.exponential() * T[T != -1] / np.average(T[T != -1])).clip(min=0.1, max=5.0)

        # print(T)

        flow = []
        index = 0
        for i in range(T.shape[0]):
            for j in range(T[i].shape[0]):
                if T[i][j] != -1:
                    index += 1
                    flow.append(T[i][j])

        return flow


if __name__ == "__main__":
    tt = Traffic(TASKS_NUM)
    t = tt.exp_traffic()
    print(t)

    flows = np.load(r'data\flows.npy')
