def emergency(type, x_in_m, y_in_m):
    # emergency data
    # read emergency source data like location, amount of smoke, starting time
    emergency_x = x_in_m  # m # source location
    emergency_y = y_in_m   # m # source location

    # Typical soot emission rate (mass of smoke particles)
    # Small room fire: 0.001–0.01 g/s
    # Big compartment fire: 0.1–1 g/s
    # To convert to a 1D source term, we treat it as “mass per meter per second”.
    if "small" in type:
        Q = 0.005    # "mass per second"
    elif "big" in type:
        Q = 0.5      # "mass per second" (abstract units OK for simulation)

    if "fire" in type:
        # ---------------------------
        # Physical / scenario params
        # ---------------------------
        Hmix = 100.0        # vertical mixing depth [m] (50..300 m typical)
        K = 10.0            # horizontal eddy diffusivity [m^2/s] (typical 1..50 m^2/s)
        # Molecular diffusion is negligible outdoors, not included separately.

    return emergency_x, emergency_y, Q, Hmix, K