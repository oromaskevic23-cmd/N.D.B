import json
import unittest
from unittest.mock import patch

from ndb_verify.__main__ import (
    ADDRESS, ReadOnlyRPC, VerificationError, decode_string, format_units, observe, quantity
)


def uint(n):
    return "0x" + n.to_bytes(32, "big").hex()


def abi_string(value):
    data = value.encode()
    return "0x" + (32).to_bytes(32, "big").hex() + len(data).to_bytes(32, "big").hex() + data.hex() + "00" * ((-len(data)) % 32)


class FakeRPC:
    def __init__(self):
        self.calls = []
        self.chain = "0x89"
        self.code = "0x6000"
        self.hashes = ["0x" + "ab" * 32, "0x" + "ab" * 32]
        self.values = {
            "0x06fdde03": abi_string("New Digital Bitcoin"),
            "0x95d89b41": abi_string("NDB"),
            "0x313ce567": uint(18),
            "0x18160ddd": uint(1_000_000_000 * 10**18),
        }

    def call(self, method, params):
        self.calls.append((method, params))
        if method == "eth_chainId":
            return self.chain
        if method == "eth_blockNumber":
            return "0x123"
        if method == "eth_getBlockByNumber":
            return {"number": "0x123", "hash": self.hashes.pop(0)}
        if method == "eth_getCode":
            return self.code
        if method == "eth_call":
            return self.values[params[0]["data"]]
        raise AssertionError("Unexpected method " + method)


class ObservationTests(unittest.TestCase):
    def test_observation_is_block_anchored_and_read_only(self):
        rpc = FakeRPC()
        report = observe(rpc)
        self.assertEqual(report["contract"], ADDRESS)
        self.assertEqual(report["chain_id"], 137)
        self.assertEqual(report["block_number"], 291)
        self.assertEqual(report["total_supply_tokens"], "1000000000")
        self.assertEqual(report["symbol"], "NDB")
        self.assertEqual(report["bytecode_size_bytes"], 2)
        self.assertEqual([method for method, _ in rpc.calls], [
            "eth_chainId", "eth_blockNumber", "eth_getBlockByNumber", "eth_getCode",
            "eth_call", "eth_call", "eth_call", "eth_call", "eth_getBlockByNumber"
        ])
        for method, params in rpc.calls:
            if method in ("eth_getCode", "eth_call"):
                self.assertEqual(params[-1], "0x123")

    def test_wrong_chain_stops_before_contract_queries(self):
        rpc = FakeRPC()
        rpc.chain = "0x1"
        with self.assertRaisesRegex(VerificationError, "not Polygon"):
            observe(rpc)
        self.assertEqual(len(rpc.calls), 1)

    def test_empty_code_stops(self):
        rpc = FakeRPC()
        rpc.code = "0x"
        with self.assertRaisesRegex(VerificationError, "No contract bytecode"):
            observe(rpc)
        self.assertFalse(any(method == "eth_call" for method, _ in rpc.calls))

    def test_block_hash_change_stops(self):
        rpc = FakeRPC()
        rpc.hashes[1] = "0x" + "cd" * 32
        with self.assertRaisesRegex(VerificationError, "Block hash changed"):
            observe(rpc)

    def test_malformed_abi_stops(self):
        rpc = FakeRPC()
        rpc.values["0x06fdde03"] = "0x01"
        with self.assertRaises(VerificationError):
            observe(rpc)

    def test_decimal_range_stops(self):
        rpc = FakeRPC()
        rpc.values["0x313ce567"] = uint(256)
        with self.assertRaisesRegex(VerificationError, "decimals"):
            observe(rpc)

    def test_string_length_is_bounded(self):
        oversized = "0x" + (32).to_bytes(32, "big").hex() + (4097).to_bytes(32, "big").hex()
        with self.assertRaises(VerificationError):
            decode_string(oversized)

    def test_exact_supply_format(self):
        self.assertEqual(format_units(1000500, 6), "1.0005")
        self.assertEqual(format_units(0, 18), "0")
        self.assertEqual(format_units(12, 0), "12")

    def test_quantity_rejects_leading_zero(self):
        with self.assertRaises(VerificationError):
            quantity("0x00")


class TransportTests(unittest.TestCase):
    def test_method_allowlist_rejects_transaction(self):
        rpc = ReadOnlyRPC("https://example.org")
        with patch("urllib.request.build_opener") as network:
            with self.assertRaisesRegex(VerificationError, "allowlist"):
                rpc.call("eth_sendRawTransaction", ["0x1234"])
            network.assert_not_called()

    def test_url_credentials_and_insecure_transport_are_rejected(self):
        for url in ("http://example.org", "https://user:pass@example.org"):
            with self.subTest(url=url), self.assertRaises(VerificationError):
                ReadOnlyRPC(url)

    def test_json_rpc_error_does_not_leak_server_message(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return None
            def read(self, _):
                return json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"message": "SECRET"}}).encode()
        with patch("urllib.request.build_opener") as opener:
            opener.return_value.open.return_value = Response()
            with self.assertRaises(VerificationError) as caught:
                ReadOnlyRPC("https://example.org").call("eth_chainId", [])
        self.assertNotIn("SECRET", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
