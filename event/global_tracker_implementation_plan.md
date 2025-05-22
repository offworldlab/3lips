# MVP Tracker Integration Guide for 3lips event.py

This document outlines the minimal necessary modifications to `event/event.py` in the 3lips project to integrate a basic system-level tracker. The goal is to achieve a Minimum Viable Product (MVP) for tracking, where the system can initiate, update (rudimentarily), and manage a list of tracks based on localised detections.

This guide assumes you have:
1.  Created `event/algorithm/track/Track.py` defining the `Track` data structure.
2.  Created `event/algorithm/track/Tracker.py` defining the `Tracker` class with methods like `update_all_tracks()`.

## I. Modifying `event.py`

The core idea is to collect all localised points from the various active API request configurations within a single scan, feed them to a global tracker instance, and then append the resulting system tracks to the output of each API request.

### Step 1: Imports and Initialization

1.  **Import `Tracker`**:
    At the top of `event.py`, add the import statement for your `Tracker` class.

    ```python
    # ... existing imports ...
    from algorithm.geometry.Geometry import Geometry

    # --- Tracker Integration ---
    from algorithm.track.Tracker import Tracker # Import the Tracker class
    # --- End Tracker Integration ---
    ```

2.  **Load Tracker Configuration from Environment Variables**:
    Instead of reading from `config/config.yml`, load tracker configuration from environment variables. Use Python's `os.environ` to access these variables, and provide sensible defaults if not set.

    ```python
    import os
    # ... existing code ...

    # Tracker config from environment variables
    tracker_config_params = {
        "verbose": os.environ.get("TRACKER_VERBOSE", "False").lower() == "true",
        "max_misses_to_delete": int(os.environ.get("TRACKER_MAX_MISSES_TO_DELETE", 5)),
        "min_hits_to_confirm": int(os.environ.get("TRACKER_MIN_HITS_TO_CONFIRM", 3)),
        # Add other parameters as needed, e.g.:
        "gating_euclidean_threshold_m": float(os.environ.get("TRACKER_GATING_EUCLIDEAN_THRESHOLD_M", 10000.0)),
        "initial_pos_uncertainty_ecef_m": [float(x) for x in os.environ.get("TRACKER_INITIAL_POS_UNCERTAINTY_ECEF_M", "500.0,500.0,500.0").split(",")],
        "initial_vel_uncertainty_ecef_mps": [float(x) for x in os.environ.get("TRACKER_INITIAL_VEL_UNCERTAINTY_ECEF_MPS", "100.0,100.0,100.0").split(",")],
        "dt_default_s": float(os.environ.get("TRACKER_DT_DEFAULT_S", 1.0)),
    }
    verbose_tracker = tracker_config_params["verbose"]
    ```
    
    **Note**: Set these environment variables in your Docker Compose file, shell, or deployment environment. For example, in your `docker-compose.yml`:
    
    ```yaml
    environment:
      - TRACKER_VERBOSE=true
      - TRACKER_MAX_MISSES_TO_DELETE=5
      - TRACKER_MIN_HITS_TO_CONFIRM=2
      - TRACKER_GATING_EUCLIDEAN_THRESHOLD_M=10000.0
      - TRACKER_INITIAL_POS_UNCERTAINTY_ECEF_M=500.0,500.0,500.0
      - TRACKER_INITIAL_VEL_UNCERTAINTY_ECEF_MPS=100.0,100.0,100.0
      - TRACKER_DT_DEFAULT_S=1.0
    ```

3.  **Initialize Global Tracker Instance**:
    After initializing other algorithm instances, create a single instance of your `Tracker`.

    ```python
    # ... (init adsbAssociator, ellipseParametricMean, etc.) ...

    # --- Tracker Integration: Initialize Global Tracker ---
    global_tracker = Tracker(config=tracker_config_params)
    # --- End Tracker Integration ---
    ```

### Step 2: Modify the Main `event()` Loop

The `event()` function needs to be restructured to accommodate the global tracker.

