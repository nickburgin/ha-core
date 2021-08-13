"""WiZ Device UDP communication."""
import json
import socket

WIZ_PORT = 38899


class WizDevice:
    """WiZ Smart device."""

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host
        self.dimming = 100
        self.state = False

    async def connect(self) -> bool:
        """Test if we can poll the host."""

        pilot = self.get_pilot()

        if pilot != {}:
            return True
        else:
            return False

    def name(self) -> str:
        return self.host

    def turn_on(self) -> None:
        self.set_pilot({"state": True, "dimming": self.dimming})

    def turn_off(self) -> None:
        self.set_pilot({"state": False})

    def set_brightness(self, value) -> None:
        self.dimming = (value / 256 * 100) | int

    def is_on(self) -> bool:
        return self.state

    def brightness(self) -> int:
        return (self.dimming / 100 * 256) | int

    def update(self) -> None:
        pilot_data = self.get_pilot()
        self.state = pilot_data["result"]["state"]
        self.dimming = pilot_data["result"]["dimming"]

    async def mac_address(self) -> str:
        """Get a unique name from the device."""

        pilot_data = self.get_pilot()

        return pilot_data["result"]["mac"]

    def get_pilot(self) -> str:
        return self.remote_call("getPilot")

    def set_pilot(self, KW_ARGS) -> str:
        return self.remote_call("setPilot", KW_ARGS)

    def remote_call(self, method, params={}) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        s.sendto(
            json.dumps({"method": method, "params": params}).encode("utf-8"),
            (self.host, WIZ_PORT),
        )

        data, _ = s.recvfrom(WIZ_PORT)

        return json.loads(data.decode("utf-8"))
