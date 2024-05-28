#!/usr/bin/env python3

import sys
import json
import numpy as np

# Model with variable coefficients

# Define constants
lambdaPP = 0.23 # [ W / m * K]
lambdaPaper = 0.15 # [ W / m * K]
rhoWater = 1000 # [kg / m^3]
c_m = 4186 # [J/kg * K]


def cylindricHeatCoefficient(r_i, r_o, h, lengthHeatCoeff):
    """
    ToDo: implement the heat flow coefficient (w/o temperature difference)
    for the cylinder.
    """
    return 

def planarHeatCoefficient(A, d, lengthHeatCoeff):
    """
    ToDo: implement the heat flow coefficient (w/o temperature difference)
    for a planar surface.
    """
    return

def cupModel(time, T_0, T_env, r_o, d_cup, h, d_lid):
    # For the ODE integration
    from scipy.integrate import odeint
    heatCoeff = cylindricHeatCoefficient(r_o - d_cup, r_o, h, lambdaPaper) + planarHeatCoefficient(np.pi * (r_o - d_cup)**2, d_lid, lambdaPP );
    Vol = 
    alpha = heatCoeff / (rhoWater * Vol * c_m)
    # The equation describing the model
    def f(T, time, alpha, T_env):
        return alpha * (T_env - T)

    # Solving the equation by numeric intergration
    temp = odeint(f, T_0, time, args=(alpha, T_env))[:, 0]

    # The output temperature
    return temp
# ...

if __name__=='__main__':
    json_input = sys.argv[1]
    with open(json_input, "r") as f:
        inputs = json.load(f)
    # Parse the json parameters
    r_o = float(inputs['r_o'])
    d_cup = float(inputs['d_cup'])
    h = float(inputs['h_cup'])
    d_lid = float(inputs['d_lid'])
    t_env = float(inputs['t_env'])
    temp0 = float(inputs['T0'])
    # manual fix of the time scale: 2500 sec , 500 time points
    t = np.linspace(0, 2500, 500)

    output_filename = inputs['out_file']
    # compute the temperature evolution
    te = cupModel(t, temp0, t_env, r_o, d_cup, h, d_lid)

    # output csv file
    np.savetxt(output_filename, te,
           delimiter=",", comments='',
           header='te')