```python
async def event():
  """
  Main event processing loop.
  Fetches data, processes each API request configuration, updates global tracks,
  and prepares output.
  """
  global api, save, global_tracker # Make sure global_tracker is accessible

  timestamp = int(time.time()*1000) # Current timestamp in milliseconds
  api_event_configs_this_cycle = copy.deepcopy(api) # Process a snapshot

  if not api_event_configs_this_cycle:
    if verbose_tracker: # Use the verbose flag loaded from config
        print(f"{timestamp}: No active API requests. Tracker will predict only.")
    if global_tracker:
        # Call tracker even with no detections to allow prediction and lifecycle management
        _ = global_tracker.update_all_tracks([], timestamp) 
    return

  # 1. Aggregate unique radar names (as before)
  radar_names = []
  for item_config in api_event_configs_this_cycle:
    if "server" in item_config and isinstance(item_config["server"], list):
      for radar_url_name in item_config["server"]:
        radar_names.append(radar_url_name)
  radar_names = list(set(radar_names))

  # 2. Fetch data from all unique radars (detections & config - as before)
  radar_dict = {}
  # ... (existing logic for fetching radar_detections_data and radar_config_data) ...
  # ... (populate radar_dict) ...
  
  # 3. Fetch ADS-B truth data (as before)
  truth_adsb = {}
  # ... (existing logic for populating truth_adsb) ...

  # --- Processing Starts ---
  all_localised_points_for_tracker_input_this_scan = []
  processed_api_request_outputs = [] 
  # Use a set of tuples to store unique points (lat, lon, alt) to avoid duplicates
  unique_lla_points_for_tracker_keys = set() 

  # --- Pass 1: Process each API request config & Collect Localised Points for Tracker ---
  for item_config in api_event_configs_this_cycle:
    item_processing_start_time = time.time()
    
    item_radars = item_config.get("server", [])
    if not isinstance(item_radars, list): item_radars = [item_radars]

    radar_dict_item = { # Data for this specific API request's servers
        key: radar_dict.get(key)
        for key in item_radars
        if key in radar_dict and radar_dict.get(key) is not None
    }

    # Handle cases where radar_dict_item might be empty or lack necessary data
    if not radar_dict_item or not any(radar_dict_item.get(r) and radar_dict_item[r].get("config") for r in item_radars):
        print(f"Skipping item {item_config.get('hash')} due to missing radar data/config for its servers.")
        temp_output = item_config.copy()
        temp_output["timestamp_event"] = timestamp
        temp_output["error"] = "Missing radar data/config for configured servers."
        # Add other default fields to ensure consistent structure if needed by API client
        temp_output["detections_associated"] = {}
        temp_output["detections_localised"] = {}
        temp_output["ellipsoids"] = {}
        temp_output["truth"] = {}
        temp_output["time"] = 0
        processed_api_request_outputs.append(temp_output)
        continue
        
    # Select associator & localisation_algorithm (as before)
    # ... (existing logic for selecting associator and localisation_algorithm) ...
    # Ensure localisation_algorithm is selected or handle error
    localisation_id = item_config.get("localisation")
    localisation_algorithm = None # Assign based on localisation_id as in your full code
    # (Simplified for brevity - refer to your complete event.py for full selection logic)
    if localisation_id == "ellipse-parametric-mean": localisation_algorithm = ellipseParametricMean
    elif localisation_id == "spherical-intersection": localisation_algorithm = sphericalIntersection
    # ... add other algorithms
    else:
        print(f"Error: Localisation algorithm '{localisation_id}' invalid for item {item_config.get('hash')}.")
        # Populate a default error output for this item
        error_output = item_config.copy()
        error_output.update({
            "timestamp_event": timestamp, "error": f"Invalid localisation: {localisation_id}",
            "detections_associated": {}, "detections_localised": {}, "ellipsoids": {},
            "truth": truth_adsb.get(item_config.get("adsb"), {}), "time": 0
        })
        processed_api_request_outputs.append(error_output)
        continue

    # Perform item-specific association (as before)
    associated_dets = adsbAssociator.process(item_radars, radar_dict_item, timestamp)

    # Prepare for localisation (as before)
    # ... (logic for associated_dets_3_radars, associated_dets_2_radars) ...
    input_for_localisation = associated_dets # Or associated_dets_3_radars depending on algo

    # Perform item-specific localisation
    localised_dets_for_item = localisation_algorithm.process(input_for_localisation, radar_dict_item)

    # --- Collect unique localised points for the global tracker ---
    for target_id, data_dict in localised_dets_for_item.items():
      if 'points' in data_dict and data_dict['points']:
        for point_lla in data_dict['points']: # point_lla is [lat, lon, alt]
          if isinstance(point_lla, list) and len(point_lla) == 3:
            # Create a unique key for the point to avoid duplicates
            point_key_tuple = (round(point_lla[0], 4), round(point_lla[1], 4), round(point_lla[2], 1))
            if point_key_tuple not in unique_lla_points_for_tracker_keys:
              unique_lla_points_for_tracker_keys.add(point_key_tuple)
              all_localised_points_for_tracker_input_this_scan.append({
                  'lla_position': point_lla,
                  'timestamp_ms': timestamp, # Use current scan timestamp
                  # Optional: add source info for debugging the tracker later
                  'source_api_hash': item_config.get("hash", "unknown_item"),
                  'source_target_id': target_id 
              })
          elif verbose_tracker:
              print(f"Skipping malformed point for tracker input: {point_lla}")


    # Calculate ellipsoids for display (item-specific - as before)
    ellipsoids_for_item = {}
    # ... (existing logic for populating ellipsoids_for_item) ...

    item_processing_stop_time = time.time()

    # Store results for this specific API request configuration (without system_tracks yet)
    output_for_this_item = item_config.copy()
    output_for_this_item["timestamp_event"] = timestamp
    output_for_this_item["truth"] = truth_adsb.get(item_config.get("adsb"), {})
    output_for_this_item["detections_associated"] = associated_dets
    output_for_this_item["detections_localised"] = localised_dets_for_item
    output_for_this_item["ellipsoids"] = ellipsoids_for_item
    output_for_this_item["time"] = item_processing_stop_time - item_processing_start_time
    
    if verbose_tracker:
        print(f"{timestamp}: Item {item_config.get('hash')} Method: {localisation_id}, Time: {output_for_this_item['time']:.4f}s", flush=True)

    processed_api_request_outputs.append(output_for_this_item)

  # --- Pass 2: Update Global Tracker with all unique localised points from this scan ---
  current_system_tracks_map = {} # Will hold {track_id: TrackObject}
  if global_tracker:
    if verbose_tracker:
        print(f"{timestamp}: Updating global_tracker with {len(all_localised_points_for_tracker_input_this_scan)} unique LLA points.")
    current_system_tracks_map = global_tracker.update_all_tracks(
        all_localised_points_for_tracker_input_this_scan, 
        timestamp # Pass current scan timestamp
    )
  
  serializable_system_tracks = [track.to_dict() for track in current_system_tracks_map.values()]
  if verbose_tracker and serializable_system_tracks:
      print(f"{timestamp}: Global System Tracks ({len(serializable_system_tracks)} generated): {[t['track_id'] for t in serializable_system_tracks]}", flush=True)


  # --- Pass 3: Augment each API request's output with the global system tracks & Manage API list ---
  final_api_list_for_this_cycle = []
  
  for processed_item_output in processed_api_request_outputs:
    # Check if the original API request config (identified by hash) should still be active
    item_hash = processed_item_output.get("hash")
    # Find the original config from the snapshot taken at the start of the cycle
    original_config = next((item_cfg for item_cfg in api_event_configs_this_cycle if item_cfg.get("hash") == item_hash), None)

    if original_config and (timestamp - original_config.get("timestamp", 0) <= tDelete * 1000):
        processed_item_output["system_tracks"] = serializable_system_tracks # Add global tracks
        final_api_list_for_this_cycle.append(processed_item_output)
    elif verbose_tracker and original_config: # Only print if original_config was found but timed out
        print(f"{timestamp}: API Config {item_hash} (orig_ts: {original_config.get('timestamp', 'N/A')}) timed out. Not including in final output.")
    elif verbose_tracker and not original_config: # Should not happen if processed_api_request_outputs is derived from api_event_configs_this_cycle
        print(f"{timestamp}: Warning - Processed item {item_hash} not found in original configs for timeout check.")

  # Update the global `api` list with the results from the current cycle for requests that are still active.
  api = final_api_list_for_this_cycle

  if save and api: # Only save if there's something to save
    append_api_to_file(api)
  elif save and not api and verbose_tracker:
    print(f"{timestamp}: Save is true, but 'api' list is empty. Nothing to save.")

# ... (rest of event.py: main(), append_api_to_file(), short_hash(), callback_message_received(), message_api_request init, if __name__ == "__main__":)
# Ensure the if __name__ == "__main__": block correctly starts the listener and runs asyncio.run(main())
# Also, make the listener_thread a daemon thread and add graceful shutdown.

In the if __name__ == "__main__": block, make these adjustments for better execution:

if __name__ == "__main__":
  # Start the TCP listener in a separate thread
  listener_thread = threading.Thread(target=message_api_request.start_listener, daemon=True)
  listener_thread.start()
  
  # Run the main asyncio event loop
  try:
    print("Starting 3lips event processor...")
    asyncio.run(main())
  except KeyboardInterrupt:
    print("Event loop stopped by user.")
  finally:
    if message_api_request and hasattr(message_api_request, 'server_socket') and message_api_request.server_socket:
        message_api_request.close_listener()
    print("3lips event processor shut down.")
```

