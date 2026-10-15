#!/usr/bin/env python3
"""Verify Apple's signature and compare each distributed workflow to its source."""
import hashlib
import json
import plistlib
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest_path = ROOT / "dist/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest:
        source = ROOT / entry["source"]
        signed = ROOT / entry["file"]
        blob = signed.read_bytes()
        if blob[:4] != b"AEA1":
            raise ValueError(f"Not an Apple-signed archive: {signed.name}")
        auth_length = struct.unpack("<I", blob[8:12])[0]
        auth = plistlib.loads(blob[12:12 + auth_length])
        with tempfile.TemporaryDirectory(prefix="english-helper-verify-") as folder:
            temp = Path(folder)
            pub = subprocess.run(["openssl", "x509", "-inform", "DER", "-pubkey", "-noout"],
                                 input=auth["SigningCertificateChain"][0],
                                 capture_output=True, check=True).stdout
            (temp / "public.pem").write_bytes(pub)
            subprocess.run(["aea", "decrypt", "-i", str(signed), "-o", str(temp / "archive"),
                            "-sign-pub", str(temp / "public.pem")], capture_output=True, check=True)
            subprocess.run(["aa", "extract", "-i", str(temp / "archive"), "-d", str(temp / "content")],
                           capture_output=True, check=True)
            actual = plistlib.loads((temp / "content/Shortcut.wflow").read_bytes())
            expected = plistlib.loads(source.read_bytes())
            # Apple's signer drops the filename-derived name and stamps its own
            # client build. All executable actions and other metadata must match.
            for key in ("WFWorkflowName", "WFWorkflowClientVersion"):
                actual.pop(key, None)
                expected.pop(key, None)
            if actual != expected:
                raise ValueError(f"Signed content differs from source: {signed.name}")
        entry["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        entry["file_sha256"] = hashlib.sha256(blob).hexdigest()
        entry["status"] = "signature-and-content-verified-see-runtime-evidence"
        print(f"Verified signature, actions, and workflow settings: {signed.name}")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
