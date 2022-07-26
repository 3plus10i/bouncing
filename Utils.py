# 为 bouncing 提供基础工具支持
# from ver.0.7

import numpy as np


# 关卡信息
class LevelInfo:
    def __init__(self):
        self.level_name = ''
        self.level_description = ''
        self.obstacle: list[Obstacle] = []
        self.bouncing_version = 0
        self.rect_w = 0
        self.rect_h = 0
        self.pos_0 = None
        self.v_0 = None
        self.acc = None  # Callable
        self.t_start = 0
        self.t_stop = 0
        self.level_name: str
        self.level_description: str


# 状态信息数据结构
# 只描述一个时刻的状态
class State:
    def __init__(self):
        self.hit_index = -1  # 谁被撞了
        self.land = False  # 是否落地
        self.pause = False  # 中断位置更新，需要处理其他任务


# 图形，只负责描述界面配置
class Graph:
    def __init__(self):
        self.fig = None
        self.fig_size = (6, 6)
        self.ax = None


# 质点的显示参数
class Ball:
    def __init__(self):
        self.head: Head = Head()
        self.tail: Tail = Tail()
        self.pos = np.zeros(2)
        self.v = np.zeros(2)


# 头
class Head:
    def __init__(self):
        self.marker = 'o'
        self.color = [0.33, 0.67, 0.93]
        self.size = 5
        self.handle = None


# 尾巴
class Tail:
    def __init__(self):
        self._max_len = 10
        self._data = np.zeros((self._max_len, 2))
        self.real_len = 0
        # self.data
        self.color = [0.3, 0.3, 0.3]
        self.linewidth = 1
        self.linestyle = '-'
        self.handle = None

    @property
    def data(self) -> np.ndarray:
        return self._data[0:self.real_len, :]

    @property
    def max_len(self):
        return self._max_len

    @max_len.setter
    def max_len(self, m: int):
        if self.real_len > 0:
            print('一个尾巴的数据被抛弃了！')
        self._max_len = m
        self.real_len = 0
        self._data = np.zeros((self.max_len, 2))

    def append_data(self, data):
        if self.real_len < self._max_len:
            self._data[self.real_len, :] = data
            self.real_len += 1
        else:
            self._data[0:(self.max_len - 1), :] = self._data[1:self.max_len, :]
            self._data[self.max_len - 1, :] = data


# 障碍物
class Obstacle:
    def __init__(self, x=0, y=0, hard=1, rgb: list[3] = None):
        self.x: int = x  # 这里不是int的话会导致很多麻烦
        self.y: int = y
        self.hard: int = hard
        self._init_hard = float(hard)
        if rgb is None:
            rgb = [0., 0., 0.]
        self.rgb = rgb  # default == 'k'
        self.handle = None

    # 根据硬度获取透明度
    @property
    def alpha(self):
        return self.hard / self._init_hard if self.hard >= 0 else 0.0

    # 根据rgb颜色和透明度获取Color
    @property
    def color(self):
        return self.rgb + [self.alpha]

    # 返回障碍物所在的cell
    # 亦可作为快速索引的key使用
    @property
    def cell(self):
        ret = (self.x, self.y)
        return ret

    # 判断给定障碍物是否与当前障碍物毗邻
    def is_adjoin(self, ob):
        dx = abs((self.x - ob.x))
        dy = abs((self.y - ob.y))
        if dx + dy == 1:
            return True
        else:
            return False
