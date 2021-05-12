# 四个SDN控制器,六个HOSTS
CONTROLLERS_NUM, TASKS_NUM = 4, 10

# Lambda
LAMBDA = 1 / (CONTROLLERS_NUM * 100)
MAX_EPISODES = 2000

# 1个控制器的平均算力是100K的吞吐量，平均1毫秒处理100条
RESOLUTIONS = [100, 120, 80, 50]
CONSIDER_TASKS, RESOLUTION_TYPE = 3, 4

LR = 0.001  # learning rate
DISCOUNT = 0.9  # reward discount
TARGET_REPLACE_ITER = 100  # target update frequency
BATCH_SIZE = 20
MEMORY_SIZE = 5000  # ER memory size

'''
Matrix:
state[FLOW][flow_index] [FLOW_COST]
     [NETWORK][controller_index] [BAND_WIDTH | PROPAGATION_DELAY]
     [CONTROLLER][controller_index] [COMPUTING_POWER | STORAGE]
action[RESOLUTION |TARGET_CONTROLLER ] = [re_index, controller_index]
'''
# to confirm the matrix
FLOW, NETWORK, CONTROLLER = 0, 1, 2
# 流的算力代价
FLOW_COST = 0
# 带宽：算力占比fc/cp 时延=发送时延+传播时延+处理时延+排队时延
BAND_WIDTH, PROPAGATION_DELAY = 0, 1
# 控制器的算力 控制器等待队列的空间
COMPUTING_POWER, STORAGE = 0, 1
# 选择的控制器，目标（存疑）
RESOLUTION, TARGET_CONTROLLER = 0, 1
