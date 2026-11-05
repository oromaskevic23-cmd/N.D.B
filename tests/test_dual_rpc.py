"""Offline dual-provider evidence regression tests. No live RPC or wallet access.

Project author and founding architect: Alexander Nikolaevich Romaskevich (RomaskevicH).
"""
import json
import unittest
from contextlib import redirect_stdout, redirect_stderr
from hashlib import sha256
from io import StringIO
from unittest.mock import patch

from ndb_verify.__main__ import (
    ADDRESS, CHAIN_ID, VerificationError, main, observe,
    observe_two,
)


def uint(n):
    return "0x" + n.to_bytes(32, "big").hex()


def text_abi(value):
    raw = value.encode("utf-8")
    return ("0x" + (32).to_bytes(32, "big").hex()
            + len(raw).to_bytes(32, "big").hex()
            + raw.hex() + ("00" * (-len(raw) % 32)))


class FakeReadOnlyRPC:
    def __init__(self):
        self.calls = []
        self.chain = "0x89"
        self.height = "0x123"
        self.block_hash = "0x" + "ab" * 32
        self.code = "0x6000"
        self.values = {
            "0x06fdde03": text_abi("New Digital Bitcoin"),
            "0x95d89b41": text_abi("NDB"),
            "0x313ce567": uint(18),
            "0x18160ddd": uint(1_000_000_000 * 10**18),
        }

    def call(self, method, params):
        self.calls.append((method, params))
        if method == "eth_chainId":
            return self.chain
        if method == "eth_blockNumber":
            return self.height
        if method == "eth_getBlockByNumber":
            return {"number": params[0], "hash": self.block_hash}
        if method == "eth_getCode":
            return self.code
        if method == "eth_call":
            return self.values[params[0]["data"]]
        raise AssertionError("A non-allowlisted RPC method was requested")


class NDBDualRPCSecurityTests(unittest.TestCase):
    def test_two_matching_providers_agree_at_shared_block(self):
        a, b = FakeReadOnlyRPC(), FakeReadOnlyRPC()
        report = observe_two(a, b)
        self.assertEqual(report["contract"], ADDRESS)
        self.assertEqual(report["chain_id"], CHAIN_ID)
        self.assertEqual(report["block_number"], 291)
        self.assertEqual(report["bytecode_sha256"], sha256(bytes.fromhex("6000")).hexdigest())
        self.assertEqual(
            report["cross_check"]["status"],
            "TWO_RPC_REPORTS_AGREE_NOT_FINALITY_PROOF",
        )
        self.assertFalse(report["cross_check"]["independent_providers_verified"])
        for rpc in (a, b):
            self.assertNotIn("eth_sendRawTransaction", [name for name, _ in rpc.calls])
            self.assertTrue(all(p[-1] == "0x123" for m, p in rpc.calls
                                if m in ("eth_call", "eth_getCode")))

    def test_conflicting_provider_contract_values_fail_closed(self):
        for change in ["hash", "code", "supply", "symbol"]:
            a, b = FakeReadOnlyRPC(), FakeReadOnlyRPC()
            if change == "hash":
                b.block_hash = "0x" + "cd" * 32
            elif change == "code":
                b.code = "0x6001"
            elif change == "supply":
                b.values["0x18160ddd"] = uint(123)
            else:
                b.values["0x95d89b41"] = text_abi("NOT-NDB")
            with self.subTest(change=change), self.assertRaisesRegex(
                VerificationError, "endpoints disagree"
            ):
                observe_two(a, b)

    def test_wrong_chain_on_peer_is_rejected_before_token_queries(self):
        a, b = FakeReadOnlyRPC(), FakeReadOnlyRPC()
        b.chain = "0x1"
        with self.assertRaisesRegex(VerificationError, "not Polygon"):
            observe_two(a, b)
        self.assertNotIn("eth_call", [method for method, _ in b.calls])

    def test_explicit_height_above_provider_tip_is_rejected(self):
        for invalid in [True, -1, "291", 292]:
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                VerificationError, "block height"
            ):
                observe(FakeReadOnlyRPC(), block_number=invalid)

    def test_one_block_is_pinned_even_if_providers_have_different_heads(self):
        a, b = FakeReadOnlyRPC(), FakeReadOnlyRPC()
        a.height = "0x124"
        report = observe_two(a, b)
        self.assertEqual(report["block_number"], 291)
        self.assertEqual(report["cross_check"]["shared_block_number"], 291)

    def test_cli_emits_cross_check_only_when_providers_agree(self):
        a, b = FakeReadOnlyRPC(), FakeReadOnlyRPC()
        output = StringIO()
        with patch("ndb_verify.__main__.ReadOnlyRPC", side_effect=[a, b]):
            with redirect_stdout(output):
                result = main(["--rpc-url", "https://rpc-one.example",
                               "--second-rpc-url", "https://rpc-two.example"])
        self.assertEqual(result, 0)
        self.assertEqual(
            json.loads(output.getvalue())["cross_check"]["status"],
            "TWO_RPC_REPORTS_AGREE_NOT_FINALITY_PROOF",
        )

    def test_same_rpc_url_is_not_counted_as_two_providers(self):
        error = StringIO()
        with redirect_stderr(error):
            result = main(["--rpc-url", "https://rpc-one.example",
                           "--second-rpc-url", "https://rpc-one.example"])
        self.assertEqual(result, 1)
        self.assertIn("distinct RPC URLs", error.getvalue())


if __name__ == "__main__":
    unittest.main()
