import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_file = os.path.join(BASE_DIR, "food_donation_model.pkl")

from .SDModel import FoodDonationPredictor
from flask import jsonify

model = FoodDonationPredictor()
model.load_model(model_file)

def changefeat(data_list:list)->list:
    for donor in data_list.get("donor", []):
        donor["avg_customers_served"] = donor.pop("serving")

def idlistgen(idlist)->list:
    changefeat(idlist)
    donorlist = idlist.get("donor",[])
    receiver = idlist.get("receiver", {})
    newlist = []
    for user in donorlist:
        res = model.predict_both(user,receiver)
        if "match_probability" not in res or not isinstance(res["match_probability"], (int, float)):
            res["match_probability"] = 0
        newlist.append(res)

    reslist = sorted(newlist, key=lambda x: x["match_probability"], reverse=True)
    print(reslist)
    return jsonify(reslist)



# lml = [
#             {
#             'Id':"Hx4567",
#             'day_of_week': 'Saturday',
#             'avg_customers_served': 350,
#             'past_donation_count': 12
#             },
#             {
#             'Id':"Bx4567",
#             'day_of_week': 'Tuesday',
#             'avg_customers_served': 140,
#             'past_donation_count': 8
#             }
#       ]
# idlistgen(lml)