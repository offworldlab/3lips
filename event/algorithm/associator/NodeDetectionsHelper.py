import numpy as np
from event.algorithm.geometry.Geometry import Geometry

class NodeDetectionsHelper: # Or place in an appropriate existing class/module

    def has_existing_tracks_in_detection_space(self, new_detection_lla, existing_tracks_map, gating_threshold_m):
        """
        Checks if a new LLA detection falls within the gating distance of any existing ECEF tracks.
        """
        if not existing_tracks_map:
            return False

        new_detection_ecef = np.array(Geometry.lla2ecef(new_detection_lla[0], new_detection_lla[1], new_detection_lla[2]))

        for _, track in existing_tracks_map.items():
            track_pos_ecef = track.state_vector[:3]
            distance_sq = np.sum((new_detection_ecef - track_pos_ecef)**2)
            
            if distance_sq < (gating_threshold_m**2):
                return True
        return False
    
    def _get_node_rx_ecef(self, node_config_dict):
        """ Helper to get RX ECEF from a node's full config dict """
        if not node_config_dict or 'location' not in node_config_dict or 'rx' not in node_config_dict['location']:
            return None
        rx_lla = node_config_dict['location']['rx']
        return np.array(Geometry.lla2ecef(rx_lla['latitude'], rx_lla['longitude'], rx_lla['altitude']))

    def get_nodes_with_overlapping_detection_space(self, current_node_id_key, all_nodes_data, max_effective_range_m):
        """
        Finds nodes with potentially overlapping detection spaces based on RX proximity.
        all_nodes_data is expected to be like radar_dict from event.py: {'node_key': {'config': {...}, 'detection': ...}}
        """
        overlapping_nodes = []
        
        current_node_full_config = all_nodes_data.get(current_node_id_key)
        if not current_node_full_config or 'config' not in current_node_full_config:
            return overlapping_nodes
        
        current_node_rx_ecef = self._get_node_rx_ecef(current_node_full_config['config'])
        if current_node_rx_ecef is None:
            return overlapping_nodes

        for other_node_id_key, other_node_full_data in all_nodes_data.items():
            if other_node_id_key == current_node_id_key:
                continue
            
            if not other_node_full_data or 'config' not in other_node_full_data:
                continue

            other_node_rx_ecef = self._get_node_rx_ecef(other_node_full_data['config'])
            if other_node_rx_ecef is None:
                continue
            
            distance_between_rxs = np.linalg.norm(current_node_rx_ecef - other_node_rx_ecef)
            
            if distance_between_rxs < (2 * max_effective_range_m):
                overlapping_nodes.append(other_node_id_key)
        
        return overlapping_nodes