Step 3: Modify callback_message_received (Minor Adjustment)
Ensure the callback_message_received correctly handles the api list and provides verbose logging if enabled. The existing logic for adding/updating API request configurations in the api list is mostly fine.

```
async def callback_message_received(msg):
  global api, verbose_tracker # Ensure verbose_tracker is accessible
  timestamp_receipt = int(time.time()*1000)
  msg_hash = short_hash(msg)
  output_for_client = {}

  existing_item = next((item for item in api if item.get("hash") == msg_hash), None)

  if existing_item:
    existing_item["timestamp"] = timestamp_receipt # Update timestamp
    output_for_client = json.dumps(existing_item) # Send back current state
    if verbose_tracker:
        print(f"{timestamp_receipt}: Updated timestamp for existing API config: {msg_hash}")
  else:
    new_api_item = {"hash": msg_hash, "timestamp": timestamp_receipt}
    try:
        # ... (existing parsing logic for msg into new_api_item) ...
        # Ensure "server" is a list
        if "server" in new_api_item and not isinstance(new_api_item["server"], list):
            new_api_item["server"] = [new_api_item["server"]]
        
        api.append(new_api_item)
        output_for_client = json.dumps(new_api_item) # Send back the new config representation
        if verbose_tracker:
            print(f"{timestamp_receipt}: Added new API config: {msg_hash} - {new_api_item}")
    except ValueError as e:
        print(f"Error parsing API request message '{msg}': {e}")
        output_for_client = json.dumps({"error": "Invalid API request format", "request": msg})
  
  return output_for_client
  ```

