import numpy as np

from .parameters import eos_properties


def Z_calc(components, T, P, z, eos_model):
    
    A, B, AA_i, BB_i = eos_properties(components, T, P, z, eos_model)
    a = -(1 - B)
    b = A - 2*B - 3*np.power(B,2)
    c = -(A*B - np.power(B,2) - np.power(B,3))
    
    Q = (a**2 - 3*b)/9
    R = (2*a**3 - 9*a*b + 27*c)/54
    
    M = R**2 - Q**3
    
    # Three Roots
    if M < 0:
        theta = np.arccos(R/np.sqrt(Q**3))
        r1 = -(2*np.sqrt(Q) * np.cos(theta/3)) - a/3
        r2 = -(2*np.sqrt(Q) * np.cos((theta + 2*np.pi) / 3)) - a/3
        r3 = -(2*np.sqrt(Q) * np.cos((theta - 2*np.pi) / 3)) - a/3
        
        r = [r1, r2, r3]
    
    # One Real Root    
    elif M > 0:
        S = -(R/abs(R)) * (abs(R) + np.sqrt(M))**(1/3)
        T = Q/S
        r = S + T - (a/3)
        
        r = [r]
        
    return r
        


def Phi_calc_liquid(components, T, P, x, eos_model):
    
    r = Z_calc(components, T, P, x, eos_model)
    if len(r) == 1:
        Z = r[0]
    else:
        Z = min(r)
    
    A, B, AA_i, BB_i = eos_properties(components, T, P, x, eos_model)
    
    if len(components) >= 2:
        if eos_model == "PR":
            Phi_liquid = np.exp((BB_i*(Z-1)) - np.log(Z-B) - (A/(2.828*B))*(AA_i-BB_i)*np.log((Z+2.414*B)/(Z-0.414*B)))
        elif eos_model == "SRK":
            Phi_liquid = np.exp((BB_i*(Z-1)) - np.log(Z-B) - (A/B)*(AA_i-BB_i)*np.log(1+(B/Z)))
    else:
        if eos_model == "PR":
            Phi_liquid = np.exp(((Z-1)) - np.log(Z-B) - (A/(2.828*B))*np.log((Z+2.414*B)/(Z-0.414*B)))
        elif eos_model == "SRK":
            Phi_liquid = np.exp(((Z-1)) - np.log(Z-B) - (A/B)*np.log(1+(B/Z))) 
    
    return Phi_liquid
  
  
        
def Phi_calc_vapor(components, T, P, y, eos_model):
    
    r = Z_calc(components, T, P, y, eos_model)
    if len(r) == 1:
        Z = r[0]
    else:
        Z = max(r)
    
    A, B, AA_i, BB_i = eos_properties(components, T, P, y, eos_model)
    
    if len(components) >= 2:
        if eos_model == "PR":
            Phi_vapor = np.exp((BB_i*(Z-1)) - np.log(Z-B) - (A/(2.828*B))*(AA_i-BB_i)*np.log((Z+2.414*B)/(Z-0.414*B)))
        elif eos_model == "SRK":
            Phi_vapor = np.exp((BB_i*(Z-1)) - np.log(Z-B) - (A/B)*(AA_i-BB_i)*np.log(1+(B/Z)))
    else:
        if eos_model == "PR":
            Phi_vapor = np.exp(((Z-1)) - np.log(Z-B) - (A/(2.828*B))*np.log((Z+2.414*B)/(Z-0.414*B)))
        elif eos_model == "SRK":
            Phi_vapor = np.exp(((Z-1)) - np.log(Z-B) - (A/B)*np.log(1+(B/Z)))
        
    return Phi_vapor