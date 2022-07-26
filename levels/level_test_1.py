import numpy as np
from Utils import LevelInfo, Obstacle


def level():
    ## 定义关卡配置
    level_info = LevelInfo()

    ## 所兼容的最低bouncing版本
    level_info.bouncing_version = 0.6

    ## 关卡基本信息
    level_info.level_name = '测试关 test1'
    level_info.level_description = '单球中心引力场运动，环形障碍物'

    ## 区域
    level_info.rect_w = 12  # 矩形区域宽度
    level_info.rect_h = 12  # 矩形区域高度

    ## 障碍
    # 以单元格__左下角__为标志，标记出障碍单元格
    # 坐标平面为0索引，左下角单元格为(0,0)
    # x坐标，y坐标，硬度
    level_info.obstacle = []
    ii = np.array([3, 2, 1, 0, -1, -2, -2, -1, 0, 1, 2, 3]) + np.floor(level_info.rect_w / 2)
    jj = np.array([1, 2, 3, 3, 2, 1, 0, -1, -2, -2, -1, 0]) + np.floor(level_info.rect_h / 2)
    for kk in range(len(ii)):
        level_info.obstacle.append(Obstacle(ii[kk], jj[kk], 3))

    ## 质点
    level_info.pos_0 = np.array([level_info.rect_w / 2, level_info.rect_h / 8])  # 质点位置初值
    va_0 = np.pi / 6  # 质点速度方向初值(rad)
    vm_0 = 2  # 质点速度大小初值
    level_info.v_0 = vm_0 * np.array([np.cos(va_0), np.sin(va_0)])

    ## 加速度场
    def gravity(pos: np.array((1, 2))) -> np.array:
        # 以区域中心为中心的引力场
        # 大小为m / r ^ 2
        center = np.array([level_info.rect_w / 2, level_info.rect_h / 2])
        R = 0.5  # 引力源半径
        m = 25  # 引力源质量

        r = pos - center
        distance = np.linalg.norm(r, 2)
        g_vector = -r / distance
        if distance > R:
            g_mag = m / (distance * distance)
        else:
            g_mag = distance * m / (R ** 3)
        g = g_mag * g_vector
        return g

    level_info.acc = gravity

    ## 时间
    level_info.t_start = 0  # 起始时间(一般都是0)
    level_info.t_stop = 10  # 停止时间

    ##
    return level_info


if __name__ == "__main__":
    tmp_level = level()
    a=11