II. MVP Testing Strategy
For an MVP, the goal is to verify that the tracker is being called, tracks are being initiated (even if crudely), and their data appears in the output. Sophisticated track accuracy is not the primary concern for the MVP.

**Configure Environment Variables:**

Set the following environment variables (in your shell, Docker Compose, or deployment environment):

```
TRACKER_VERBOSE=true
TRACKER_MAX_MISSES_TO_DELETE=5   # Number of scans before deleting a track with no updates
TRACKER_MIN_HITS_TO_CONFIRM=2    # Number of updates to confirm a tentative track
TRACKER_GATING_EUCLIDEAN_THRESHOLD_M=10000.0 # Large gate for MVP
TRACKER_INITIAL_POS_UNCERTAINTY_ECEF_M=500.0,500.0,500.0
TRACKER_INITIAL_VEL_UNCERTAINTY_ECEF_MPS=100.0,100.0,100.0
TRACKER_DT_DEFAULT_S=1.0
```

Set `3lips: save: true` to inspect the output NDJSON files.

Prepare Track.py and Tracker.py for MVP:

Track.py: Ensure to_dict() serializes basic track info (ID, status, current state, hits, misses, age).

Tracker.py:

Focus on:

__init__: Loads config.

update_all_tracks(): Main loop.

_predict_tracks(): Can be very simple (e.g., no change or rudimentary constant velocity if no KF yet).

