from pathlib import Path
from datetime import datetime
import threading

_file_lock = threading.Lock()
DATA_FILLED_PATH = Path(__file__).resolve().parent.parent / "datafilled.txt"


class DataRecorder:
    """
    Appends live test input data filled during test execution into datafilled.txt.
    """

    @classmethod
    def record(cls, module: str, action: str, fields: dict[str, str]) -> None:
        """
        Record a structured entry of data filled into a form during a test run.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "",
            "-" * 80,
            f"TEST RUN RECORD: {timestamp}",
            f"Module:      {module}",
            f"Action:      {action}",
            "Data Filled:",
        ]

        for field_name, field_value in fields.items():
            lines.append(f"  * {field_name:<20}: {field_value}")

        lines.append("-" * 80)
        entry_text = "\n".join(lines) + "\n"

        with _file_lock:
            with open(DATA_FILLED_PATH, mode="a", encoding="utf-8") as f:
                f.write(entry_text)
