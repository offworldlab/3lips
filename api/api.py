"""@file api.py
@brief API for 3lips.
@author 30hours
"""

import json
import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)

from common.Message import Message

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize configuration from environment variables
radar_data = []
radar_names = os.getenv("RADAR_NAMES", "")
radar_urls = os.getenv("RADAR_URLS", "")

if radar_names and radar_urls:
    radar_names_list = [name.strip() for name in radar_names.split(",") if name.strip()]
    radar_urls_list = [url.strip() for url in radar_urls.split(",") if url.strip()]
    if len(radar_names_list) != len(radar_urls_list):
        print(
            f"[ERROR] Number of RADAR_NAMES ({len(radar_names_list)}) does not match RADAR_URLS ({len(radar_urls_list)})",
            flush=True,
        )
    else:
        for name, url in zip(radar_names_list, radar_urls_list):
            radar_data.append({"name": name, "url": url})
        radar_list_str = [f"{r['name']}@{r['url']}" for r in radar_data]
        print(f"[INFO] Loaded {len(radar_data)} radars: {radar_list_str}", flush=True)
else:
    print("[WARNING] RADAR_NAMES or RADAR_URLS not set or empty.", flush=True)

map_data = {
    "location": {
        "latitude": float(os.getenv("MAP_LATITUDE", -34.9286)),
        "longitude": float(os.getenv("MAP_LONGITUDE", 138.5999)),
    },
    "center_width": int(os.getenv("MAP_CENTER_WIDTH", 50000)),
    "center_height": int(os.getenv("MAP_CENTER_HEIGHT", 40000)),
    "tar1090": os.getenv("TAR1090_URL", "localhost:5001"),
}

# store state data
servers = []
for radar in radar_data:
    if radar["name"] and radar["url"]:
        servers.append({"name": radar["name"], "url": radar["url"]})

associators = [{"name": "ADSB Associator", "id": "adsb-associator"}]

localisations = [
    {"name": "Ellipse Parametric (Mean)", "id": "ellipse-parametric-mean"},
    {"name": "Ellipse Parametric (Min)", "id": "ellipse-parametric-min"},
    {"name": "Ellipsoid Parametric (Mean)", "id": "ellipsoid-parametric-mean"},
    {"name": "Ellipsoid Parametric (Min)", "id": "ellipsoid-parametric-min"},
    {"name": "Spherical Intersection", "id": "spherical-intersection"},
    {"name": "RETINA Solver", "id": "retina-solver"},
]

adsbs = [
    {"name": map_data["tar1090"], "url": map_data["tar1090"]},
    {"name": "synthetic-adsb:5001", "url": "synthetic-adsb:5001"},
    {"name": "None", "url": ""},
]

# store valid ids
valid = {}
valid["servers"] = [item["url"] for item in servers]
valid["associators"] = [item["id"] for item in associators]
valid["localisations"] = [item["id"] for item in localisations]
valid["adsbs"] = [item["url"] for item in adsbs]


# message received callback
async def callback_message_received(msg):
    print(f"Callback: Received message in main.py: {msg}", flush=True)


# init messaging
event_host = os.environ.get("EVENT_HOST", "127.0.0.1")
message_api_request = Message(event_host, 6969)


