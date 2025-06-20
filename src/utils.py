import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Hashable

import pandas as pd
import requests
from dotenv import load_dotenv

from src.config import logs_path, root_path, user_settings

load_dotenv()
api_key = os.getenv("Alpha_Vantage_API_KEY")

logging.basicConfig(
    filename=f"{logs_path}/logs.log",
    encoding="utf-8",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s: %(message)s",
)

logger_util = logging.getLogger("app.utils")


