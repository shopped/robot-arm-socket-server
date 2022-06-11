in_min = [0, 45, 0, 0, 0, 0]
in_max = [180, 110, 180, 180, 180, 180]
out_min = [0, 0, 90, 0, 0, 90]
out_max = [180, 120, 180, 180, 180, 180]
reverse = [False, True, False, True, True, False]
resting = [90, 70, 150, 10, 110, 150]

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
