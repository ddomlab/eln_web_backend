from flask import Flask, request, jsonify, send_from_directory
from flask_cors import cross_origin
import search_process

app = Flask(__name__)
@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

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
    return search_process.rm.get_items_types()[int(cat)-1]

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
        search_process.rm.create_item(data['category'], resource)
        return jsonify({"status": "ok", "received": data})
    
    except Exception as e: # send all errors to the client
        print("Error parsing submission:", e)
        return jsonify({"status": "error", "error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
