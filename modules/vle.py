import numpy as np
from bublP import bubble_P
from dewP import dew_P
from parameters import component_properties
from phiCalc import Phi_calc_liquid, Phi_calc_vapor


def initiate(components, T, P, z, eos_model):
    
    status_bubl, message_bubl, P_bubl, y_bubl = bubble_P(components, T, z, eos_model)
    status_dew, message_dew, P_dew, x_dew = dew_P(components, T, z, eos_model)
    
    next_step = 0
    if P > P_bubl:
        next_step = 1
        message_initiate = "The mixture is at SUB-COOLED state. VLE calculation can NOT be continued. Try a higher temperature or a lower pressure."
    elif P < P_dew:
        next_step = 1
        message_initiate = "The mixture is at SUPER-HEATED state. VLE calculation can NOT be continued. Try a lower temperature or a higher pressure."
    elif (P < P_bubl) & (P > P_dew):
        next_step = 0
        message_initiate = "The mixture has vapor and liquid phase. Flash Calculation can be proceed."
    else:
        next_step = 1
        message_initiate = "OOPS!"
        
    if next_step == 0:
        parameters = component_properties(components, T, eos_model)
        Pc = parameters['Pc']
        omega = parameters['omega']
        Tr = parameters['Tr']
        V_initial = (P_bubl - P)/(P_bubl - P_dew)
        K_initial = (Pc/P)*np.exp(5.37*(1+omega)*(1-(1/Tr)))
    elif next_step == 1:
        V_initial = 0
        K_initial = 0
        
    return next_step, V_initial, K_initial, P_bubl, P_dew, message_bubl, message_dew, message_initiate


def first_block(V, K, z, components, T, P, eos_model):
    
    F = np.sum((z * (K - 1)) / (1 + V*(K - 1)))
    dF = -np.sum((z * (K - 1)**2) / (1 + V*(K - 1))**2)
    V_new = V - (F/dF)
    
    x = z/(1 + V_new*(K - 1))
    y = x*K
    
    Phi_liquid = Phi_calc_liquid(components, T, P, x, eos_model)
    Phi_vapor = Phi_calc_vapor(components, T, P, y, eos_model)
    K_new = Phi_liquid/Phi_vapor
    
    return V_new, K_new, x, y



def inner_loop(V, K, z, components, T, P, eos_model):
    
    V_new, K_new, x, y = first_block(V, K, z, components, T, P, eos_model)
    if (abs(V_new - V) < 0.001) & (np.sum(abs(K_new - K)) < 0.01):
        return V_new, K_new, x, y
    else:
        return inner_loop(V_new, K_new, z, components, T, P, eos_model)
   
    
        
def outer_loop(components, T, P, z, eos_model):
    
    next_step, V_initial, K_initial, P_bubl, P_dew, message_bubl, message_dew, message_initiate = initiate(components, T, P, z, eos_model)
    if next_step == 0:
        V, K, x, y = inner_loop(V_initial, K_initial, z, components, T, P, eos_model)
        return V, x, y, P_bubl, P_dew, message_bubl, message_dew, message_initiate
    
    elif next_step == 1:
        V = None
        x = None
        y = None
        return V, x, y, P_bubl, P_dew, message_bubl, message_dew, message_initiate
    
