from flask import Flask, request, jsonify
from flask_cors import CORS
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

app = Flask(__name__)

# Allow requests from any origin so the API can be embedded in any website.
# ⚠️  Security: set the ALLOWED_ORIGIN environment variable to your website's
# exact origin in production (e.g. "https://yoursite.com") to prevent
# unauthorised cross-origin requests.
CORS(app, resources={r"/*": {"origins": os.environ.get("ALLOWED_ORIGIN", "*")}})


def _run_source(source: str, inputs_str: str) -> dict:
    """Parse and interpret *source*, feed *inputs_str* (comma-separated) as
    stdin, and return ``{"output": "..."}`` or ``{"error": "..."}``.
    """
    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        input_queue = [x.strip() for x in inputs_str.split(",")] if inputs_str.strip() else []

        output_lines = []

        def _capture_print(*args, **kwargs):
            sep = kwargs.get("sep", " ")
            output_lines.append(sep.join(str(a) for a in args))

        interp = Interpreter(program, input_queue)
        with patch("builtins.print", _capture_print):
            interp.run()

        return {"output": "\n".join(output_lines)}
    except Exception as exc:
        return {"error": str(exc)}


@app.route("/run", methods=["POST"])
def run_code():
    """Execute an algorithm.

    **Request** (JSON):
    ```json
    { "code": "<algorithm source>", "inputs": "val1,val2,..." }
    ```

    **Response** (JSON) – success:
    ```json
    { "output": "line1\\nline2\\n..." }
    ```

    **Response** (JSON) – error:
    ```json
    { "error": "description of the error" }
    ```
    """
    payload = request.get_json(silent=True) or {}
    source = payload.get("code", "")
    inputs_str = payload.get("inputs", "")
    result = _run_source(source, inputs_str)
    status = 400 if "error" in result else 200
    return jsonify(result), status


@app.route("/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
