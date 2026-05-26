"""Client to DALIA website."""

import pystow

from dalia_dif.dif13 import EducationalResourceDIF13


class Client:
    def __init__(self):
        self.token = pystow.get_config("dalia", "token", raise_on_missing=True)
        self.email = pystow.get_config("dalia", "email", raise_on_missing=True)

    def upload_dif13(self, r: EducationalResourceDIF13) -> None:
        """Upload a learning resource to DALIA."""
        raise NotImplementedError
