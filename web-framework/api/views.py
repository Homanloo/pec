import json

from django.http import JsonResponse

from .brain import main


def get(request):
    
    if request.method == 'GET':
        input_data = json.loads(request.body)
        try:
            V, x, y, P_bubl, P_dew, message_bubl, message_dew, message_initiate = main.main(input_data)
            try:
                V = round(V, 4)
            except Exception:
                pass
            try:
                x = list(x)
                x = [round(i, 4) for i in x]
            except Exception:
                pass
            try:
                y = list(y)
                y = [round(i, 4) for i in y]
            except Exception:
                pass
            try:
                P_bubl = round(P_bubl, 4)
            except Exception:
                pass
            try:
                P_dew = round(P_dew, 4)
            except Exception:
                pass
            Message = "Calculations completed without any error."
            response = {
                "Message": Message,
                "message_bubl": message_bubl,
                "message_dew": message_dew,
                "message_initiate": message_initiate,
                "V": V,
                "x": x,
                "y": y,
                "P_bubl": P_bubl,
                "P_dew": P_dew,
            }
        
        except Exception:
            Message = "Caclculations can not be procced. Inputs are either invalid or in the wrong format."
            response = {
                "Message": Message
            }
            
    return JsonResponse(response)