import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import cross_origin
import print_handling
import pth_data
from datetime import datetime
import json
import search_process
import eln_packages_common.resourcemanage as resourcemanage
import label_creating
from bottle_ocr import bottle_ocr_bp

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "pth_data.csv")

app.register_blueprint(bottle_ocr_bp)
    

def rm():
    """
    Initialize the Resource_Manager with the API key from cookies.
    This function is called in each route that requires it.
    """
    key = request.cookies.get("apiKey")
    if key is None:
        raise ValueError("No API key provided")
    return resourcemanage.Resource_Manager(key=key)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, "index.html") # type: ignore
@app.route('/favicon.ico', methods=['GET'])
def favicon():
    # return send_from_directory(app.static_folder, 'favicon.ico') # type: ignore   
    return jsonify({"status": "ok", "message": "favicon.ico not available"}), 404
@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@app.route("/add_resource_interface")
def add_resource_interface(): 
    return send_from_directory(app.static_folder, "add_resource.html") # type: ignore
@app.route("/label_gen_interface")
def label_gen_interface(): 
    return send_from_directory(app.static_folder, "label_gen.html") # type: ignore
@app.route('/create_label', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def create_label():
    data = request.get_json(force=True)
    title = data.get('Title', '')
    text = data.get('Text', '')
    icon = data.get('Icon', None)
    qr_type = data.get('QRContentType', None)
    qr_content = data.get('QRContent', None)
    height = data.get('Height', 18)

    if qr_type == "Resource":
        qr_content = "https://eln.ddomlab.org/database.php?mode=view&id=" + str(qr_content)
    if icon == "QR Code":
        icon = None
    if icon == "None":
        icon = None
    label_creating.print_label(
        caption=title,
        longcaption=text,
        icon=icon,
        codecontent=qr_content,
        height=height
    )
    return send_from_directory(app.static_folder, "print.pdf") # type: ignore

    
    


@app.route('/search', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def search():
    data = request.get_json(force=True)  # Parse JSON from body
    CAS = data.get('CAS')
    template = data.get('template')

    print("Search query:", CAS)
    try:
        results = search_process.search_and_fill(template, CAS)
    except ValueError as e:
        print("Error in search_and_fill:", e)
        return jsonify({"error": str(e)}), 400
    print("Results:", results)
    return jsonify(results)


@app.route('/print', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def print_registry():
    data = request.get_json()
    ids = data.get('id', [])
    if len(ids) == 0:
        return jsonify({"error": "No IDs provided"}), 400
    if not isinstance(ids, list):
        return jsonify({"error": "Expected a list of IDs"}), 400

    print_handling.add_item([int(x) for x in ids])
    print("Printing items with IDs:", ids)
    
    return send_from_directory(app.static_folder, "print.pdf") # type: ignore

@app.route('/associate', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def associate():
    data = request.get_json()
    ids = data.get('id', [])
    exp_id = data.get('exp_id')
    if len(ids) == 0:
        return jsonify({"error": "No IDs provided"}), 400
    rmn = rm()
    if not isinstance(ids, list):
        return jsonify({"error": "Expected a list of IDs"}), 400
    for id in ids:
        rmn.experiment_item_link(exp_id, id)
    return ("Success", 200, {"exp_name": rmn.get_experiment(exp_id)["title"]})

@app.route('/mark_open', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def mark_open():
    data = request.get_json()
    ids = data.get('id', [])
    if len(ids) == 0:
        return jsonify({"error": "No IDs provided"}), 400
    rmn = rm()
    if not isinstance(ids, list):
        return jsonify({"error": "Expected a list of IDs"}), 400
    for id in ids:
        body = rmn.get_item(id)
        metadata = json.loads(body["metadata"])
        if metadata["extra_fields"]["Opened"]["value"] != "":
            return jsonify({ "error" : f"Item {id} already marked as opened on {metadata['extra_fields']['Opened']['value']}"}), 400
        metadata["extra_fields"]["Opened"]["value"] = datetime.now().isoformat()[:10]
        rmn.change_item(id, {"metadata": json.dumps(metadata), "status": 4})
    return "Success", 200

@app.route('/change_location', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def change_location():
    data = request.get_json()
    ids = data.get('id', [])
    if len(ids) == 0:
        return jsonify({"error": "No IDs provided"}), 400
    rmn = rm()
    if not isinstance(ids, list):
        return jsonify({"error": "Expected a list of IDs"}), 400
    for id in ids:
        body = rmn.get_item(id)
        metadata = json.loads(body["metadata"])
        metadata["extra_fields"]["Location"]["value"] = data.get('location', "")
        rmn.change_item(id, {"metadata": json.dumps(metadata), "status": 4})
    return "Success", 200

# @app.route('/change_sublocation', methods=['POST'])
# @cross_origin(origins="http://localhost:8000")
# def change_sublocation():
#     data = request.get_json()
#     ids = data.get('id', [])
#     if len(ids) == 0:
#         return jsonify({"error": "No IDs provided"}), 400
#     rmn = rm()
#     if not isinstance(ids, list):
#         return jsonify({"error": "Expected a list of IDs"}), 400
#     for id in ids:
#         # body = rmn.get_item(id)
#         # metadata = json.loads(body["metadata"])
#         # new_field = {
#         #     "Sublocation":
#         #         {
#         #             "value": data.get('sublocation', "err"),
#         #             "type": "text",
#         #             "description": "This optional sublocation field can be used to specify a precise location of this item (shelf, drawer, bin, etc.). "
#         #             "This field is optional, and may not be entirely accurate. It is inteded to serve as a hint, not a definitive location."
#         #         }
#         # }
#         # metadata["extra_fields"].update(new_field)
#         # rmn.change_item(id, {"metadata": json.dumps(metadata)})
#     return "Success", 200

@app.route('/mark_empty', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def mark_empty():
    data = request.get_json()
    ids = data.get('id', [])
    if len(ids) == 0:
        return jsonify({"error": "No IDs provided"}), 400
    rmn = rm()
    if not isinstance(ids, list):
        return jsonify({"error": "Expected a list of IDs"}), 400
    for id in ids:
        rmn.change_item(id, {"status": 5})
    return "Success", 200

@app.route('/template', methods=['GET'])
@cross_origin(origins="http://localhost:8000")
def get_template():
    cat = request.args.get('category')
    if cat is None:
        return jsonify({})
    try:
        return rm().get_items_types()[int(cat)-1]
    except Exception as e:
        print("Error initializing Resource_Manager:", e)
        return jsonify({"status": "error", "error": str(e)}), 400
@app.route('/add_resource', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def add_resource():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            raise ValueError("Expected top-level JSON object")
        
        # At this point, `data` is a plain Python dict
        # print("Received form submission:", data)
        resource = search_process.dict_complexify(data)
        try:
            rm().create_item(data['category'], resource)
            return jsonify({"status": "ok", "received": data})
        except Exception as e:
            print("Error Initializing Resource Manager:", e)
            return jsonify({"status": "error", "error": str(e)}), 400
    
    except Exception as e: # send all errors to the client
        print("Error parsing submission:", e)
        return jsonify({"status": "error", "error": str(e)}), 400
@app.route('/get_locations', methods=['GET'])
@cross_origin(origins="http://localhost:8000")
def get_locations():
    try:
        rmn = rm()
        types = rmn.get_items_types()
        locations = []
        for t in types:
            try:
                locs = json.loads(t["metadata"])["extra_fields"]["Location"]["options"]
            except KeyError:
                locs = []
            # Add only unique locations
            for loc in locs:
                if loc not in locations:
                    locations.append(loc)
        return jsonify(locations)
    except Exception as e:
        print("Error getting locations:", e)
        return jsonify({"status": "error", "error": str(e)}), 400

@app.route('/store_pth_data', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def store_pth_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if pth_data.save_as_csv(CSV_PATH, data):
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500
@app.route('/get_closest_pth_data', methods=['GET'])
@cross_origin(origins="http://localhost:8000")
def get_closest_pth_data():
    target_time = request.args.get('time')  
    if not target_time:
        return jsonify({"error": "No time provided"}), 400
    result = pth_data.get_closest_time(CSV_PATH, target_time)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "No matching data found"}), 404

@app.errorhandler(404)
def not_found(e):
    return f"404 Not Found: {request.path}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
