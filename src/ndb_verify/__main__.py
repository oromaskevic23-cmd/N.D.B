"""Observe the NDB token using only read-only Polygon JSON-RPC calls."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


ADDRESS = "0x5F5E3dCa37D12F1bFef21418B066c6ccacbebBE4"
CHAIN_ID = 137
SOURCE_URL = "https://repo.sourcify.dev/137/" + ADDRESS
MAX_RESPONSE_BYTES = 1_000_000
MAX_STRING_BYTES = 4096
READ_ONLY_METHODS = frozenset({
    "eth_chainId", "eth_blockNumber", "eth_getBlockByNumber", "eth_getCode", "eth_call"
})
SELECTORS = {
    "name": "0x06fdde03",
    "symbol": "0x95d89b41",
    "decimals": "0x313ce567",
    "total_supply": "0x18160ddd",
}


class VerificationError(Exception):
    """A required observation failed; no partial success is reported."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise VerificationError("RPC redirects are not supported; use the final HTTPS endpoint")


def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value):
        raise VerificationError("Invalid JSON-RPC quantity")
    return int(value[2:], 16)


def hex_bytes(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*", value):
        raise VerificationError("Invalid hexadecimal data")
    return bytes.fromhex(value[2:])


def decode_uint(value):
    data = hex_bytes(value)
    if len(data) != 32:
        raise VerificationError("Invalid ABI integer")
    return int.from_bytes(data, "big")


def decode_string(value):
    data = hex_bytes(value)
    if len(data) < 64:
        raise VerificationError("Invalid ABI string")
    offset = int.from_bytes(data[:32], "big")
    if offset % 32 or offset < 32 or offset + 32 > len(data):
        raise VerificationError("Invalid ABI string offset")
    size = int.from_bytes(data[offset:offset + 32], "big")
    start = offset + 32
    if size > MAX_STRING_BYTES or start + size > len(data):
        raise VerificationError("Invalid ABI string length")
    try:
        return data[start:start + size].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError("Invalid ABI string encoding") from exc


def format_units(value, decimals):
    if not 0 <= decimals <= 255:
        raise VerificationError("Invalid token decimals")
    if decimals == 0:
        return str(value)
    whole, fraction = divmod(value, 10 ** decimals)
    tail = str(fraction).zfill(decimals).rstrip("0")
    return f"{whole}.{tail}" if tail else str(whole)


class ReadOnlyRPC:
    def __init__(self, url):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise VerificationError("RPC endpoint must be an HTTPS URL without embedded user credentials")
        self._url = url
        self._next_id = 0

    def call(self, method, params):
        if method not in READ_ONLY_METHODS:
            raise VerificationError("RPC method is not in the read-only allowlist")
        self._next_id += 1
        request_id = self._next_id
        body = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}).encode()
        request = urllib.request.Request(self._url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
                payload = response.read(MAX_RESPONSE_BYTES + 1)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise VerificationError("RPC request failed; check endpoint and connectivity") from exc
        if len(payload) > MAX_RESPONSE_BYTES:
            raise VerificationError("RPC response exceeds size limit")
        try:
            result = json.loads(payload)
        except (ValueError, UnicodeDecodeError) as exc:
            raise VerificationError("RPC response is not valid JSON") from exc
        if (not isinstance(result, dict) or result.get("jsonrpc") != "2.0"
                or result.get("id") != request_id or "result" not in result or "error" in result):
            raise VerificationError("RPC returned an invalid response or error")
        return result["result"]


def _block_hash(rpc, tag, expected_number):
    block = rpc.call("eth_getBlockByNumber", [tag, False])
    if not isinstance(block, dict) or quantity(block.get("number")) != expected_number:
        raise VerificationError("RPC returned the wrong block")
    block_hash = block.get("hash")
    if not isinstance(block_hash, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", block_hash):
        raise VerificationError("RPC returned an invalid block hash")
    return block_hash.lower()


def observe(rpc):
    """Read contract metadata at one numbered block from an RPC-compatible object."""
    if quantity(rpc.call("eth_chainId", [])) != CHAIN_ID:
        raise VerificationError("Endpoint is not Polygon Mainnet (chain ID 137)")
    number = quantity(rpc.call("eth_blockNumber", []))
    tag = hex(number)
    before = _block_hash(rpc, tag, number)
    bytecode = hex_bytes(rpc.call("eth_getCode", [ADDRESS, tag]))
    if not bytecode:
        raise VerificationError("No contract bytecode at the configured address")
    values = {}
    for field, selector in SELECTORS.items():
        raw = rpc.call("eth_call", [{"to": ADDRESS, "data": selector}, tag])
        values[field] = decode_string(raw) if field in ("name", "symbol") else decode_uint(raw)
    if values["decimals"] > 255:
        raise VerificationError("Token decimals exceed uint8 range")
    after = _block_hash(rpc, tag, number)
    if before != after:
        raise VerificationError("Block hash changed during observation; retry")
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "chain_id": CHAIN_ID,
        "contract": ADDRESS,
        "block_number": number,
        "block_hash": before,
        "bytecode_size_bytes": len(bytecode),
        "name": values["name"],
        "symbol": values["symbol"],
        "decimals": values["decimals"],
        "total_supply_raw": str(values["total_supply"]),
        "total_supply_tokens": format_units(values["total_supply"], values["decimals"]),
        "source_reference": SOURCE_URL,
        "limitations": "RPC data is provider-reported; source matching, finality and security are not checked by this tool."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only, block-anchored NDB contract observation on Polygon.")
    parser.add_argument("--rpc-url", default=os.environ.get("NDB_RPC_URL"),
                        help="HTTPS Polygon JSON-RPC endpoint; NDB_RPC_URL can be used instead")
    args = parser.parse_args(argv)
    if not args.rpc_url:
        parser.error("set NDB_RPC_URL or provide --rpc-url")
    try:
        report = observe(ReadOnlyRPC(args.rpc_url))
    except VerificationError as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

