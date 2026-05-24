#!/usr/bin/env python3
"""One-time Vizio TV pairing. Run once from the backend/ directory."""
import os
import uuid
from dotenv import load_dotenv
from pyvizio import Vizio, DEVICE_CLASS_TV

load_dotenv()
IP = os.environ["VIZIO_IP"]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".tv_token")

vizio = Vizio(str(uuid.uuid4()), IP, "Franz", device_type=DEVICE_CLASS_TV)

pair_data = vizio.start_pair()
pin = input("Enter the PIN shown on your TV: ").strip()
result = vizio.pair(pair_data.ch_type, pair_data.token, pin)

with open(TOKEN_FILE, "w") as f:
    f.write(result.auth_token)

print(f"Paired. Token saved to backend/{TOKEN_FILE}")
