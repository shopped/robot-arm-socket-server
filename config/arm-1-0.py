min = [0, 0, 0, 0, 0, 0]
max = [180, 150, 180, 180, 180, 155]
reverse = [False, True, True, False, False, False]
resting = [105,20,175,0,110,150]

def lerp(index, value):
    new_value = 180 - value if reverse[index] else value
    new_value = min[index] + (new_value/180) * (max[index] - min[index])
    return new_value
