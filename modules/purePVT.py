import numpy as np
import math
from scipy.optimize import fsolve
import pandas as pd
import matplotlib.pyplot as plt
from properties import prop


######

# Just to compare this method with the other method used for the system.

######


def get_properties(component):
    """ 
    Collecting required data of the component

    Args:
        substances (list): Components list
        T (float): Tempreture in kelvins
    """

    omega = prop[component]['omega']
    Tc = prop[component]['Tc']
    Pc = prop[component]['Pc']
    
    return omega, Pc, Tc


def SRK_model(Tr, omega):
    """ 
    Redlich-Kwong EoS model.
    
    Args:   Tr (float): Reduced temperature.
    """
    sigma = 1
    epsilon = 0
    Omega = 0.08664
    Psi = 0.42748
    Zc = 1/3
    alpha = (1 + (0.48 + 1.574*omega - 0.176*(omega**2)) * (1-(Tr**(0.5))))**2
    
    return sigma, epsilon, Omega, Psi, Zc, alpha


def VDW_model(Tr):
    """ 
    Redlich-Kwong EoS model.
    
    Args:   Tr (float): Reduced temperature.
    """
    sigma = 0
    epsilon = 0
    Omega = 1/8
    Psi = 27/64
    Zc = 3/8
    alpha = 1
    
    return sigma, epsilon, Omega, Psi, Zc, alpha


def PR_model(Tr, omega):
    """ 
    Peng-Robinson EoS model
    
    Args:   Tr (float): Reduced temperature.
    """
    sigma = 1 + math.sqrt(2)
    epsilon = 1 - math.sqrt(2)
    Omega = 0.07780
    Psi = 0.45724
    Zc = 0.30740
    alpha = (1 + (0.37464 + 1.54226*omega - 0.2992*(omega)**2) * (1 - (Tr)**0.5))**2
    
    return sigma, epsilon, Omega, Psi, Zc, alpha


def RK_model(Tr):
    """ 
    Redlich-Kwong EoS model.
    
    Args:   Tr (float): Reduced temperature.
    """
    sigma = 1
    epsilon = 0
    Omega = 0.08664
    Psi = 0.42748
    Zc = 1/3
    alpha = Tr**(-1/2)
    
    return sigma, epsilon, Omega, Psi, Zc, alpha



def eos_par_calc(P, T, Psi, alpha, Tc, Pc, Omega):
    
    # Gas Constant = [cm^3 bar / mol k]
    R = 83.14

    a_i = Psi*alpha*R**2*Tc**2/Pc
    b_i = Omega*R*Tc/Pc
    
    beta = (b_i*P)/(R*T)
    q = a_i/(b_i*R*T)
    
    
    return a_i, b_i, beta, q



def Z_func_vapor(Z):
    """ 
    Iterative calculation of the vapor phase Z factor.
    
    Args:       Z (float): Z factor.
    Returns:    float: Recalculated Z factor.
    """
    Z_temp = 1 + beta - q*beta*((Z - beta)/((Z + epsilon*beta)*(Z + sigma*beta))) - Z
    return Z_temp


def Z_func_liquid(Z):
    """ 
    Iterative calculation of the vapor phase Z factor.
    
    Args:       Z (float): Z factor.
    Returns:    float: Recalculated Z factor.
    """
    Z_temp = beta + (Z+(epsilon*beta))*(Z+(sigma * beta))*((1+beta-Z)/(q*beta)) - Z
    return Z_temp 


def Z_Phi_calc():

    Z_liquid = fsolve(Z_func_liquid, beta)
    Z_vapor = fsolve(Z_func_vapor, 1)

    I_liquid = (1/(sigma-epsilon)) * np.log((Z_liquid+sigma*beta)/(Z_liquid+epsilon*beta))
    I_vapor = (1/(sigma-epsilon)) * np.log((Z_vapor+sigma*beta)/(Z_vapor+epsilon*beta))

    Phi_liquid = np.exp(Z_liquid - 1 - np.log(Z_liquid-beta) - q*I_liquid)
    Phi_vapor = np.exp(Z_vapor - 1 - np.log(Z_vapor-beta) - q*I_vapor)
    
    return Z_liquid, Z_vapor, Phi_liquid, Phi_vapor
    
    
    
