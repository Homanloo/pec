from django.shortcuts import render
from .forms import ComponentForm, CompositionForm, UnitForm, ValueForm, EosModel, NodeForm, TemperatureForm, EnvelopeTemp, GapForm
from .brain import main, binaryPxy, phaseEnvelope
import numpy as np

# Create your views here.

def home(request):
    return render(request, "home.html")


def vle(request):
    component_form = ComponentForm(request.POST or None, prefix="component_form")
    composition_form = CompositionForm(request.POST or None, prefix="composition_form")
    unit_form = UnitForm(request.POST or None, prefix="unit_form")
    value_form = ValueForm(request.POST or None, prefix="value_form")
    eos_form = EosModel(request.POST or None, prefix="eos_form")
    
    Components = None
    Composition = None
    Temperature_unit = None
    Pressure_unit = None
    Tempreture_value = None
    Pressure_value = None
    Eos_model = None
    
    x = None
    y = None
    V = None
    P_bubl = None
    P_dew = None
    
    message_bubl = ""
    message_dew = ""
    message_initiate = ""
    Message = ""
    
    result_status = 0
    
    if request.method == 'POST':
        if component_form.is_valid() == False:
            Message = "Please choose the components correctly!"
        elif composition_form.is_valid() == False:
            Message = "Please choose the composition correctly!"
        elif unit_form.is_valid() == False:
            Message = "Please choose the units correctly!"
        elif value_form.is_valid() == False:
            Message = "Please choose the values correctly!"
        elif eos_form.is_valid() == False:
            Message = "Please choose the EoS Model correctly!"
        else:
            Message = "Data format OK. Starting the calculations..."
            Components = component_form.cleaned_data['Components']
            Composition = composition_form.cleaned_data['Composition']
            Temperature_unit = unit_form.cleaned_data['T_units']
            Pressure_unit = unit_form.cleaned_data['P_units']
            Tempreture_value = value_form.cleaned_data['T_value']
            Pressure_value = value_form.cleaned_data['P_value']
            Eos_model = eos_form.cleaned_data['Eos_model']
            
            if any(c.isalpha() for c in Composition) == False:
                Composition = [float(i) for i in Composition.split()]
                input_data = {
                    "components": Components,
                    "z": Composition,
                    "T_unit": Temperature_unit,
                    "P_unit": Pressure_unit,
                    "T": Tempreture_value,
                    "P": Pressure_value,
                    "eos_model": Eos_model,
                    }
                
                try:            
                    V, x, y, P_bubl, P_dew, message_bubl, message_dew, message_initiate = main.main(input_data)
                    result_status = 1
                except:
                    Message = "System is NOT defined!"
                    result_status = 2
                
                
            elif any(c.isalpha() for c in Composition) == True:
                Message = "Enter the composition input with the right format."
    
    if result_status == 1:
        try:
            V = np.round(V, 4)  # ty: ignore[no-matching-overload]  (None when a step failed)
        except:
            pass
        try:
            x = np.round(x, 4)  # ty: ignore[no-matching-overload]  (None when a step failed)
        except:
            pass
        try:
            y = np.round(y, 4)  # ty: ignore[no-matching-overload]  (None when a step failed)
        except:
            pass
        try:
            P_bubl = np.round(P_bubl, 4)  # ty: ignore[no-matching-overload]  (None when a step failed)
        except:
            pass
        try:
            P_dew = np.round(P_dew, 4)  # ty: ignore[no-matching-overload]  (None when a step failed)
        except:
            pass
        
    context = {
        "component_form": component_form,
        "composition_form": composition_form,
        "unit_form": unit_form,
        "value_form": value_form,
        "eos_form": eos_form,
        
        "components": Components,
        "composition": Composition,
        "T_unit": Temperature_unit,
        "P_unit": Pressure_unit,
        "T_value": Tempreture_value,
        "P_value": Pressure_value,
        "eos_model": Eos_model,
        
        "V": V,
        "x": x,
        "y": y,
        "P_bubl": P_bubl,
        "P_dew": P_dew,
        "message_bubl": message_bubl,
        "message_dew":message_dew,
        "message_initiate": message_initiate,
        "Message": Message,
        "result_status": result_status,
    }
                
    return render(request, "vle.html", context)



