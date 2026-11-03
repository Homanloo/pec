import numpy as np

from .properties import prop


def component_properties(components, T, eos_model):
    if isinstance(components, list):
        omega = []
        Tc = []
        Pc = []
        for i in components:
            omega.append(prop[i]['omega'])
            Tc.append(prop[i]['Tc'])
            Pc.append(prop[i]['Pc'])

        R = 83.14       #Gas Constant = [cm^3 bar / mol k]
        Pc = np.array(Pc)
        omega = np.array(omega)
        Tc = np.array(Tc)   
        Tr = T/Tc
        
        if eos_model == "PR":
            sigma = 1 + np.sqrt(2)
            epsilon = 1 - np.sqrt(2)
            Omega = 0.07780
            Psi = 0.45724
            alpha = (1 + (0.37464 + 1.54226*omega - 0.2992*(omega)**2) * (1 - (Tr)**0.5))**2
            
        elif eos_model == "SRK":
            sigma = 1
            epsilon = 0
            Omega = 0.08664
            Psi = 0.42748
            alpha = (1 + (0.480 + 1.547*omega - 0.176*(omega)**2) * (1 - (Tr)**0.5))**2
        
        a_i = Psi*R**2*Tc**2/Pc
        b_i = Omega*R*Tc/Pc
        
        parameters = {"Pc" : Pc, "Tc" : Tc, "Tr" : Tr, "omega" : omega, "sigma" : sigma,
                      "epsilon" : epsilon, "Omega" : Omega, "Psi" : Psi, "alpha" : alpha,
                      "a_i" : a_i, "b_i" : b_i}
        
        return parameters
    
    
def eos_properties(components, T, P, z, eos_model):
    
    R = 83.14
    parameters = component_properties(components, T, eos_model)
    a_i = parameters['a_i']
    b_i = parameters['b_i']
    alpha = parameters['alpha']

    if len(components) >= 2:
        aa_i = alpha*a_i
        aa_ij = np.sqrt(np.outer(np.reshape(aa_i, (-1,1)), aa_i))
        zz = np.outer(np.reshape(z, (-1,1)), z)
                
        aa_m = 0
        n = np.shape(zz)[0]
        for i in range(n):
            for j in range(n):
                aa_m += z[i]*z[j] * np.sqrt(aa_i[i]*aa_i[j])
                
        b_m = np.dot(z, b_i)
        
        AA_i = (2/aa_m)*np.sum(aa_ij*z, axis=1)
        BB_i = b_i/b_m
        
        # Applying the mixing rule
        A = (aa_m*P)/(R*T)**2
        B = (b_m*P)/(R*T)
                
    elif len(components) == 1:
        A = (alpha*a_i*P)/(R**2 * T**2)
        B = (b_i*P)/(R*T)
        AA_i = 0
        BB_i = 1
            
    return A, B, AA_i, BB_i