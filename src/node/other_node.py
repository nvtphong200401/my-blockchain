import requests

from node.node import Node


class OtherNode(Node):
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    def send_new_block(self, block: dict) -> requests.Response:
        return self.post(endpoint="block", data=block)
