from vle import outer_loop


def main(input_data):
    """
    Doesn't have any use for any case other than the designed API.
    It filters the recieved data, convert the values, and sent the results.
    
    """
    
    components = input_data['components']
    z = input_data['z']
    T_unit = input_data['T_unit']
    P_unit = input_data['P_unit']
    T = input_data['T']
    P = input_data['P']
    eos_model = input_data['eos_model']
    
    if T_unit == "C":
        T = T + 273.15
    elif T_unit == "F":
        T = (T-32)*(5/9) + 273.15
        
    if P_unit == "atm":
        P = P * 1.01325
    elif P_unit == "kpa":
        P = P / 100
    elif P_unit == "psi":
        P = P * 0.068948
        
    V, x, y, P_bubl, P_dew, message_bubl, message_dew, message_initiate = outer_loop(components, T, P, z, eos_model)
    
    return V, x, y, P_bubl, P_dew, message_bubl, message_dew, message_initiate