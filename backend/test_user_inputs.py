#!/usr/bin/env python3
"""
Ad-hoc test cases for Body Language Translator endpoints.
Run from backend directory:  python test_user_inputs.py
"""
import sys
import json
import time
from typing import List, Dict, Any

import requests

BASE = "http://localhost:8000"

def pretty(label: str, data: Any):
    print(f"\n=== {label} ===")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2)[:2000])  # limit output size
    else:
        print(data)

def test_text_to_body(inputs: List[str]):
    results = []
    for text in inputs:
        try:
            r = requests.post(f"{BASE}/translate/text-to-body", json={"text": text})
            res = r.json()
            results.append({
                "input": text,
                "status": r.status_code,
                "num_instructions": len(res.get("body_language_instructions", [])),
                "first_instruction": res.get("body_language_instructions", [{}])[0] if res.get("body_language_instructions") else None,
            })
        except Exception as e:
            results.append({"input": text, "error": str(e)})
    pretty("Text → Body (summary)", results)


def test_wlasl():
    try:
        vocab = requests.get(f"{BASE}/asl/wlasl-vocabulary").json()
        pretty("WLASL vocabulary count", {"count": len(vocab.get("vocabulary", []))})
    except Exception as e:
        pretty("WLASL vocabulary error", str(e))

    try:
        anim = requests.post(f"{BASE}/asl/text-to-wlasl-animation", json={"text": "hello"}).json()
        pretty("WLASL animation (hello)", {
            "success": anim.get("success"),
            "gloss": anim.get("gloss"),
            "has_animation": bool(anim.get("animation_data") or anim.get("animation"))
        })
    except Exception as e:
        pretty("WLASL animation error", str(e))


def test_how2sign():
    try:
        info = requests.get(f"{BASE}/how2sign/info").json()
        pretty("How2Sign info", info)
    except Exception as e:
        pretty("How2Sign info error", str(e))

    try:
        anim = requests.post(f"{BASE}/how2sign/animation", json={"sign_gloss": "HELLO"}).json()
        pretty("How2Sign animation (HELLO)", {
            "success": anim.get("success"),
            "num_frames": len(anim.get("animation", [])) if isinstance(anim.get("animation"), list) else None
        })
    except Exception as e:
        pretty("How2Sign animation error", str(e))


def test_sigml():
    try:
        res = requests.post(f"{BASE}/sign/sigml/generate", json={"text": "hello", "duration": 3.0}).json()
        pretty("SiGML generate (hello)", {
            "success": res.get("success"),
            "hamnosys": res.get("animation", {}).get("hamnosys"),
            "sigml_len": len(res.get("animation", {}).get("sigml", ""))
        })
    except Exception as e:
        pretty("SiGML generate error", str(e))


def main():
    # Quick health ping
    try:
        r = requests.get(f"{BASE}/")
        print(f"Server: {r.status_code}")
    except Exception as e:
        print("Server not reachable:", e)
        sys.exit(1)

    # Planner tests (text → body)
    inputs = [
        "hello",
        "let's swim in the yard",
        "you are so tall?",
        "no",
        "I need help"
    ]
    test_text_to_body(inputs)

    # WLASL
    test_wlasl()

    # How2Sign
    test_how2sign()

    # SiGML / JASigning path
    test_sigml()

if __name__ == "__main__":
    main()