_convert_localised_detections_to_measurements(): Converts LLA to ECEF. Covariance can be a fixed large diagonal matrix for MVP.

_data_association(): For MVP, even a very simple "assign first detection to first track" or a basic nearest neighbor within a large gate is okay to see the flow. The provided Tracker.py has a greedy assignment.

_initiate_new_track(): Creates a Track object with an initial state (position from detection, zero velocity) and a large initial covariance.

_manage_track_lifecycle(): Basic promotion (tentative -> confirmed) and deletion logic.

Crucially for MVP: The Kalman Filter integration can be simplified or stubbed out. The Track.update() method in Tracker.py can directly use the associated measurement to update the track's position, perhaps with some blending with the predicted position, rather than a full KF update. The goal is to see tracks being created and roughly following detections.

Run 3lips:

Start the Docker containers: sudo docker compose up --build

Observe the console output of the 3lips-event container: sudo docker logs -f 3lips-event

Send API Requests:

Use a tool like curl or Postman, or your browser, to send an API request to http://localhost:49156/api?... with at least one radar server specified.
Example: http://localhost:49156/api?server=radar4.30hours.dev&associator=adsb-associator&localisation=ellipse-parametric-mean&adsb=adsb.30hours.dev
(Replace with your actual radar node URLs if testing with live/simulated data).

Monitor Logs and Output:

Console Logs (3lips-event):

Look for print statements from event.py and Tracker.py (if verbose: true).

"{timestamp}: No active API requests. Tracker will predict only." (if no API calls made yet).

"{timestamp}: Updating global_tracker with {N} unique LLA points."

"{timestamp}: Global System Tracks ({M} generated): [...]"

Messages from Tracker.py about track initiation, prediction, association, confirmation, deletion.

Crucially, ensure there are no Python tracebacks.

API Response / Saved NDJSON (/app/save/*.ndjson inside the container):

The JSON output for your API request should now contain a system_tracks key.

The value should be a list of dictionaries, where each dictionary is a serialized Track object from its to_dict() method.

MVP Checks for system_tracks:

Are tracks being initiated when new, unassociated localised points appear? (Check for new track IDs).

Does a track's hits count increase when it's updated with a detection?

Does a track's status change from tentative to confirmed after min_hits_to_confirm?

If you stop providing detections that would associate with a track, does its misses count increase?

Does the track get removed from system_tracks after max_misses_to_delete?

Is the timestamp_update_ms changing?

Is the position in current_state_vector roughly corresponding to the input detections (even if the velocity components are zero or crudely estimated for MVP)?

Basic Scenarios to Test (MVP Focus):

Single, Persistent Target: Send data that should result in one consistent set of localised points over several scans.

Expected: One track initiated, becomes confirmed, hits increase, misses stay low.

Target Disappears: After establishing a track, stop sending data that would localise to its position.

Expected: Track misses increase, track eventually deleted.

New Target Appears: Introduce data for a second, distinct target.

Expected: A new track is initiated for the second target, while the first (if still getting detections) continues.

Visualisation (Highly Recommended, even for MVP if possible):

The simplest way is to modify api/map/event/radar.js (or create a new track.js and include it in api/map/index.html).

Fetch the system_tracks array from the API response.

For each track in system_tracks:

Extract the LLA position (e.g., from track['current_state_vector'] if your Track.to_dict() and state vector are structured for it, or convert ECEF from state vector to LLA using Geometry.js if you adapt it for Cesium).

Use Cesium's viewer.entities.add to plot a simple point for each track's current position. You could color-code by status or use the track ID as a label.

This visual feedback is invaluable for quickly seeing if tracks are forming where expected and roughly following the data.

This MVP approach focuses on getting the data flowing through the new Tracker and seeing basic track lifecycle management. The quality of tracking (accuracy, handling of complex scenarios) will be primitive but provides the foundation for future improvements like Kalman filtering and more advanced data association.


This Markdown document provides a step-by-step guide for the `event.py` modifications and a clear testing strategy for an MVP implementation of tracking in 3lips. It emphasizes verifying the flow and basic lifecycle over sophisticated tracking performance at this stage.
