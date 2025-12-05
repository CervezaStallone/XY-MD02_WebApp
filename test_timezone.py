"""Test timezone conversie"""
import pandas as pd
from datetime import datetime

# Simuleer wat er gebeurt
ts = int(datetime.now().timestamp())
print(f"Nu (lokaal): {datetime.now()}")
print(f"Timestamp: {ts}")
print(f"Conversie (oud): {pd.to_datetime(ts, unit='s')}")
print(f"Conversie (nieuw): {pd.to_datetime(ts, unit='s').tz_localize('UTC').tz_convert('Europe/Amsterdam').tz_localize(None)}")
