import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .bublP import bubble_P


def tabulate(components, T, EoS_model, node_number):
    
    P_list = []
    y_list = []
    x_list = []

    step = 1/node_number
    x1 = np.arange(0, 1 + step, step)
    for i in x1:
        x_i = [i, 1-i]
        x_list.append(x_i)
    x_list = np.array(x_list)

    for i in x_list:    
        try:
            if np.array_equal(i, x_list[0]):
                status, message, P_final, y_final = bubble_P(components, T, i, EoS_model)
                P_list.append(P_final)
                y_list.append(y_final)
            else:
                status, message, P_final, y_final = bubble_P(components, T, i, EoS_model)
                P_list.append(P_final)
                y_list.append(y_final)
        except Exception:
            continue
    
    df1 = pd.DataFrame()
    df1['x1'] = [i[0] for i in x_list]
    df1['x2'] = 1 - df1['x1']

    df2 = pd.DataFrame()
    df2['y1'] = [i[0] for i in y_list]
    df2['y2'] = 1 - df2['y1']

    df3 = pd.DataFrame()
    df3['P'] = P_list

    df = pd.concat([df1, df2], axis=1)
    df = pd.concat([df, df3], axis=1)
    df.dropna(inplace=True)
            
    return df



def visualize(components, T, EoS_model, node_number):
    
    df = tabulate(components, T, EoS_model, node_number)
    
    fig, ax = plt.subplots(1,2, figsize=(10,4))

    ax[0].plot(df['x1'], df['P'], label='x', marker='o')
    ax[0].plot(df['y1'], df['P'], label='y', marker='x')
    ax[0].set_xlabel("x1, y1")
    ax[0].set_ylabel("P (bar)")
    ax[0].set_title(f'{components[0]} - {components[1]} at T = {T} K')
    ax[0].grid()
    ax[0].legend()


    x_eq = np.linspace(0, 1, num=10, endpoint=True)
    y_eq = x_eq
    x_plot_max = df['x1'].max()
    y_plot_max = df['y1'].max()
    ax[1].set_xlim(0,x_plot_max)
    ax[1].set_ylim(0,y_plot_max)
    ax[1].plot(df['x1'], df['y1'], label='Calculated', marker='o')
    ax[1].plot(x_eq, y_eq, label='x=y')
    ax[1].set_xlabel("x1")
    ax[1].set_ylabel("y1")
    ax[1].set_title(f'{components[0]} - {components[1]} at T = {T} K')
    ax[1].grid()
    ax[1].legend()
    
    return fig, df
