# Implementation of LAHM model and application to my dataset
from copy import copy
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import special
from dataclasses import dataclass

###### Requirements etc
# only applicable to:
# - velocities over 1m/day
# - energy extraction under 45.000 kWh/year

# LAHM model (Kinzelbach, 1987):
# - calculates temperature field
# - with continous point source
# - convective and dispersive heat transport
# - in a homogeneous confined aquifer ("homogener gespannter Porengrundwasserleiter")
# - under instationary conditions

# - equations:
# $$ \Delta T (x,y,t) = \frac{Q \cdot \Delta T_{inj}}{4 \cdot n_e \cdot M \cdot v_a \cdot \sqrt{\pi \cdot \alpha_T}}
# \cdot \exp{(\frac{x - r}{2 \cdot \alpha_L})} \cdot \frac{1}{\sqrt{r}}
# \cdot erfc(\frac{r - v_a \cdot t/R}{2 \cdot \sqrt{v_a \cdot \alpha_L \cdot t/R}}) 
# $$
# with:
# $$ r = \sqrt{x^2 + y^2 \cdot \frac{\alpha_L}{\alpha_T}} $$

# - $\Delta T$ : Gesuchte Isotherme als Differenz zur unbeeinflussten Grundwassertemperatur [K]
# - $Q$ : Injektionsrate [m 3 /s]
# - $T_{inj}$ : Differenz zwischen der Injektionstemperatur und der unbeeinflussten Grundwassertemperatur [K]
# - $n_e$ : effektive Porosität [–]
# - $M$ : genutzte, grundwassererfüllte Mächtigkeit [m]
# - $v_a$ : Abstandsgeschwindigkeit [m/s]
# - $α_{L,T}$ : Längs- und Querdispersivität [m]
# - $x$, $y$: Längs- und Querkoordinaten [m]
# - $t$: Zeit [s]
# - $R$: Retardation [–]
# - $r$: radialer Abstand vom Injektionsbrunnen [m]

######## Next steps
# TODO temperature added too high

# read input from file
# test on dataset
# adaptation to 3D
# read streamlines
# coordination transformation

def delta_lahm(x, y, time, parameters, v_a):
    """
    Calculate the temperature difference between the injection well and the point (x, y) at time t.
    """
    
    n_e = parameters.n_e
    M = parameters.m_aquifer
    alpha_L = parameters.alpha_L
    alpha_T = parameters.alpha_T
    R = parameters.R
    T_inj_diff = parameters.T_inj_diff
    q_inj = parameters.q_inj

    radial_distance = _radial_distance(x, y, alpha_L, alpha_T)
    term_numerator = q_inj * T_inj_diff
    term_denominator = 4 * n_e * M * v_a * np.sqrt(np.pi * alpha_T)
    term_exponential = np.exp((x - radial_distance) / (2 * alpha_L))
    term_sqrt = 1 / np.sqrt(radial_distance)
    term_erfc = special.erfc((radial_distance - v_a * time / R) / (2 * np.sqrt(v_a * alpha_L * time / R)))
    return term_numerator / term_denominator * term_exponential * term_sqrt * term_erfc

###### helper functions
def _radial_distance(x, y, alpha_L, alpha_T):
    return np.sqrt(x**2 + y**2*alpha_L/alpha_T)

# helper functions
def _calc_R(ne, Cw, Cs):
    return ((1-ne)*Cs+ne*Cw)/(ne*Cw)

def _calc_perm(k_cond, eta, rho_w, g):
    return k_cond*eta/(rho_w*g)

def _calc_vf(k_cond, grad_p):
    return -k_cond*grad_p

def _calc_va(vf, ne):
    return vf/ne

def _calc_alpha_T(alpha_L):
    return 0.1*alpha_L

def _approx_prop_of_porous_media(prop_water : float, prop_solid : float, n_e : float) -> float:
    return prop_water * n_e + prop_solid * (1-n_e) # new compared to LAHM, rule source: diss.tex

@dataclass
class Parameters:
    n_e : float = 0.25
    C_w : float = 4.2e6 # [J/m^3K]
    C_s : float = 2.4e6
    C_m : float = _approx_prop_of_porous_media(C_w, C_s, n_e)
    R : float = _calc_R(n_e, C_w, C_s) #2.7142857142857144
    rho_w : float = 1000
    rho_s : float = 2800
    g : float = 9.81
    eta : float = 1e-3
    alpha_L : float = 1 #[1,30]
    alpha_T : float = _calc_alpha_T(alpha_L)
    m_aquifer : float = 5#[5,14]

    T_gwf : float = 10.6
    T_inj_diff : float = 5
    q_inj : float = 0.00024 #[m^3/s]

    lambda_w : float = 0.65 # [-], source: diss
    lambda_s : float = 1.0 # [-], source: diss
    lambda_m : float = _approx_prop_of_porous_media(lambda_w, lambda_s, n_e)

@dataclass
class Testcase:
    name : str
    grad_p : float # [-]
    k_cond : float # [m/s]
    k_perm : float = 0 # [m^2]
    v_f : float = 0 # [m/s]
    v_a : float = 0 # [m/s]
    v_a_m_per_day : float = 0 # [m/day]

    def post_init(self, params:Parameters):
        if self.k_perm == 0:
            self.k_perm = _calc_perm(self.k_cond, params.eta, params.rho_w, params.g)
        else:
            temp = _calc_perm(self.k_cond, params.eta, params.rho_w, params.g)
            assert abs(temp - self.k_perm) < 1e-6, f"k_perm {self.k_perm} must be equal to k_cond*eta/(rho_w*g) {temp}"
        self.v_f = _calc_vf(self.k_cond, self.grad_p)
        self.v_a = np.array(np.round(_calc_va(self.v_f, params.n_e), 12))
        if self.v_a < 0:
            print("v_a must be positive, I change it to its absolute value")
            self.v_a = abs(self.v_a)

        self.v_a_m_per_day = np.array(np.round(self.v_a*24*60*60, 12))

        # first lahm requirement:
        # assert self.v_a_m_per_day <= -1, "v_a must be at least 1 m per day to get a valid result"