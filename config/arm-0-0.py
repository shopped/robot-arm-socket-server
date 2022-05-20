min = [0, 0, 0, 0, 0, 0]
max = [180, 180, 180, 180, 180, 100]
reverse = [False, True, False, False, True, False]
resting = [95,15,180,0,50,30]

def lerp(index, value):
    if (index == 4):
        if (value < 90):
            return int(170 - (value)*(125/90))
        else:
            return 45
    new_value = 180 - value if reverse[index] else value
    new_value = min[index] + (new_value/180) * (max[index] - min[index])
    return new_value
