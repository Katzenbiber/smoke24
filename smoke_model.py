import numpy as np
from weather import weather
from emergency import emergency
from domain import domain

# # 2D advection-diffusion (explicit)
# Represents ground-level concentration C(x,y,t) [g/m^3] for an outdoor smoke source Q [g/s].

# Notes:
# - Assumes smoke mixes into a vertical mixing depth Hmix (m).
# - Uses first-order upwind for advection, central differences for diffusion (explicit).
# - Stability: dt <= min( dx/|u|, dy/|v|, dx^2/(4*K), dy^2/(4*K) ) * safety_factor

# ---------------------------
# Helper discrete ops
# ---------------------------
def upwind_advection(C, ux, uy, dx, dy, dt, inflow_val=0.0):
    """
    First-order upwind advection with non-periodic boundaries.
    inflow_val = value imposed at inflow boundaries (usually 0).
    """
    Ny, Nx = C.shape
    Cn = C.copy()

    # ---------- X-direction ----------
    if ux >= 0:
        # use left gradient, interior only
        Cn[:, 1:] = C[:, 1:] - ux * dt/dx * (C[:, 1:] - C[:, :-1])
        # left boundary is inflow → impose inflow_val
        Cn[:, 0] = inflow_val
    else:
        # use right gradient, interior only
        Cn[:, :-1] = C[:, :-1] - ux * dt/dx * (C[:, 1:] - C[:, :-1])
        # right boundary is inflow → impose inflow_val
        Cn[:, -1] = inflow_val

    # ---------- Y-direction ----------
    C2 = Cn.copy()

    if uy >= 0:
        C2[1:, :] = Cn[1:, :] - uy * dt/dy * (Cn[1:, :] - Cn[:-1, :])
        C2[0, :] = inflow_val
    else:
        C2[:-1, :] = Cn[:-1, :] - uy * dt/dy * (Cn[1:, :] - Cn[:-1, :])
        C2[-1, :] = inflow_val

    return C2

def diffusion_step(C, K, dx, dy, dt):
    """
    Explicit 2D diffusion, no wrap-around, correct shapes.
    Zero-gradient (Neumann) boundaries.
    """
    Ny, Nx = C.shape
    Cn = C.copy()

    # enforce zero-gradient boundaries BEFORE applying stencil
    Cn[:, 0]  = Cn[:, 1]
    Cn[:, -1] = Cn[:, -2]
    Cn[0, :]  = Cn[1, :]
    Cn[-1, :] = Cn[-2, :]

    Cout = Cn.copy()

    # Interior: 1..Ny-2, 1..Nx-2
    d2x = (Cn[1:-1, 2:] - 2*Cn[1:-1, 1:-1] + Cn[1:-1, :-2]) / (dx*dx)
    d2y = (Cn[2:, 1:-1] - 2*Cn[1:-1, 1:-1] + Cn[:-2, 1:-1]) / (dy*dy)

    Cout[1:-1, 1:-1] = Cn[1:-1, 1:-1] + dt * K * (d2x + d2y)

    # enforce zero-gradient again
    Cout[:, 0]  = Cout[:, 1]
    Cout[:, -1] = Cout[:, -2]
    Cout[0, :]  = Cout[1, :]
    Cout[-1, :] = Cout[-2, :]

    return Cout

def smoke_concentration(C, save_times, dt, nt, vx, vy, dx, dy, K, src_mask, inflow_val=0.0):
    snapshots = {}
    save_steps = set(int(np.round(t / dt)) for t in save_times)

    for n in range(nt):

        C = upwind_advection(C, vx, vy, dx, dy, dt, inflow_val=inflow_val)
        C = diffusion_step(C, K, dx, dy, dt)

        # steady source
        C += dt * src_mask

        # enforce non-periodic BCs finally
        C[:, 0]  = C[:, 1]
        C[:, -1] = C[:, -2]
        C[0, :]  = C[1, :]
        C[-1, :] = C[-2, :]

        if n in save_steps:
            snapshots[n] = C.copy()

    return snapshots

