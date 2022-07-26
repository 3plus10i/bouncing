
from levels import test_level_1, test_level_2, test_level_3, level_1
from bouncing07 import Bouncing

# bc = Bouncing(test_level_1.level())
# bc = Bouncing(test_level_2.level())

level = level_1.level()
print(level.level_name)

bc = Bouncing(level)
bc.mainloop()

summary = {
    'total time': bc.total_time,
    'real time': bc.static['last_run_time'],
    'fps': bc.fps,
    'fps_render': bc.fps_render,
    'real fps': bc.static['visual fps']
}
[print(x) for x in summary.items()]

