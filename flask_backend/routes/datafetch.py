from flask import Blueprint, request, jsonify
from services.suppDemand import idlistgen
from services.filter_routing import filtersort

list_bp = Blueprint("listgen",__name__)
filtersort_bp = Blueprint("filter",__name__)

@list_bp.route('/receiver/listings',methods=["POST","GET"])
def listings():
    if request.method =="POST":
        data_list = request.get_json()
        
        newlist = idlistgen(data_list)
        return newlist
    return "POST request not recorded"


@filtersort_bp.route("/receiver/filter",methods=["POST","GET"])
def filterlist():
    print("Route /receiver/filter hit")
    if request.method == "POST":
        data_list = request.get_json()
        print(data_list)
        reslist = filtersort(data_list)
        return reslist
    return "POST request not recorded"

