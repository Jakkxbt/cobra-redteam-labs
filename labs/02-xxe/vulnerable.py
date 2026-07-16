#!/usr/bin/env python3
"""
vulnerable.py — XXE-vulnerable XML endpoint for testing
FOR AUTHORISED TESTING ONLY. Runs on localhost:8081.

This endpoint processes XML with external entities ENABLED —
demonstrates a classic XXE vulnerability.

DO NOT EXPOSE THIS TO PUBLIC NETWORKS.
"""
from flask import Flask, request, jsonify
from lxml import etree

app = Flask(__name__)


@app.route("/xxe", methods=["POST"])
def xxe_endpoint():
    """Vulnerable XXE endpoint — external entities NOT disabled."""
    try:
        xml_data = request.data  # Get raw bytes, not decoded string
        print(f"[*] Received XML: {xml_data[:200]}...")

        # VULNERABLE: parse XML with lxml (external entities enabled by default)
        parser = etree.XMLParser(resolve_entities=True)
        root = etree.fromstring(xml_data, parser=parser)
        text_content = root.text if root.text else ""

        # Echo back the parsed content
        return jsonify({
            "status": "success",
            "parsed_content": text_content,
            "message": "XML parsed (external entities enabled)"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"XML parsing error: {str(e)}"
        }), 400


if __name__ == "__main__":
    print("=" * 60)
    print("VULNERABLE XXE TESTLAB")
    print("=" * 60)
    print("This endpoint has XXE enabled for testing purposes only.")
    print("DO NOT expose to public networks.")
    print()
    print("Running on http://localhost:8081/xxe")
    print()
    print("Test with:")
    print("=" * 60)
    app.run(host="127.0.0.1", port=8081, debug=False)
