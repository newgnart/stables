from typing import Dict, List
from decimal import Decimal


class MetricsProcessor:
    """Process transfer events to calculate metrics."""

    @staticmethod
    def process_transfer_events(events: List[Dict], decimals: int) -> Dict:
        """Process transfer events to calculate total volume and count.

        Args:
            events: List of transfer events from Alchemy API
            decimals: Number of decimals for the token

        Returns:
            Dict containing:
                - total_transfer_volume: Total volume in standard units
                - transfer_count: Number of transfers
        """
        if not events:
            return {"total_transfer_volume": Decimal("0"), "transfer_count": 0}

        total_volume = Decimal("0")
        for event in events:
            # Extract data from event
            data = event.get("data", "0x0")
            # Convert hex data to decimal, considering token decimals
            amount = Decimal(int(data, 16)) / Decimal(10**decimals)
            total_volume += amount

        return {
            "total_transfer_volume": total_volume,
            "transfer_count": len(events),
        }
