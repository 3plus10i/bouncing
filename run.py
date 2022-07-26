
from levels import level_test_1, level_test_2, level_test_3, level_1
from bouncing import Bouncing

# bc = Bouncing(level_test_1.level())
# bc = Bouncing(level_test_2.level())

level = level_test_3.level()
print(level.level_name)

bc = Bouncing(level)
bc.ball[1].tail.max_len = 100  # 0.8支持用户修改参数了
bc.ball[1].head.color = [0.9, 0.1, 0.1]
bc.t_stop = 100

bc.mainloop()

summary = {
    'total time': bc.total_time,
    'real time': bc.static['last_run_time'],
    'fps': bc.fps,
    'fps_render': bc.fps_render,
    'real fps': bc.static['visual fps']
}
[print(x) for x in summary.items()]

