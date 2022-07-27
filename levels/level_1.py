# -*- coding: utf-8 -*-
import numpy as np
from Utils import LevelInfo, Obstacle


def level():
    ## 定义关卡配置
    level_info = LevelInfo()

    ## 所兼容的最低bouncing版本
    level_info.bouncing_version = 0.7

    ## 关卡基本信息
    level_info.level_name = 'Level 1'
    level_info.level_description = '单球，金字塔，游戏，微弱重力'

    ## 区域
    level_info.rect_w = 10  # 矩形区域宽度
    level_info.rect_h = 8  # 矩形区域高度

    ## 障碍
    # 以单元格__左下角__为标志，标记出障碍单元格
    # 坐标平面为0索引，左下角单元格为(0,0)
    # x坐标，y坐标，硬度
    level_info.obstacle = []
    for i in range(4):
        y = i + 4
        for x in range(i+1, 9-i):
            level_info.obstacle.append(Obstacle(x, y, 2))

    ## 质点
    level_info.pos_0 = []
    level_info.v_0 = []
    for i in range(1):
        level_info.pos_0.append(np.array([level_info.rect_w / 2, 0.01]))  # 质点位置初值
        va_0 = np.pi / 3  # 质点速度方向初值(rad)
        vm_0 = 1  # 质点速度大小初值
        level_info.v_0.append(vm_0 * np.array([np.cos(va_0), np.sin(va_0)]))

    ## 加速度场
    def gravity(pos: np.array) -> np.array:
        # 微弱重力场
        return np.array([0, -0.1])

    level_info.acc = gravity

    ## 时间
    level_info.t_start = 0  # 起始时间(一般都是0)
    level_info.t_stop = 100  # 停止时间

    ##
    return level_info


if __name__ == "__main__":
    tmp_level = level()
