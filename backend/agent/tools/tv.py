import os
from langchain_core.tools import tool
from pyvizio import Vizio, DEVICE_CLASS_TV
from dotenv import load_dotenv

_TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".tv_token")
_ENV_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".env")


def _tv() -> Vizio:
    load_dotenv(_ENV_FILE)
    ip = os.getenv("VIZIO_IP")
    if not ip:
        raise RuntimeError("VIZIO_IP not set in backend/.env")
    try:
        with open(_TOKEN_FILE) as f:
            token = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError("TV not paired. Run `python backend/pair_tv.py` first.")
    return Vizio("franz", ip, "Franz", token, DEVICE_CLASS_TV)


@tool
def tv_power(action: str = "toggle") -> str:
    """Control the living room TV power. action: 'on', 'off', or 'toggle'."""
    print(f"[tv_power] action={action!r}")
    try:
        vizio = _tv()
        a = action.lower()
        if a == "on":
            result = vizio.pow_on()
        elif a == "off":
            result = vizio.pow_off()
        else:
            result = vizio.pow_toggle()
        print(f"[tv_power] result={result}")
        if result is None:
            return f"TV did not respond to power {action} (check connection or token)."
        return f"TV turned {action}."
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        print(f"[tv_power] exception={e}")
        return f"Could not reach TV: {e}"


@tool
def tv_volume(action: str, amount: int = 5) -> str:
    """Control the living room TV volume.

    action: 'up', 'down', 'mute', 'unmute', 'mute_toggle', or 'set'
    amount: steps for 'up'/'down', or target level (0-100) for 'set'
    """
    print(f"[tv_volume] action={action!r} amount={amount}")
    try:
        vizio = _tv()
        a = action.lower()

        if a == "up":
            result = vizio.vol_up(amount)
        elif a == "down":
            result = vizio.vol_down(amount)
        elif a == "mute":
            result = vizio.mute_on()
        elif a == "unmute":
            result = vizio.mute_off()
        elif a == "mute_toggle":
            result = vizio.mute_toggle()
        elif a == "set":
            current = vizio.get_current_volume()
            if current is None:
                return "Could not read current volume."
            delta = amount - current
            if delta > 0:
                result = vizio.vol_up(delta)
            elif delta < 0:
                result = vizio.vol_down(abs(delta))
            else:
                return f"Volume is already at {amount}."
        else:
            return f"Unknown action '{action}'. Use: up, down, mute, unmute, mute_toggle, set."

        print(f"[tv_volume] result={result}")
        if result is None:
            return "TV did not respond (check connection or token)."
        return f"Volume {action}."
    except RuntimeError as e:
        return str(e)
    except Exception as e:
        print(f"[tv_volume] exception={e}")
        return f"Could not reach TV: {e}"
