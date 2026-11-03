import matplotlib.pyplot as plt
import numpy as np
from bublP import bubble_P
from dewP import dew_P


def phase_envelope(components, z, eos_model, T_start, T_finish, T_step, gap_ratio_treshhold):
    """
    Calculating the required data to plot the phase envelope.

    Args:
        components (list): List of components.
        z (list): Mole fraction of the mixture.
        eos_model (str): EoS model.
        T_start (float): Starting point of the calculations.
        T_finish (float): End point of the calculations.
        T_step (inr): Temperature step.
        gap_ratio_treshhold (int): Used for fault detection in the system. Default value 5. Change if necessary.

    """
    
    T_list = np.arange(T_start, T_finish, T_step)
    bublP_list = []
    dewP_list = []

    for i in T_list:
        bp = bubble_P(components, i, z, eos_model)[2]
        dp = dew_P(components, i, z, eos_model)[2]
        bublP_list.append(bp)
        dewP_list.append(dp)

    # Check if the data near critical region is OK or not.
    for i in range(len(bublP_list)):
        if i > 0.1*(round((T_finish-T_start)/T_step)):
            previous_change = bublP_list[i-1] - bublP_list[i-2]
            if (-bublP_list[i] + bublP_list[i-1]) > gap_ratio_treshhold * previous_change:
                bublP_list_new = bublP_list[:i-1]
                break
            else:
                bublP_list_new = bublP_list
                
    for i in range(len(dewP_list)):
        if i > 0.1*(round((T_finish-T_start)/T_step)):
            previous_change = dewP_list[i-1] - dewP_list[i-2]
            if (-dewP_list[i] + dewP_list[i-1]) > gap_ratio_treshhold * previous_change:
                dewP_list_new = dewP_list[:i-1]
                break
            else:
                dewP_list_new = dewP_list

    return bublP_list_new, dewP_list_new, T_list
    
    
    
def plotter(components, z, eos_model, T_start, T_finish, T_step, gap_ratio_treshhold):
    
    bublP_list_new, dewP_list_new, T_list = phase_envelope(components, z, eos_model, T_start, T_finish, T_step, gap_ratio_treshhold)
    
    P_max_bubl = max(bublP_list_new)
    P_max_dew = max(dewP_list_new)
    T_max_bubl = T_list[bublP_list_new.index(P_max_bubl)]
    T_max_dew = T_list[dewP_list_new.index(P_max_dew)]
    
    fig, ax = plt.subplots()
    ax.plot(T_list[:len(dewP_list_new)], dewP_list_new, label='Dew Line', marker = 'x', markersize=3)
    ax.plot(T_list[:len(bublP_list_new)], bublP_list_new, label='Bubble Line', marker = 'o', markersize=3)
    ax.plot([T_max_bubl, T_max_dew], [P_max_bubl, P_max_dew], label = 'Critical Region')

    if len(components) == 2:
        bp1, dp1, t1 = phase_envelope(components, [1, 0], eos_model, T_start, T_finish, T_step, gap_ratio_treshhold)
        bp2, dp2, t2 = phase_envelope(components, [0, 1], eos_model, T_start, T_finish, T_step, gap_ratio_treshhold)
        
        ax.plot(t1[:len(dp1)], dp1, label=components[0], marker = 's', markersize=3)
        ax.plot(t2[:len(dp2)], dp2, label=components[1], marker = 's', markersize=3)
    
    plt.text(0.99, 0.01, f"{components[0]}: {z[0]}", ha='right', va='bottom', transform=ax.transAxes)
    ax.set_title(f'Phase Envelope of {", ".join(f"{i}" for i in components)}')
    ax.set_xlabel("Temperature (k)")
    ax.set_ylabel("Pressure (bar)")
    ax.legend()
    ax.grid()
    
    return fig