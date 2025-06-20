from pathlib import Path

root_path = Path(__file__).resolve().parent.parent
logs_path = root_path / "logs"
data_file = f"{root_path}/data/operations.xlsx"
user_settings = f"{root_path}/user_settings.json"
