from Traffic import *


def gen_batch_traffic(tasks_num):
    count = 0
    flow = []
    for i in range(4):
        tt = Traffic(tasks_num)
        t = tt.exp_traffic()
        for x in range(len(t)):
            flow.append(t[x])
    return flow


def gen_flow_info(num):
    flow = gen_batch_traffic(num)
    return flow


def gen_controller_info(c_num, c_range=[50, 120], s_range=[50, 100]):
    # computing_power = RESOLUTIONS
    computing_power = np.random.uniform(c_range[0], c_range[1], size=c_num).astype(np.int)
    storage = np.random.uniform(s_range[0], s_range[1], size=c_num).astype(np.int)
    # storage = [60, 60, 50, 50]
    controller = [list(c) for c in zip(computing_power, storage)]
    return controller


def gen_network_info2(flow, controllers_set, controllers_num, batch_num):
    set1, set2 = [], []

    for i in range(batch_num):
        for cn in range(controllers_num):
            wait, fc_ac, count, st_use, wait_ac = 0, 0, 0, 0, 0
            band_width = []
            wait_time = []
            start = datetime.datetime.now()
            for fc in range(len(flow[i])):
                if (fc_ac + flow[i][fc]) <= controllers_set[i][cn][COMPUTING_POWER]:
                    # 如果顺序读到累计和未达到最高算力 说明一次并发未到达
                    fc_ac += flow[i][fc]
                    # sum += flows[i][fc]
                    count += 1
                else:
                    never_full = False
                    # 执行一次并发 记录当前最高条数
                    band_width.append(count)
                    count = 0
                    fc_ac = 0
                    # 把当前来临的加入等待队列
                    start = datetime.datetime.now()
                    while fc < len(flow[i]):
                        if (wait_ac + flow[i][fc]) > controllers_set[i][cn][STORAGE]:
                            break
                        # 并发加入等待
                        wait_ac += flow[i][fc]
                        fc += 1
                    # 并发加入等待结束，假设执行已经结束
                    end = datetime.datetime.now()
                    wait = (end - start).microseconds
                    wait_time.append(wait)
                    wait_ac = 0

            sum1, sum2 = 0, 0
            if len(band_width) == 0 and len(wait_time) == 0:
                bandwidth = count
                wait = 0.0
            elif len(band_width) == 0:
                bandwidth = count
            elif len(wait_time) == 0:
                wait = 0.0
            else:
                for b in range(0, len(band_width)):
                    sum1 += band_width[b]
                for w in range(0, len(wait_time)):
                    sum2 += wait_time[0]
                bandwidth = sum1 / len(band_width)
                wait = sum2 / len(wait_time)
            set1.append([bandwidth, wait])
        set2.append(set1)
        set1 = []
    return set2


'''
def gen_network_info(tasks_num, edges_num, bw_range=[10, 30], p_range=[0.1, 0.5]):
    networks = []
    for i in range(tasks_num):
        band_width = np.random.uniform(bw_range[0], bw_range[1], size=edges_num).astype(np.float32)
        propagation_delay = np.random.uniform(p_range[0], p_range[1], size=edges_num).astype(np.float32)
        networks.append([list(t) for t in zip(band_width, propagation_delay)])
    return networks
Matrix:
state[FLOW][flow_index] [FLOW_COST]
     [SDN_NETWORK][controller_index] [BAND_WIDTH | PROPAGATION_DELAY]
     [CONTROLLER] [controller_index] [COMPUTING_POWER | STORAGE]
action[RESOLUTION |TARGET_CONTROLLER ] = [re_index, controller_index]

'''

if __name__ == "__main__":
    tasks_num, controllers_num = TASKS_NUM, CONTROLLERS_NUM
    batch_num = 4000
    # 4000次批量。360个包一毫秒。
    flows = [gen_flow_info(tasks_num) for i in range(batch_num)]
    controllers = [gen_controller_info(CONTROLLERS_NUM) for i in range(batch_num)]
    networks = gen_network_info2(flows, controllers, controllers_num, batch_num)
    print(flows)
    print(controllers)
    print(networks)

    np.save(r'data\flows.npy', np.array(flows))
    np.save(r'data\controllers.npy', np.array(controllers))
    np.save(r'data\networks.npy', np.array(networks))

    flows = np.load(r'data\flows.npy')
    controllers = np.load(r'data\controllers.npy')
    networks = np.load(r'data\networks.npy')

    print("Complete generate data !")

    # print("Networks:", networks.shape)
    print("Flows:", flows.shape)
    print("Controllers:", controllers.shape)

    for i in range(batch_num):
        for cn in range(controllers_num):
            print("ctrl[", cn, "][COMPUTING_POWER][STORAGE]:", controllers[i][cn][COMPUTING_POWER],
                  controllers[i][cn][STORAGE])
            print("nets[", cn, "][BAND_WIDTH][PROPGT_DELAY]:", networks[i][cn][BAND_WIDTH],
                  networks[i][cn][PROPAGATION_DELAY])
            for fc in range(len(flows[i])):
                if (fc % 100) == 0:
                    print("flow[", i, "][", fc, "]: ", flows[i][fc])
