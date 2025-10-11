from flask import Blueprint, request, jsonify
from services.suppDemand import idlistgen
from services.filter_routing import filtersort
# from services.utils import send_to_express

list_bp = Blueprint("listgen", __name__)
filtersort_bp = Blueprint("filter", __name__)

@list_bp.route('/receiver/listings', methods=["POST", "GET"])
def listings():
    if request.method == "POST":
        data_list = request.get_json()
        newlist = idlistgen(data_list)
        return jsonify(newlist)
    return "POST request not recorded"


@filtersort_bp.route("/receiver/filter", methods=["POST","GET"])
def filterlist():
    print("Route /receiver/filter hit")
    if request.method == "POST":
        try:
            data_list = request.get_json()
            print("Received from frontend:", data_list)

            # Apply your filtering logic
            reslist = filtersort(data_list)
            print("Filter results:", reslist)

            # Extract donation IDs
            filtered_donation_ids = [item["_id"] for item in reslist]
            print("Filtered donation IDs:", filtered_donation_ids)

            # Prepare data to send to Express
            # Send to Express
            # express_response = send_to_express(reslist)
            print("Response from Express:", reslist)

            # Return both Flask & Express response summary to caller
            return jsonify(reslist), 200

        except Exception as e:
            print(f"Error in filterlist: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to filter donations'
            }), 500

    return jsonify({
        'success': False,
        'error': 'Only POST method is supported'
    }), 405
