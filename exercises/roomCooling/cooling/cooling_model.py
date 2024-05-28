#!/usr/bin/env python3

import sys
import json
import numpy as np

# Model with variable coefficients

# Define constants
c_m = 4186 # [J/kg * K], water

rhoAir = 1.225 # kg / m^3
c_p = 1.005e3 # [J / kg * K], air

lambdaGlass = 0.84 # [ W / (m * K) ]
lambdaAir = 0.023 # [ W / (m * K) ]
lambdaBrick = 0.12 # [ W / (m * K) ]
lambdaWood = 0.06 # [ W / (m * K) ]

def doublePaneWindowHeatCoefficient(A, b_glass, b_gas):
        """
        A function that encapsulates the calculation of the 
        heat conduction coefficient of a double-plied window
        of area A, glasss thickness b_glass and gas layer thickness
        b_gas - assuming the gas to be air.
        """
        return

def windowHeatFlux(w, h, T_1, T_2, b_glass, b_gas):
        """
        The function determines the heat flux across a double-plied
        window of a given area and composition with a temperature
        gradient T_1 - T_2.
        """
        return doublePaneWindowHeatCoefficient(w*h, b_glass, b_gas) * (T_1 - T_2)

def wallHeatFlux(w, h, d, T_1, T_2):
        """
        The function provides the heat flux across a brick wall
        """
        return 

def doorHeatFlux(w, h, d, T_1, T_2):
        """
        The function provides the heat flux across a wooden door
        """
        return 

def roomModel(time, T_0, T_env, w_room, l_room, h_room, d_wall, w_short,\
                w_window, h_window,
                w_door, h_door, d_door, b_glass, b_gas, \
                Qheater):
    # For the ODE integration
    from scipy.integrate import odeint
    # use a temeperature difference of 1 K to obtain the coefficients themselves
    surfaceHeatFlux = 0
    doorSurfaceHeatFlux = 0 
    Vol = 
    # The equation describing the model
    def f(T, time, alpha, beta, T_env):
        return alpha *( T_env - T) / (rhoAir * Vol * c_p) + beta * (T - T_0)/(rhoAir*Vol*c_p)

    # Solving the equation by intergration
    temp = odeint(f, T_0, time, args=(surfaceHeatFlux, doorSurfaceHeatFlux, T_env))[:, 0]

    # The output temperature
    return temp
# ...

if __name__=='__main__':
    json_input = sys.argv[1]
    with open(json_input, "r") as f:
        inputs = json.load(f)

    t_env = float(inputs['t_env'])
    temp0 = float(inputs['T0'])
    w_room = float(inputs['w_room'])
    l_room = float(inputs['l_room'])
    h_room = float(inputs['h_room'])
    w_short = float(inputs['w_short'])
    d_wall = float(inputs['d_wall'])
    w_window = float(inputs['w_window'])
    h_window = float(inputs['h_window'])
    w_door = float(inputs['w_door'])
    h_door = float(inputs['h_door'])
    d_door = float(inputs['d_door'])
    b_glass = float(inputs['b_glass'])
    b_air = float(inputs['b_air'])
    heaterPower = float(inputs['heaterPower'])
    # Time scale: 3600 [s/h] * 24 [h] using 750 time points
    t = np.linspace(0, 3600*24, 750)

    output_filename = inputs['out_file']

    te = roomModel(t, temp0, t_env, w_room, l_room, h_room, d_wall, w_short, w_window, h_window, w_door, h_door, d_door, b_glass, b_air, heaterPower);

    # output csv file
    np.savetxt(output_filename, te,
           delimiter=",", comments='',
           header='te')
