min = [0, 0, 90, 0, 0, 10]
max = [180, 180, 180, 180, 180, 100]
reverse = [False, False, False, True, True, False]
resting = [90,0,160,0,170,30]

def lerp(index, value):
    if (index == 4):
        if (value > 90):
            return int(180 - (value - 90)*(110/90))
        else:
            return 180
    new_value = 180 - value if reverse[index] else value
    new_value = min[index] + (new_value/180) * (max[index] - min[index])
    return new_value