def initialize_source_distribution(source_x, source_y, Q, x, y, Nx, Ny, dx, dy, Hmix):
    # ---------------------------
# Initial condition & source
# ---------------------------
    C = np.zeros((Ny, Nx), dtype=float)  # concentration [g/m^3]
# Source location (building) - put near upwind left side
    ix = int(round((source_x - x[0]) / dx))
    iy = int(round((source_y - y[0]) / dy))
# source term per cell as volumetric source (g/m^3/s) = Q / (cell_area * Hmix)
    cell_area = dx * dy
    S_cell = Q / (cell_area * Hmix)  # g / m^3 / s injected into that cell
    # print(f"Source at grid cell (iy,ix)=({iy},{ix}), S_cell={S_cell:.3e} g/m^3/s")

# Option: distribute source over a small patch
    src_radius_m = 2.0
    src_radius_cells = max(1, int(np.round(src_radius_m / max(dx, dy))))
    src_mask = np.zeros_like(C, dtype=float)
    for j in range(max(0, iy-src_radius_cells), min(Ny, iy+src_radius_cells+1)):
        for i in range(max(0, ix-src_radius_cells), min(Nx, ix+src_radius_cells+1)):
            dist = np.hypot((x[i]-source_x), (y[j]-source_y))
            if dist <= src_radius_m:
                src_mask[j,i] = 1.0
# normalize mask so total source = Q
    mask_sum = src_mask.sum()
    if mask_sum > 0:
        src_mask *= (Q / mask_sum) / (cell_area * Hmix)  # now src_mask has g/m^3/s per cell
    else:
        src_mask[iy,ix] = S_cell

    return C, src_mask

# ---------------------------
# Time stepping params
# ---------------------------

# Stability constraints
def stability_constraints(dx, dy, vx, vy, K, t_final):
    cfl_adv_x = abs(vx) / dx if dx>0 else 1e9
    cfl_adv_y = abs(vy) / dy if dy>0 else 1e9
    dt_adv = 0.9 / max(1e-12, (cfl_adv_x + cfl_adv_y))  # conservative for split advection
    dt_diff = 0.25 * min(dx*dx, dy*dy) / (4 * K + 1e-12)  # diffusion stability approx
    safety = 0.5
    dt = safety * min(dt_adv, dt_diff, 1.0)  # cap to 1 s for sanity
    nt = int(np.ceil(t_final / dt))
    # print(f"dx={dx:.2f} m, dy={dy:.2f} m, dt={dt:.3f} s, nt={nt}, u=({vx:.2f},{vy:.2f}) m/s, K={K} m^2/s")
    return dt, nt

def smoke(time_sec:float):
    vx, vy = weather("constant light breeze") # read weather data (wind velocity, direction, temperature)
    map, x, y, Lx, Ly, Nx, Ny, dx, dy = domain("frontend/data/houses.png", Nx=201, Ny=201) # read domain data (map of the area)
    # print("Domain size (m): ", Lx, Ly, " Grid points: ", Nx, Ny)
    emergency_x, emergency_y, Q, Hmix, K = emergency("small fire", 100, 50) # set emergency type and location

    t_final = time_sec +1  # in seconds
    dt, nt = stability_constraints(dx, dy, vx, vy, K, t_final)

    C, src_mask = initialize_source_distribution(emergency_x, emergency_y, Q, x, y, Nx, Ny, dx, dy, Hmix)
    snapshots = smoke_concentration(C, save_times=[time_sec,], dt=dt, nt=nt, vx=vx, vy=vy, dx=dx, dy=dy, K=K, src_mask=src_mask)
    return {"Nx" : Nx, "Ny" : Ny,
            "dx" : dx, "dy" : dy,
            "data" : snapshots[int(np.round(time_sec / dt)) ].flatten().tolist()}
