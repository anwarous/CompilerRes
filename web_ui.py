from flask import Flask, request, jsonify, send_file
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

# Directory where algorithm files are stored on the server.
FILES_DIR = os.path.join(os.path.dirname(__file__), "algo_files")
os.makedirs(FILES_DIR, exist_ok=True)


def _safe_path(filename: str):
    """Return the absolute path for *filename* inside FILES_DIR, or None if
    the resolved path would escape the directory (path-traversal guard)."""
    # Strip any leading slashes / path components supplied by the caller.
    basename = os.path.basename(filename)
    if not basename or basename.startswith("."):
        return None
    full = os.path.realpath(os.path.join(FILES_DIR, basename))
    real_dir = os.path.realpath(FILES_DIR)
    if os.path.commonpath([full, real_dir]) != real_dir:
        return None
    return full


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


# ---------------------------------------------------------------------------
# File-management endpoints
# ---------------------------------------------------------------------------

@app.route("/files", methods=["GET"])
def list_files():
    """Return a list of all saved algorithm files.

    **Response** (JSON):
    ```json
    { "files": ["hello.algo", "sort.algo"] }
    ```
    """
    names = [
        f for f in os.listdir(FILES_DIR)
        if not f.startswith(".") and os.path.isfile(os.path.join(FILES_DIR, f))
    ]
    return jsonify({"files": sorted(names)}), 200


@app.route("/files", methods=["POST"])
def create_file():
    """Save a new algorithm file.

    **Request** (JSON):
    ```json
    { "name": "hello.algo", "content": "Algorithme hello\\ndebut\\n  Ecrire(\\"Bonjour\\")\\nfin" }
    ```

    **Response** (JSON) – success `201`:
    ```json
    { "name": "hello.algo", "size": 42 }
    ```
    """
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip()
    content = payload.get("content", "")

    if not name:
        return jsonify({"error": "Field 'name' is required"}), 400

    path = _safe_path(name)
    if path is None:
        return jsonify({"error": "Invalid file name"}), 400

    if os.path.exists(path):
        return jsonify({"error": f"File '{name}' already exists. Use PUT to update it."}), 409

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)

    return jsonify({"name": os.path.basename(path), "size": os.path.getsize(path)}), 201


@app.route("/files/<path:filename>", methods=["GET"])
def get_file(filename):
    """Return the content of a saved file.

    **Response** (JSON) – success `200`:
    ```json
    { "name": "hello.algo", "content": "..." }
    ```
    """
    path = _safe_path(filename)
    if path is None or not os.path.isfile(path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()

    return jsonify({"name": os.path.basename(path), "content": content}), 200


@app.route("/files/<path:filename>", methods=["PUT"])
def update_file(filename):
    """Overwrite (or clear) a saved file's content.

    Send an empty string for ``content`` to clear the file without deleting it.

    **Request** (JSON):
    ```json
    { "content": "Algorithme new_version\\n..." }
    ```

    **Response** (JSON) – success `200`:
    ```json
    { "name": "hello.algo", "size": 30 }
    ```
    """
    path = _safe_path(filename)
    if path is None or not os.path.isfile(path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    payload = request.get_json(silent=True) or {}
    content = payload.get("content", "")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)

    return jsonify({"name": os.path.basename(path), "size": os.path.getsize(path)}), 200


@app.route("/files/<path:filename>", methods=["DELETE"])
def delete_file(filename):
    """Permanently delete a saved file.

    **Response** (JSON) – success `200`:
    ```json
    { "deleted": "hello.algo" }
    ```
    """
    path = _safe_path(filename)
    if path is None or not os.path.isfile(path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    os.remove(path)
    return jsonify({"deleted": os.path.basename(path)}), 200


@app.route("/files/<path:filename>/run", methods=["POST"])
def run_file(filename):
    """Execute the algorithm stored in *filename*.

    **Request** (JSON, optional):
    ```json
    { "inputs": "5,10" }
    ```

    **Response** (JSON) – success `200`:
    ```json
    { "output": "120" }
    ```

    **Response** (JSON) – error `400`:
    ```json
    { "error": "..." }
    ```
    """
    path = _safe_path(filename)
    if path is None or not os.path.isfile(path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()

    payload = request.get_json(silent=True) or {}
    inputs_str = payload.get("inputs", "")
    result = _run_source(source, inputs_str)
    status = 400 if "error" in result else 200
    return jsonify(result), status


@app.route("/files/<path:filename>/download", methods=["GET"])
def download_file(filename):
    """Download the raw algorithm file.

    The response is the file's raw text content with
    ``Content-Disposition: attachment`` so that browsers trigger a download.
    """
    path = _safe_path(filename)
    if path is None or not os.path.isfile(path):
        return jsonify({"error": f"File '{filename}' not found"}), 404

    return send_file(
        path,
        as_attachment=True,
        download_name=os.path.basename(path),
        mimetype="text/plain; charset=utf-8",
    )


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
