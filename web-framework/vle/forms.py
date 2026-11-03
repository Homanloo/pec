from django import forms

from .brain.properties import prop

keys = prop.keys()
COMPONENTS_LIST = ()
for i in keys:
    temp = (i, i)
    COMPONENTS_LIST = (temp,) + COMPONENTS_LIST

COMPONENTS_LIST = reversed(COMPONENTS_LIST)    
    
class ComponentForm(forms.Form):
    Components = forms.MultipleChoiceField(choices=COMPONENTS_LIST, 
                                           label="Components",
                                           required=True, 
                                           widget=forms.SelectMultiple(attrs={"multiselect-search":"true"}))

class UnitForm(forms.Form):
    TEMP_UNITS = (
        ("K", "Kelvin"),
        ("C", "Celsius"),
        ("F", "Fahrenheit"),
    )
    PRES_UNITS = (
        ("bar", "bar"),
        ("atm", "atm"),
        ("kpa", "kilo Pascal"),
        ("psi", "psi") 
    )
    T_units = forms.ChoiceField(choices=TEMP_UNITS, label="Temperature Unit", required=True)
    P_units = forms.ChoiceField(choices=PRES_UNITS, label="Pressure Unit", required=True)
 
 
class EosModel(forms.Form):
    EoS_MODELS = (
        ("PR", "Peng-Robinson"),
        ("SRK", "Soave-Redlich-Kwong")
     )
    Eos_model = forms.ChoiceField(choices=EoS_MODELS, label="EoS Model", required=True)
    
    
class ValueForm(forms.Form):
    T_value = forms.FloatField(min_value=-274, label= "Temperature Value", required=True)
    P_value = forms.FloatField(min_value=0, label= "Pressure Value", required=True)
    
    
class CompositionForm(forms.Form):
    Composition = forms.CharField(label="Composition", required=True)
    
    
class NodeForm(forms.Form):
    Node_number = forms.IntegerField(min_value=5, max_value=100, label="Number of Calculation Nodes", required=True, initial=20)
    
    
class TemperatureForm(forms.Form):
    TEMP_UNITS = (
    ("K", "Kelvin"),
    ("C", "Celsius"),
    ("F", "Fahrenheit"),
    )
    T_units = forms.ChoiceField(choices=TEMP_UNITS, label="Temperature Unit", required=True)    
    T_value = forms.FloatField(min_value=-274, label= "Temperature Value", required=True)
    
    
class EnvelopeTemp(forms.Form):
    TEMP_UNITS = (
    ("K", "Kelvin"),
    ("C", "Celsius"),
    ("F", "Fahrenheit"),
    )
    T_units = forms.ChoiceField(choices=TEMP_UNITS, label="Temperature Unit", required=True)
    T_value_start = forms.FloatField(min_value=-274, label= "Temperature Start Value", required=True)
    T_value_end = forms.FloatField(min_value=-274, label= "Temperature End Value", required=True)
    T_step = forms.IntegerField(min_value=5, max_value=100, label="Temperature Step", required=True)
    
    
class GapForm(forms.Form):
    Gap = forms.IntegerField(min_value=1, max_value=30, label="Gap Ratio Threshold", required=True, initial=5)