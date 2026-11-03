import numpy as np

from .parameters import component_properties
from .phiCalc import Phi_calc_liquid, Phi_calc_vapor


def second_block(components, T, P, x, y, eos_model):

    Phi_liquid = Phi_calc_liquid(components, T, P, x, eos_model)
    Phi_vapor = Phi_calc_vapor(components, T, P, y, eos_model)
    
    K = Phi_liquid/Phi_vapor
    sum_Ky = np.dot(y,1/K)
    
    return K, sum_Ky


def third_block(components, T, P, x, y, eos_model):
    
    K, sum_Ky = second_block(components, T, P, x, y, eos_model)
    x_third = (y/K)/sum_Ky
    
    return x_third, sum_Ky


def fourth_block(components, T, P, x_third, y, eos_model):
    
    K, sum_Ky_new = second_block(components, T, P, x_third, y, eos_model)
    
    return sum_Ky_new


def inner_loop(components, T, P, x, y, eos_model):
    
    x_third, sum_Ky = third_block(components, T, P, x, y, eos_model)
    sum_Ky_new = fourth_block(components, T, P, x_third, y, eos_model)
    
    if abs(sum_Ky - sum_Ky_new) <= 0.001:
        return x_third, sum_Ky_new
    else:
        return inner_loop(components, T, P, x_third, y, eos_model)
    
    
def outer_loop(components, T, P, x, y, eos_model):
    
    x_third, sum_Ky_new = inner_loop(components, T, P, x, y, eos_model)
        
    if np.round(sum_Ky_new, 4) == 1:
        return P, x_third
    else:
        P = P/sum_Ky_new
        return outer_loop(components, T, P, x_third, y, eos_model)
    
    

def dew_P(components, T, z, eos_model):
    
    y = z
    parameters = component_properties(components, T, eos_model)
    Pc = parameters['Pc']
    Tr = parameters['Tr']
    omega = parameters['omega']

    f0 = 5.92714 - (6.09648/Tr) - (1.28862*np.log(Tr) + 0.169247*(Tr**6))
    f1 = 15.2518 - (15.6875/Tr) - (13.4721*np.log(Tr) + 0.435770*(Tr**6))
    P_i = Pc * np.exp(f0 + omega*f1)
    P_initial = np.dot(y, P_i)

    K_initial = (Pc/P_initial)*np.exp(5.37*(1+omega)*(1-(1/Tr)))
    x_initial = (y/K_initial) / np.dot(y, 1/K_initial)
    
    P_final, x_final = outer_loop(components, T, P_initial, x_initial, y, eos_model)
    
    status = 0
    message = "Dew P calculated successfuly!"
    
    if abs((P_initial - P_final)/P_final) < 0.1:
        P_initial_10 = P_initial * 10
        P_initial_01 = P_initial / 10
        P_final_10, x_final_10 = outer_loop(components, T, P_initial_10, x_initial, y, eos_model)
        P_final_01, x_final_01 = outer_loop(components, T, P_initial_01, x_initial, y, eos_model)

        if abs((P_initial_10 - P_final_10)/P_final_10) > 0.01:
            P_final = P_final_10
            x_final = x_final_10
        elif abs((P_initial_01 - P_final_01)/P_final_01) > 0.01:
            P_final = P_final_01
            x_final = x_final_01
        else:
            status = 1
            message = "Good progress has NOT been achieved for P by iteration."
    
    return status, message, P_final, x_final
