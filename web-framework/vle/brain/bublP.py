import numpy as np

from .parameters import component_properties
from .phiCalc import Phi_calc_liquid, Phi_calc_vapor


def second_block(components, T, P, x, y, eos_model):

    Phi_liquid = Phi_calc_liquid(components, T, P, x, eos_model)
    Phi_vapor = Phi_calc_vapor(components, T, P, y, eos_model)
    
    K = Phi_liquid/Phi_vapor
    sum_Kx = np.dot(x,K)
    
    return K, sum_Kx


def third_block(components, T, P, x, y, eos_model):
    
    K, sum_Kx = second_block(components, T, P, x, y, eos_model)
    y_third = K*x/sum_Kx
    
    return y_third, sum_Kx


def fourth_block(components, T, P, x, y_third, eos_model):
    
    K, sum_Kx_new = second_block(components, T, P, x, y_third, eos_model)
    
    return sum_Kx_new


def inner_loop(components, T, P, x, y, eos_model):
    
    y_third, sum_Kx = third_block(components, T, P, x, y, eos_model)
    sum_Kx_new = fourth_block(components, T, P, x, y_third, eos_model)
    
    if abs(sum_Kx - sum_Kx_new) <= 0.001:
        return y_third, sum_Kx_new
    else:
        return inner_loop(components, T, P, x, y_third, eos_model)
    
    
def outer_loop(components, T, P, x, y, eos_model):
    
    y_third, sum_Kx_new = inner_loop(components, T, P, x, y, eos_model)
    
    if np.round(sum_Kx_new, 4) == 1:
        return P, y_third
    else:
        P = P*sum_Kx_new
        return outer_loop(components, T, P, x, y_third, eos_model)
    
    
    
def bubble_P(components, T, z, eos_model):
    
    x = z
    parameters = component_properties(components, T, eos_model)
    Pc = parameters['Pc']
    Tr = parameters['Tr']
    omega = parameters['omega']

    f0 = 5.92714 - (6.09648/Tr) - (1.28862*np.log(Tr) + 0.169247*(Tr**6))
    f1 = 15.2518 - (15.6875/Tr) - (13.4721*np.log(Tr) + 0.435770*(Tr**6))
    P_i = Pc * np.exp(f0 + omega*f1)
    P_initial = np.dot(x, P_i)

    K_initial = (Pc/P_initial)*np.exp(5.37*(1+omega)*(1-(1/Tr)))
    y_initial = (x*K_initial)/(np.dot(x,K_initial))
    
    P_final, y_final = outer_loop(components, T, P_initial, x, y_initial, eos_model)
    
    status = 0
    message = "Bubble P calculated successfuly!"
        
    if abs((P_initial - P_final)/P_final) <= 0.1:
        P_initial_10 = P_initial * 10
        P_initial_01 = P_initial / 10
        P_final_10, y_final_10 = outer_loop(components, T, P_initial_10, x, y_initial, eos_model)
        P_final_01, y_final_01 = outer_loop(components, T, P_initial_01, x, y_initial, eos_model)
        
        if abs((P_initial_10 - P_final_10)/P_final_10) > 0.001:
            P_final = P_final_10
            y_final = y_final_10
        elif abs((P_initial_01 - P_final_01)/P_final_01) > 0.001:
            P_final = P_final_01
            y_final = y_final_01
        else:
            status = 1
            message = "Good progress has NOT been achieved for P by iteration."
    
    return status, message, P_final, y_final
