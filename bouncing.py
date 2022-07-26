# 反弹球
# 2022年7月26日

# TODO
#   封装 done
#   非同步渲染（垂直同步） done
#   颜色管理 done
#   多球 done
#   关闭窗口即终止程序 done
#   射击 on dev
#   用路径检查实现碰撞判定
#       不见得就更好，应该详细分析穿越的问题
#   按钮：开始，暂停，结束
#   动态多球


import time

import matplotlib.pyplot as plt

from Utils import *


class Bouncing:
    ## 版本
    bouncing_version = 0.8

    ## 加载关卡信息，静态初始化
    def __init__(self, level: LevelInfo):
        # 版本兼容性检查
        assert level.bouncing_version <= self.bouncing_version, 'The selected level needs higher version of bouncing!'

        ## 静态初始化
        self.init_flag = False

        # 参数
        self.t = 0.             # 仿真时序
        self.t_len = 0          # 仿真时长
        self.total_time = 0.    # 总仿真时长(在这里设置n倍速)
        self.n_num = 0          # 仿真点数
        self.total_frames = 0   # 总仿真帧数
        self.fps = 0.           # 仿真频率
        self.render_per = 0     # 每 render_per 个frame渲染一帧
        self.ob_idx = {}        # 障碍物快速索引

        # 统计信息
        self.static = {
            'bounce number': 0,
            'total hardness': 0,
            'shoot number': 0,
            'last_run_time': 0.0,
            'visual fps': 0.0,
            'hit number': 0
        }

        # 关卡信息
        self.level = level
        self.rect_w = level.rect_w
        self.rect_h = level.rect_h
        self.acc = level.acc
        self.t_start = level.t_start
        self.t_stop = level.t_stop

        # 时间和帧数管理
        self.dt = 0.05  # 仿真步长
        self.frame = 0  # 0 索引
        self.fps_render = 30  # 渲染帧率

        ## 初始化图形界面graph
        self.graph = Graph()

        ## 小球管理
        # 构造列表
        self.ball = []
        if isinstance(level.pos_0, np.ndarray):
            # 向后兼容
            level.pos_0 = [level.pos_0]
            level.v_0 = [level.v_0]
        self.n_ball = len(level.pos_0)
        for i in range(self.n_ball):
            self.ball.append(Ball())
            self.ball[i].pos = level.pos_0[i].astype(float)
            self.ball[i].v = level.v_0[i].astype(float)
            self.ball[i].tail.max_len = 1 + int(1 / self.dt)  # 尾巴长度（点数）

        ## 障碍物管理
        # 获取障碍物信息
        self.obstacle = level.obstacle
        for i in range(len(self.obstacle)):
            # 检查障碍物合法性
            if self.obstacle[i].x >= self.rect_w or self.obstacle[i].y >= self.rect_h:
                raise 'Obstacle value invalid!'

    ## 初始化动态参数和变量
    # 由静态参数派生而来
    def initialize(self):
        # 正常情况只初始化一次
        if self.init_flag:
            return self.init_flag

        # 时间和帧数管理
        self.t = self.t_start
        self.t_len = self.t_stop - self.t_start  # 仿真时长
        self.total_time = self.t_len / 5  # 总仿真时长(在这里设置n倍速)
        self.n_num = int(self.t_len / self.dt)  # 仿真点数
        self.total_frames = self.n_num  # 总仿真帧数
        self.fps = self.total_frames / self.total_time  # 仿真频率
        if self.fps_render > self.fps:
            self.fps_render = self.fps
        self.render_per = int(self.fps / self.fps_render)  # 每 render_per 次渲染一帧

        ## 初始化图形元素
        # 界面graph
        plt.ion()
        plt.rcParams['toolbar'] = 'None'  # 禁用工具栏
        self.graph.fig = plt.figure(figsize=self.graph.fig_size, frameon=False)
        self.graph.fig.canvas.set_window_title('bouncing!')
        self.graph.ax = plt.subplot(xlim=[0, self.rect_w], ylim=[0, self.rect_h], aspect=1)
        self.graph.ax.set_xticks([i for i in range(self.rect_w)], labels=[])
        self.graph.ax.set_yticks([i for i in range(self.rect_h)], labels=[])
        self.graph.ax.grid(visible=True, linewidth=0.5)
        self.graph.ax.tick_params(axis='both', length=0)
        self.graph.ax.set_xlabel('rest time: ' + str(self.t_len))
        self.graph.ax.set_title('bouncing! ver. ' + str(self.bouncing_version))

        ## 小球管理
        # 生成句柄
        for i in range(self.n_ball):
            self.ball[i].head.handle, = self.graph.ax.plot(
                self.ball[i].pos[0], self.ball[i].pos[1],
                marker=self.ball[i].head.marker,
                markersize=self.ball[i].head.size,
                color=self.ball[i].head.color,
                zorder=10
            )
            self.ball[i].tail.append_data(self.ball[i].pos)
            self.ball[i].tail.handle, = self.graph.ax.plot(
                self.ball[i].tail.data[:, 0], self.ball[i].tail.data[:, 1],
                linestyle=self.ball[i].tail.linestyle,
                color=self.ball[i].tail.color,
                linewidth=self.ball[i].tail.linewidth,
                zorder=9
            )

        ## 障碍物管理
        # 获取障碍物信息
        for i in range(len(self.obstacle)):
            ob = self.obstacle[i]  # 注意ob不做左值
            # 生成快速索引
            self.ob_idx[(ob.x, ob.y)] = i
            # 生成障碍物句柄
            rect = plt.Rectangle(
                (ob.x, ob.y), 1, 1,
                facecolor=ob.color, linewidth=0.5
            )
            self.obstacle[i].handle = self.graph.ax.add_patch(rect)
            self.static['total hardness'] += self.obstacle[i].hard

        ## 返回初始化标记
        self.init_flag = True
        return self.init_flag

    ## 状态递推器
    # 根据当前的环境和质点属性，推导出一个球的下一时刻的属性
    def next_state(self, ball_num=0):
        # 状态信息
        state_info = State()

        ball = self.ball[ball_num]

        # 防穿越
        # 如果cell_new不是cell_old的相邻四格，则缩短步长
        pos_new, __ = self.move(pos=ball.pos, v=ball.v)
        cell_old = np.floor(ball.pos).astype(int)
        cell_new = np.floor(pos_new).astype(int)
        if sum(abs((cell_new - cell_old))) > 1:
            dtp = self.dt
            for tmp in range(5):  # 只做有限次
                dtp = dtp / 2
                pos_new, __ = self.move(pos=ball.pos, v=ball.v, dt=dtp)
                if sum(abs((cell_new - cell_old))) <= 1:
                    break
            cell_old = np.floor(ball.pos).astype(int)
            cell_new = np.floor(pos_new).astype(int)

        # 防超速
        # v*dt < 0.2
        v_m = np.linalg.norm(ball.v, 2)
        if v_m > 0.2 / self.dt:
            ball.v = ball.v / v_m * 0.2 / self.dt

        # 边界检查 + 障碍物撞击检查
        # 如果下一刻前要撞击，那么现在就撞击
        hit_ceil = pos_new[1] > self.rect_h
        hit_floor = pos_new[1] < 0
        hit_left = pos_new[0] < 0
        hit_right = pos_new[0] > self.rect_w
        if hit_ceil or hit_floor or hit_left or hit_right:
            self.static['bounce number'] += 1
            if hit_floor:
                ball.v[1] = -ball.v[1]
            if hit_ceil:
                ball.v[1] = -ball.v[1]
            if hit_left:
                ball.v[0] = -ball.v[0]
            if hit_right:
                ball.v[0] = -ball.v[0]
        elif (cell_new[0], cell_new[1]) in self.ob_idx:
            self.static['bounce number'] += 1
            self.static['hit number'] += 1
            idx = self.ob_idx[(cell_new[0], cell_new[1])]
            if idx and self.obstacle[idx].hard > 0:
                if not cell_old[0] == cell_new[0]:
                    ball.v[0] = -ball.v[0]
                if not cell_old[1] == cell_new[1]:
                    ball.v[1] = -ball.v[1]
                state_info.hit_index = idx

        # 更新位置
        pos, v = self.move(pos=ball.pos, v=ball.v)
        self.ball[ball_num].pos = pos
        self.ball[ball_num].v = v
        return state_info

    # 击发函数
    # TODO 需要好好设计
    def shoot(self, ball, target):
        # target
        target = target - ball.pos
        ball.v = np.linalg.norm(ball.v, 2) * target / np.linalg.norm(target, 2)
        pos, v = self.move(pos=ball.pos, v=ball.v)
        self.static['shoot number'] += 1
        return pos, v

    # 运动行为
    # 运动产生的后果：位置变化，速度变化
    def move(self, pos, v, dt=None, acc=None):
        # 梯形法求加速度
        if not dt:
            dt = self.dt
        if not acc:
            acc = self.acc
        a_1 = acc(pos)
        pos_2 = pos + v * dt + 0.5 * a_1 * dt * dt
        a_2 = acc(pos_2)
        a_ = (a_1 + a_2) / 2
        pos = pos + v * dt + 0.5 * a_ * dt * dt
        v = v + a_ * dt
        return pos, v

    ## 仿真主循环
    def mainloop(self):
        exit_flag = 0
        time_start = time.time()
        # 动态初始化
        if not self.init_flag:
            self.initialize()
        try:
            render_counter = 0
            for frame in range(self.total_frames):
                # 圈计
                loop_timer = time.time()
                # 逐个仿真
                for ball_num in range(self.n_ball):
                    # 更新运动状态
                    state_info = self.next_state(ball_num)

                    # 更新头
                    self.ball[ball_num].head.handle.set(
                        xdata=self.ball[ball_num].pos[0], ydata=self.ball[ball_num].pos[1]
                    )
                    # 更新尾巴
                    self.ball[ball_num].tail.append_data(self.ball[ball_num].pos)
                    self.ball[ball_num].tail.handle.set(
                        xdata=self.ball[ball_num].tail.data[:, 0],
                        ydata=self.ball[ball_num].tail.data[:, 1]
                    )
                    # 更新障碍物
                    if state_info.hit_index > -1:
                        self.obstacle[state_info.hit_index].hard -= 1
                        self.obstacle[state_info.hit_index].handle.set(
                            color=self.obstacle[state_info.hit_index].color
                        )

                # 更新标签
                self.graph.ax.set_xlabel(
                    'rest time: ' + str(np.round(self.t_stop - self.t - self.dt, 1))
                )
                self.t += self.dt
                self.frame += 1

                # 渲染画面
                # 降频渲染+动态时间管理
                render_counter += 1
                if render_counter % self.render_per == 0 or frame == self.total_frames-1:
                    # 检查存在性
                    if not plt.fignum_exists(self.graph.fig.number):
                        raise 'Bouncing has been terminated!'
                    pause_time = 1 / self.fps_render - (time.time() - loop_timer)
                    if pause_time < 0.001:
                        pause_time = 0.001
                    plt.pause(pause_time * 0.8)  # 留20%裕度
                    render_counter = 0

        except Exception:
            # raise  # for debug
            exit_flag = -1
        time_end = time.time()
        self.static['last_run_time'] = time_end - time_start
        self.static['visual fps'] = self.total_frames / self.render_per / (time_end - time_start)
        return exit_flag


if __name__ == '__main__':
    from levels import level_test_3

    bc = Bouncing(level_test_3.level())
    bc.ball[1].tail.max_len = 100  # 0.8支持用户修改参数了
    bc.ball[1].head.color = [0.9, 0.1, 0.1]

    flag = bc.mainloop()
    summary = {
        'flag': flag,
        'total time': bc.total_time,
        'real time': bc.static['last_run_time'],
        'fps': bc.fps,
        'fps_render': bc.fps_render,
        'real fps': bc.static['visual fps']
    }
    [print(x) for x in summary.items()]

    # tmp = ''
    # for i in range(3):
    #     print(tmp+str(3-i), end='')
    #     tmp = '\b'*len(str(3-i))
    #     time.sleep(1)
