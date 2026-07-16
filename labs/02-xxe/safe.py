#!/usr/bin/env python3
"""
safe.py — XXE-safe XML endpoint for testing
FOR AUTHORISED TESTING ONLY. Runs on localhost:8082.

This endpoint processes XML with external entities DISABLED —
demonstrates proper XXE protection.

A hardened parser that rejects external entities.
"""
from flask import Flask, request, jsonify
from xml.etree.ElementTree import fromstring
from defusedxml.ElementTree import fromstring as safe_fromstring

app = Flask(__name__)


@app.route("/xxe", methods=["POST"])
def xxe_endpoint():
    """Safe XXE endpoint — external entities DISABLED."""
    try:
        xml_data = request.data.decode("utf-8")
        print(f"[*] Received XML: {xml_data[:200]}...")

        # SAFE: parse XML with defusedxml (external entities disabled)
        root = safe_fromstring(xml_data)
        text_content = root.text if root.text else ""

        # Echo back the parsed content
        return jsonify({
            "status": "success",
            "parsed_content": text_content,
            "message": "XML parsed (external entities disabled)"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"XML parsing error: {str(e)}"
        }), 400


if __name__ == "__main__":
    print("=" * 60)
    print("SAFE XXE TESTLAB")
    print("=" * 60)
    print("This endpoint has XXE disabled for secure testing.")
    print()
    print("Running on http://localhost:8082/xxe")
    print()
    print("Test with:")
    print("=" * 60)
    app.run(host="127.0.0.1", port=8082, debug=False)
