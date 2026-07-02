import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "system_status_monitor" / "app"))

import health


class HealthDimensionsTest(unittest.TestCase):
    def test_health_dimensions_use_requested_order_and_names(self):
        stats = {
            "cpu": {"percent": 10, "count": 4},
            "memory": {"percent": 20},
            "disks": [{"mount": "host", "percent": 30}],
            "load": {"load1": 0.5},
            "temperature": 45,
        }
        result = health.calculate(stats, {"latency_ms": 20})
        names = [item["name"] for item in result["dimensions"]]

        self.assertEqual(
            names,
            ["CPU", "CPU温度", "系统负载", "响应延迟", "内存", "磁盘"],
        )


if __name__ == "__main__":
    unittest.main()