@app.route("/")
def index():
    # Configure tile servers with proper HTTPS
    tile_servers = {
        "esri": os.getenv(
            "TILE_SERVER_ESRI",
            "tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        "mapbox_streets": os.getenv(
            "TILE_SERVER_MAPBOX_STREETS",
            "tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        "mapbox_dark": os.getenv(
            "TILE_SERVER_MAPBOX_DARK",
            "tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        "opentopomap": os.getenv(
            "TILE_SERVER_OPENTOPOMAP",
            "tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        "esri_satellite": os.getenv(
            "TILE_SERVER_ESRI_SATELLITE",
            "server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        ),
        "google_satellite": os.getenv(
            "TILE_SERVER_GOOGLE_SATELLITE",
            "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        ),
    }
    
    app_config = {
        "map": {
            "location": {
                "latitude": float(os.getenv("MAP_LATITUDE", -34.9286)),
                "longitude": float(os.getenv("MAP_LONGITUDE", 138.5999)),
            },
            "center_width": int(os.getenv("MAP_CENTER_WIDTH", 50000)),
            "center_height": int(os.getenv("MAP_CENTER_HEIGHT", 40000)),
            "tile_server": ensure_tile_server_https(tile_servers),
            "tar1090": os.getenv("TAR1090_URL", "localhost:5001"),
        },
    }
    
    # Translate container URLs to localhost URLs for browser
    browser_servers = translate_container_to_browser_urls(servers)
    browser_adsbs = []
    for adsb in adsbs:
        browser_adsb = adsb.copy()
        browser_adsb["url"] = browser_adsb["url"].replace("synthetic-adsb:", "localhost:")
        browser_adsbs.append(browser_adsb)
    
    return render_template(
        "index.html",
        servers=browser_servers,
        associators=associators,
        localisations=localisations,
        adsbs=browser_adsbs,
        app_config=app_config,
        config_json=json.dumps(app_config),
    )


# serve static files from the /app/public folder
@app.route("/public/<path:file>")
def serve_static(file):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    public_folder = os.path.join(base_dir, "public")
    return send_from_directory(public_folder, file)


def translate_browser_to_container_urls(url_list, url_type="server"):
    """Translate localhost URLs from browser to container URLs for internal processing"""
    translated = []
    for url in url_list:
        # Translate localhost URLs to container URLs
        container_url = url.replace("localhost:", "synthetic-adsb:")
        translated.append(container_url)
    return translated

def translate_container_to_browser_urls(server_list):
    """Translate container URLs to localhost URLs for browser consumption"""
    browser_servers = []
    for server in server_list:
        browser_server = server.copy()
        # Translate synthetic-adsb container URLs to localhost URLs
        browser_server["url"] = browser_server["url"].replace("synthetic-adsb:", "localhost:")
        browser_servers.append(browser_server)
    return browser_servers

def ensure_tile_server_https(tile_config):
    """Ensure tile server URLs have https:// prefix"""
    for key, url in tile_config.items():
        if url and not url.startswith(('http://', 'https://')):
            tile_config[key] = f"https://{url}"
    return tile_config

@app.route("/api")
def api():
    api = request.query_string.decode("utf-8")
    # input protection
    servers_api = request.args.getlist("server")
    associators_api = request.args.getlist("associator")
    localisations_api = request.args.getlist("localisation")
    adsbs_api = request.args.getlist("adsb")
    
    # Translate localhost URLs to container URLs for internal validation and processing
    servers_translated = translate_browser_to_container_urls(servers_api, "server")
    adsbs_translated = translate_browser_to_container_urls(adsbs_api, "adsb")
    
    print(f"[DEBUG] Original servers: {servers_api}", flush=True)
    print(f"[DEBUG] Translated servers: {servers_translated}", flush=True)
    print(f"[DEBUG] Valid servers list: {valid['servers']}", flush=True)
    
    if not all(item in valid["servers"] for item in servers_translated):
        print(f"[DEBUG] Server validation failed for translated: {servers_translated}", flush=True)
        return "Invalid server"
    if not all(item in valid["associators"] for item in associators_api):
        return "Invalid associator"
    if not all(item in valid["localisations"] for item in localisations_api):
        return "Invalid localisation"
    if not all(item in valid["adsbs"] for item in adsbs_translated):
        return "Invalid ADSB"
    
    # Reconstruct API query string with translated container URLs for event processing
    api_parts = []
    for server in servers_translated:
        api_parts.append(f"server={server}")
    for adsb in adsbs_translated:
        api_parts.append(f"adsb={adsb}")
    for assoc in associators_api:
        api_parts.append(f"associator={assoc}")
    for loc in localisations_api:
        api_parts.append(f"localisation={loc}")
    
    translated_api = "&".join(api_parts)
    
    # send to event handler
    try:
        print(f"Sending original API request: {api}", flush=True)
        print(f"Sending translated API request: {translated_api}", flush=True)
        reply_chunks = message_api_request.send_message(translated_api)
        print("Got reply_chunks generator", flush=True)
        reply = "".join(reply_chunks)
        print(f"Final reply: {reply}", flush=True)
        # Parse the JSON string and return it as proper JSON response
        import json
        try:
            reply_data = json.loads(reply)
            return jsonify(reply_data)
        except json.JSONDecodeError:
            # If it's not valid JSON, return as-is with JSON error wrapper
            return jsonify({"error": "Invalid JSON response", "raw": reply})
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Exception occurred: {e}", flush=True)
        print(f"Traceback: {error_trace}", flush=True)
        reply = "Exception: " + str(e)
        return jsonify(error=reply), 500


@app.route("/map/<path:file>")
def serve_map(file):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    public_folder = os.path.join(base_dir, "map")
    response = send_from_directory(public_folder, file)
    
    # Add no-cache headers for JavaScript files to prevent browser caching during development
    if file.endswith('.js'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response


# handle /cesium/ specifically
@app.route("/cesium/")
def serve_cesium_index():
    return redirect("/cesium/index.html")


@app.route("/cesium/<path:file>")
def serve_cesium_content(file):
    cesium_host = os.environ.get("CESIUM_HOST", "127.0.0.1")
    apache_url = f"http://{cesium_host}:8080/" + file
    try:
        response = requests.get(apache_url, timeout=10)
        if response.status_code == 200:
            return Response(
                response.content,
                content_type=response.headers["content-type"],
            )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from Apache server: {e}")
    return Response(
        "Error fetching content from Apache server",
        status=500,
        content_type="text/plain",
    )


if __name__ == "__main__":
    app.run()
