from flask import Flask, request, jsonify, send_from_directory
from flask_cors import cross_origin
import search_process
import eln_packages_common.resourcemanage as resourcemanage

app = Flask(__name__)
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
    return send_from_directory(app.static_folder, "index.html")
@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@app.route("/add_resource_interface")
def add_resource_interface(): 
    return send_from_directory(app.static_folder, "add_resource.html")

@app.route('/search', methods=['POST'])
@cross_origin(origins="http://localhost:8000")
def search():
    data = request.get_json(force=True)  # Parse JSON from body
    CAS = data.get('CAS')
    template = data.get('template')

    print("Search query:", CAS)
    results = search_process.search_and_fill(template, CAS)
    print("Results:", results)
    return jsonify(results)

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

@app.errorhandler(404)
def not_found(e):
    return f"404 Not Found: {request.path}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
