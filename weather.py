import numpy as np

def weather(wind_type):
    if "light" in wind_type:
        v_mag = 2 # m/s (1-3)
    elif "strong" in wind_type:
        v_mag = 4 # m/s (4-7)

    v_dir = -45  # degrees (from north, clockwise)

    # wind_dir_deg = 20.0 # wind direction degrees (meteorological: direction from which it comes)
    # convert to vector: wind blowing TOWARD (u_x, u_y)
    theta = np.deg2rad(270 - v_dir)  # convert meteorological to math angle
    vx = v_mag * np.cos(theta)
    vy = v_mag * np.sin(theta)

    return vx,vy