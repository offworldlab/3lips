from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Associator(ABC):
    """Abstract base class for associators. Any associator should implement the process method."""

    @abstractmethod
    def process(
        self,
        radar_list: List[str],
        radar_data: Dict[str, Any],
        timestamp: int,
    ) -> Dict[str, Any]:
        """Associate detections from 2+ radars.

        Args:
            radar_list (List[str]): List of radars to associate.
            radar_data (Dict[str, Any]): Radar data for list of radars.
            timestamp (int): Timestamp to compute delays at (ms).

        Returns:
            Dict[str, Any]: Associated detections by [hex][radar].

        """
