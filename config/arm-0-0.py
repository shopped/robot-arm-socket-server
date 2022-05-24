in_min = [0, 0, 0, 0, 0, 0]
in_max = [180, 180, 180, 180, 180, 180]
out_min = [0, 0, 0, 0, 0, 0]
out_max = [180, 180, 180, 180, 180, 100]
reverse = [False, True, False, False, True, False]
resting = [95,15,180,0,50,30]

def set_pwm_ranges(kit):
    kit.servo[2].set_pulse_width_range(500, 2500)

def lerp(index, value):
    if (index == 4):
        if (value < 90):
            return int(170 - (value)*(125/90))
        else:
            return 45
    new_value = 180 - value if reverse[index] else value
    new_value = max(value, in_min[index])
    new_value = min(new_value, in_max[index])
    new_value -= in_min[index]
    new_value = 180 * new_value / (in_max[index] - in_min[index])

    new_value = 180 - new_value if reverse[index] else new_value
    new_value = min[index] + (new_value/180) * (max[index] - min[index])
    return new_value
