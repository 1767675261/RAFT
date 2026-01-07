import random
import json
random.seed(33)


config = json.load(open("config.json", "r", encoding="utf-8"))
c = config[0]
n = len(c)


# 每次随机删掉一个元素
for i in range(n):
    cpy = config[-1].copy()
    idx = random.randint(0, len(cpy) - 1)
    cpy.pop(idx)
    config.append(cpy)

config = [c for c in config if c]

json.dump(config, open("config.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)