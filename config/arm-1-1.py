min = [0, 0, 90, 0, 0, 0]
max = [180, 180, 180, 180, 180, 45]
reverse = [False, True, False, True, True, False]
resting = [70,160,175,0,90,30]

def lerp(index, value):
    new_value = 180 - value if reverse[index] else value
    new_value = min[index] + (new_value/180) * (max[index] - min[index])
    return new_value
