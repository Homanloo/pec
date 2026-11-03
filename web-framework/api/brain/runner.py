import matplotlib.pyplot as plt
from phaseEnvelope import plotter

z = [0.5, 0.5]
components = ["propane", "n-butane"]
eos_model = "PR"
T_start = 300
T_finish = 600
T_step = 2
gap_ratio_treshhold = 5

fig = plotter(components, z, eos_model, T_start, T_finish, T_step, gap_ratio_treshhold)

plt.show()