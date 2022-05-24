in_min = [0, 45, 0, 0, 0, 0]
in_max = [180, 110, 180, 180, 180, 180]
out_min = [0, 50, 90, 0, 0, 0]
out_max = [180, 180, 180, 180, 180, 45]
reverse = [False, True, False, True, True, False]
resting = [70,160,175,0,90,30]

def set_pwm_ranges(kit):
    kit.servo[1].set_pulse_width_range(500, 2500)
    kit.servo[2].set_pulse_width_range(500, 2500)

def lerp(index, value):
    new_value = max(value, in_min[index])
    new_value = min(new_value, in_max[index])
    new_value -= in_min[index]
    new_value = 180 * new_value / (in_max[index] - in_min[index])

    new_value = 180 - new_value if reverse[index] else new_value
    new_value = min[index] + (new_value/180) * (max[index] - min[index])
    return new_value
