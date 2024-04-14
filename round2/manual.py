to_num = {"pizza": 0, "root": 1, "snowball": 2, "shell": 3}
to_str = {0: "pizza", 1: "root", 2: "snowball", 3: "shell"}
convertion_rate = [
    [1, 0.48, 1.52, 0.71],
    [2.05, 1, 3.26, 1.56],
    [0.64, 0.3, 1, 0.46],
    [1.41, 0.61, 2.08, 1],
]

max_value = 0
max_path = []
MAX_LENGTH = 6


def find_max_path(path, value, visited):
    global max_value, max_path
    if len(path) == MAX_LENGTH and path[-1] == to_num["shell"]:
        if value == 1.0569693888:
            print(path)
            max_value = value
            max_path = path
        return
    elif len(path) == MAX_LENGTH:
        return
    for i in range(4):
        find_max_path(path + [i], value * convertion_rate[path[-1]][i], visited + [i])


find_max_path([to_num["shell"]], 1, [to_num["shell"]])
print(max_value, list(map(lambda x: to_str[x], max_path)))
print(max_value * 2000000)