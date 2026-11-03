![image](https://github.com/Homanloo/PEC/assets/118424174/f590a4e2-472c-4afa-ae5b-1f8811cb90cc)

# Phase Equilibrium Calculator - PEC
Phase Equilibrium Calculator (PEC) is an simple web-based tool designed for determining phase equilibrium of multi-component mixtures. PEC boasts a user-friendly Graphical User Interface (GUI) that simplifies the process for users, while also providing an Application Programming Interface (API) ideal for developers and researchers.

Since this project is open source, I would be more than grateful for any contribution to further improve the existing framework for more complex calculation and a wider application range.

**Table of Content**
1. [What is PEC?](#1)
2. [How to use PEC](#2)
3. [Modules](#3)
4. [What is VLE calculations?](#4)
5. [Outputs & Results](#5)
6. [Install PEC on your computer](#6)

## What is PEC?  <a name="1"></a>
PEC can manage simple VLE calculation of multicomponent mixtures that are consistent with the models used in this project, which are the PR and SRK Equations of state (EOS) and have their own limitations. 
In addition to VLE calculations, PEC can be helpful in creating P-x-y and P-T diagrams (also known as phase diagrams or phase envelopes). 

## How to use PEC <a name="2"></a>
There are 3 main ways to use PEC:

 1. Customize and run codes directly using the modules.
 2. Using the GUI designed for the website.
 3. Using "GET" requests via the designed API.

Each module is responsible for a narrow range of tasks, but the results are created by chaining the modules in such a way that the outputs of one module would be fed to the next module as its input.

## Modules <a name="3"></a>
Here is the summary of all the modules in the program:

**properties:**
Contains the essential data required for the calculations. Although only 3 parameter ($T_c$, $P_c$, and $\omega$) are required for all the tasks, there other parameters stored in the data base for future use cases.

**parameters:**
Calculating the desired EOS parameters and preparing all the necessary data for next modules.

**phiCalc:**
Two of the main parameters in the whole phase calculation, which are the Compressibility factor $Z$ and Fugacity  Coefficient $\Phi$, are calculated in this section. Fugacity Coefficient is the core parameter for all the future calculations since $\Phi$ - $\Phi$ Model is being used for Vapor Liquid Equilibrium (VLE) calculations.

**bublP & dewP:**
Evaluation of Bubble Pressure and Dew Pressure is used for P-x-y and P-T graphs and also for initializing the VLE calculation. Thus, this is one of the most important tools in the whole framework.

**vle:**
VLE calculations, which is the objective of this project, would be completed in this section and the results would be filtered and reported.
The output consists of $P_{dew}, P_{bubl}, \nu, x, y$. Other parameters that are used for intermediate calculations are not reported.

**binaryPxy:**
Pressure-Composition graph can be obtained for binary mixtures using this modules. It uses the results of *bubP* and *dewP* moduls to plot the desired phase diagram.

**phaseEnvelope:**
Phase Envelopes or P-T diagrams can be plotted using this module by determining the composition and the desired temperature range.

## What is VLE calculation? <a name="4"></a>
Equilibrium is a condition in which no changes occur in the macroscopic properties of an isolated system with time. At equilibrium, all potentials that may cause change are exactly balanced, so no driving force exists for any change in the system.

Vapor Liquid Equilibrium (VLE) is a subset of phase equilibrium which solely focus on vapor and liquid phase. This subject has a significant rule in chemical engineering as it is widely used for both research and in industry.

By completing VLE calculations successfully, one can obtain vapor/liquid ratio, vapor phase and liquid phase mole fractions, bubble pressure, dew pressure, fugacity coefficients, Z factors, etc.

![VLE_Diagram](https://github.com/Homanloo/PEC/assets/118424174/32161459-4e26-4f13-ad56-e9800651024a)

There are several models and equations for VLE calculations introduced by different sources. The major differences between these models are their precision and complexity. The model of choice in this project however, is the Phi-Phi Model ($\Phi$ - $\Phi$ Model) which requires minimum amount of data and offers an acceptable accuracy.

By using the definition of fugacity one can obtain the equations below:

$$\hat{f}_i^v = \hat{f}_i^l$$

$$y_i P \hat{\Phi}_i^v = x_i P \hat{\Phi}_i^l$$

$$y_i \hat{\Phi}_i^v = x_i \hat{\Phi}_i^l$$

Thus by evaluating $\Phi$ values for each of the phases (vapor and liquid), the composition of each phase and the Vapor Ratio $\nu$ can be obtained.

There are several algorithms to pull off the calculations, but it is strongly recommended to read PennState University's documentation about the VLE calculations using EOS models. This and other useful resources are listed below:

 - [Solutions Algorithms for VLE Problems](https://www.e-education.psu.edu/png520/m17_p4.html)
 - [Cubic EOS Fugacity Expression](https://www.e-education.psu.edu/png520/m16_p6.html)
 - [PT Flash calculation using PR EOS](https://cheguide.com/pt_flash.html#:~:text=PT%20Flash%20calculation%20determines%20split,of%20State%20%28PR%20EOS%29.)
 - [Lee-Kesler method for initial guesses](https://en.wikipedia.org/wiki/Lee%E2%80%93Kesler_method#:~:text=The%20Lee%E2%80%93Kesler%20method%20allows,acentric%20factor%20%CF%89%20are%20known.)

For a deeper understanding of the concept of VLE and phase equilibrium in general, these sources are heavily recommended:

 -  Smith, J. M, Van Ness, H. C, Abbott, Michael M., Swihart, Mark T.; *Introduction To Chemical Engineering Thermodynamics*, 8th Edition, McGraw-Hill Education, 2017.

 - Bruce E. Poling, John M. Prausnitz, John P. O’Connell; *The Properties of Gases And Liquids*, 5th Edition, McGraw-Hill Education, 2004.

 - Stanley M. Walas; *Phase Equilibrium in Chemical Engineering*, Butterworth-Heinemann, 2013.

## Outputs & Results <a name="5"></a>
A few samples of the results and possible outputs of the framework is as follows:

**VLE Calculations:**

![image](https://github.com/Homanloo/PEC/assets/118424174/8f5f85b7-e2f1-4718-a115-84bd68634200)


**P-x-y Diagrams:**

![Figure_2](https://github.com/Homanloo/PEC/assets/118424174/d0ca2560-b5ee-4e4e-857c-768091844177)


**P-T diagrams:**

![Figure_1](https://github.com/Homanloo/PEC/assets/118424174/ff2f9a0c-9c90-4e23-b4e7-cc0e662df22a)



## Install PEC on your computer <a name="6"></a>
If you are a developer and want to customize or work on the existing project yourself, you can install PEC locally and use it on your computer:

 1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and [just](https://github.com/casey/just).
 2. Run `uv sync` in the repository. It creates `.venv` with the locked dependencies (add `--group notebooks` for Jupyter).
 3. Run `just` to list the commands: `just run` starts the site, `just check` runs lint, type check, tests and the audit.


 Now that your virtual environment is ready, you can use the modules directly in your code by cloning the repository to the folder you created the venv, or pasting the project folder manually.
Another way is to create a Django Project and replace the files with the vle.W1 folder in the repository. To do so, after you created the virtual environment, follow the steps below:
1. `cd` to the same directory as you made your VE and use `django-admin startproject vleW1` to start a project.
2. Use `python manage.py startapp vle` and `python manage.py startapp api` to create the apps needed for the project.
3. Replace the entire *web-framework* folder with the folder in the repository.

After you have install the requirements, you can create python files and play with the modules on your own. Here is a simple example:
```  
from phaseEnvelope import plotter
import matplotlib.pyplot as plt
  

z = [0.6, 0.4]
components = ["methanol", "benzene"]
eos_model =  "PR"
T_start =  400
T_finish =  600
T_step =  5
gap_ratio_treshhold =  5

fig =  plotter(components, z, eos_model, T_start, T_finish, T_step, gap_ratio_treshhold)
plt.show()  
```