def pxy(request):

    component_form = ComponentForm(request.POST or None, prefix="component_form")
    temp_form = TemperatureForm(request.POST or None, prefix="temp_form")
    eos_form = EosModel(request.POST or None, prefix="eos_form")
    node_form = NodeForm(request.POST or None, prefix="node_form")
    
    Components = None
    Temperature_unit = None
    Tempreture_value = None
    Eos_model = None
    Node_number = None
    fig = None
    df = None
    Message = ""
    
    result_status = 0
    
    if request.method == 'POST':
        if component_form.is_valid() == False:
            Message = "Please choose the components correctly!"
        elif temp_form.is_valid() == False:
            Message = "Please choose the values correctly!"
        elif eos_form.is_valid() == False:
            Message = "Please choose the EoS Model correctly!"
        elif node_form.is_valid() == False:
            Message = "Please choose Node Number correctly!"
        else:
            Message = "Data format OK. Starting the calculations..."
            Components = component_form.cleaned_data['Components']
            Temperature_unit = temp_form.cleaned_data['T_units']
            Tempreture_value = temp_form.cleaned_data['T_value']
            Eos_model = eos_form.cleaned_data['Eos_model']
            Node_number = node_form.cleaned_data['Node_number']
            
            if Temperature_unit == "C":
                Tempreture_value = Tempreture_value + 273.15
            elif Temperature_unit == "F":
                Tempreture_value = (Tempreture_value-32)*(5/9) + 273.15
            
            if len(Components) > 2:
                Message = "Please choose only 2 components."
                result_status = 2
            elif len(Components) == 2:
                try:            
                    fig, df = binaryPxy.visualize(Components, Tempreture_value, Eos_model, Node_number)
                    result_status = 1
                except:
                    Message = "System is NOT defined!"
                    result_status = 2

    print(Message)  
    context = {
        "component_form": component_form,
        "temp_form": temp_form,
        "eos_form": eos_form,
        "node_form": node_form,
        
        "components": Components,
        "T_unit": Temperature_unit,
        "T_value": Tempreture_value,
        "eos_model": Eos_model,
        "node_number": Node_number,
        
        "fig": fig,
        "df": df,
        "result_status": result_status,
        "message": Message,
    }
                
    return render(request, "pxy.html", context)





def pt(request):
    
    component_form = ComponentForm(request.POST or None, prefix="component_form")
    temp_form = EnvelopeTemp(request.POST or None, prefix="temp_form")
    composition_form = CompositionForm(request.POST or None, prefix="eos_form")
    eos_form = EosModel(request.POST or None, prefix="eos_form")
    gap_form = GapForm(request.POST or None, prefix="eos_form")
        
    Components = None
    Composition = None
    Temperature_unit = None
    Temperature_start = None
    Temperature_end = None
    Temperature_step = None
    Eos_model = None
    fig = None
    Message = ""
    
    result_status = 0
    
    if request.method == 'POST':
        if component_form.is_valid() == False:
            Message = "Please choose the components correctly!"
        elif composition_form.is_valid() == False:
            Message = "Please choose the composition correctly!"
        elif temp_form.is_valid() == False:
            Message = "Please choose the values correctly!"
        elif eos_form.is_valid() == False:
            Message = "Please choose the EoS Model correctly!"
        elif gap_form.is_valid() == False:
            Message = "Please choose Gap Ratio Threshold correctly!"
        else:
            Message = "Data format OK. Starting the calculations..."
            Components = component_form.cleaned_data['Components']
            Composition = composition_form.cleaned_data['Composition']
            Temperature_unit = temp_form.cleaned_data['T_units']
            Temperature_start = temp_form.cleaned_data['T_value_start']
            Temperature_end = temp_form.cleaned_data['T_value_end']
            Temperature_step = temp_form.cleaned_data['T_step']
            Eos_model = eos_form.cleaned_data['Eos_model']
            Gap = gap_form.cleaned_data['Gap']
            
            if Temperature_unit == "C":
                Temperature_start = Temperature_start + 273.15
                Temperature_end = Temperature_end + 273.15
            elif Temperature_unit == "F":
                Temperature_start = (Temperature_start-32)*(5/9) + 273.15
                Temperature_end = (Temperature_end-32)*(5/9) + 273.15
            
            if any(c.isalpha() for c in Composition) == False:
                Composition = [float(i) for i in Composition.split()]
                try:            
                    fig = phaseEnvelope.plotter(Components, Composition, Eos_model, Temperature_start, Temperature_end, Temperature_step, Gap)
                    result_status = 1
                except:
                    Message = "System is NOT defined!"
                    result_status = 2
                    
            elif any(c.isalpha() for c in Composition) == True:
                Message = "Enter the composition input with the right format."

    context = {
        "component_form": component_form,
        "composition_form": composition_form,
        "temp_form": temp_form,
        "eos_form": eos_form,
        "gap_form": gap_form,        

        
        "fig": fig,
        "result_status": result_status,
        "message": Message,
    }
     
    return render(request, "pt.html", context)




def api(request):
    return render(request, "api.html")



def docs(request):
    return render(request, "docs.html")