def tabulate(component, eos_model, node_number):

    omega, Pc, Tc = get_properties(component)
    P_list = []
    T_list = []
    Z_liquid_list = []
    Z_vapor_list = []

    for i in range(node_number):
        if i == 0:
            T = Tc
            P = Pc
        else:
            T = 0.99*T_list[-1]
            P = 0.99*P_list[-1]
            
        Tr = T/Tc
        
        global sigma, epsilon, q, beta
        
        if eos_model == "PR":
            sigma, epsilon, Omega, Psi, Zc, alpha = PR_model(Tr, omega)
        elif eos_model == "SRK":
            sigma, epsilon, Omega, Psi, Zc, alpha = SRK_model(Tr, omega)
        elif eos_model == "VDW":
            sigma, epsilon, Omega, Psi, Zc, alpha = VDW_model(Tr)
        elif eos_model == "RK":
            sigma, epsilon, Omega, Psi, Zc, alpha = RK_model(Tr)
            
        a_i, b_i, beta, q = eos_par_calc(P, T, Psi, alpha, Tc, Pc, Omega)
        
        Z_liquid, Z_vapor, Phi_liquid, Phi_vapor = Z_Phi_calc()
        error = Phi_liquid - Phi_vapor
        while abs(error) > 0.01:
            if error > 0:
                P = (P + P_list[-1]) / 2
            elif error < 0:
                P = 0.99*P
            
            a_i, b_i, beta, q = eos_par_calc(P, T, Psi, alpha, Tc, Pc, Omega)    
            Z_liquid, Z_vapor, Phi_liquid, Phi_vapor = Z_Phi_calc()
            error = Phi_liquid - Phi_vapor
        
        T = np.round(T, 6)
        P = np.round(P, 6)
        Z_liquid = np.round(Z_liquid, 6)
        Z_vapor = np.round(Z_vapor, 6)
        
        T_list.append(float(T))
        P_list.append(float(P))
        Z_liquid_list.append(float(Z_liquid))
        Z_vapor_list.append(float(Z_vapor))
        
        if P < 0.001:
            break

    # Gas Constant = [cm^3 bar / mol k]
    R = 83.14

    df = pd.DataFrame()
    df['T'] = T_list
    df['P'] = P_list
    df['Z Liquid'] = Z_liquid_list
    df['Z Vapor'] = Z_vapor_list

    df['V Liquid'] = df['Z Liquid'] * R * df['T'] / df['P']
    df['V Vapor'] = df['Z Vapor'] * R * df['T'] / df['P']

    Vc = df['V Liquid'][0]

    df_liquid = pd.DataFrame()
    df_liquid['P'] = df['P']
    df_liquid['V'] = df['V Liquid']
    df_liquid = df_liquid[df_liquid['V'] <= Vc]

    df_vapor = pd.DataFrame()
    df_vapor['P'] = df['P']
    df_vapor['V'] = df['V Vapor']
    df_vapor = df_vapor[(df_vapor['V'] >= Vc) & (df_vapor['V'] <= (Vc*25))]

    poly_TP = np.poly1d(np.polyfit(df['T'], df['P'], 4))
    poly_VP_liquid = np.poly1d(np.polyfit(df_liquid['V'], df_liquid['P'], 11))
    poly_VP_vapor = np.poly1d(np.polyfit(df_vapor['V'], df_vapor['P'], 5))

    
    return df, df_vapor, df_liquid, poly_TP, poly_VP_liquid, poly_VP_vapor, Vc



def visualize(component, eos_model, node_number):
    
    df, df_vapor, df_liquid, poly_TP, poly_VP_liquid, poly_VP_vapor, Vc = tabulate(component, eos_model, node_number)

    fig, (ax_TP, ax_VP) = plt.subplots(nrows=1, ncols=2 ,figsize=(12,5))
    ax_TP.plot(df['T'], df['P'], 'o',  markersize=3);
    ax_TP.plot(df['T'], poly_TP(df['T']), '-')
    ax_TP.set_xlabel('Temperature (k)');
    ax_TP.set_ylabel('Pressure (bar)');
    ax_TP.set_title(f'T-P Phase Diagram for {component[0].upper()}');

    ax_VP.plot(df_liquid['V'], df_liquid['P'], 'o', markersize=5,);
    ax_VP.plot(df_liquid['V'], poly_VP_liquid(df_liquid['V']), '-', label='Liquid Pressure');
    ax_VP.plot(df_vapor['V'], df_vapor['P'], 'o', markersize=5);
    ax_VP.plot(df_vapor['V'], poly_VP_vapor(df_vapor['V']), '-', label='Vapor Pressure');
    ax_VP.plot(df['V Liquid'][0], df['P'][0], marker='o', markersize=8, label='Critical Point');
    ax_VP.set_xlim(0, Vc*25);
    ax_VP.legend();
    ax_VP.set_xlabel('Molar Volume (cm$^3$/mol)');
    ax_VP.set_ylabel('Pressure (bar)');
    ax_VP.set_title(f'V-P Phase Diagram for {component[0].upper()}');

    plt.show()
    
    return fig