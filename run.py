# -*- coding: utf-8 -*-
from levels import level_test_1, level_test_2, level_test_3, level_1
from bouncing import Bouncing

# bc = Bouncing(level_test_1.level())
# bc = Bouncing(level_test_2.level())

bc = Bouncing(level_1.level())
bc.ball[0].tail.color = [0.4, 0.4, 0.8]  # 0.8支持用户修改参数了
bc.ball[0].head.color = [0.9, 0.1, 0.1]

flag = bc.mainloop()

# [print(x) for x in bc.statistic.items()]

summary = {
    'flag': flag,
    'total time': bc.simulate_time,
    'real time': bc.statistic['last run time'],
    'fps': bc.fps_simulate,
    'fps_render': bc.fps_render,
    'visual fps': bc.statistic['visual fps']
}
[print(x) for x in summary.items()]


