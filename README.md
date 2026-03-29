# AlgoInterpreter — REST API

A Python interpreter for French-style pseudocode algorithms, exposed as a REST API so it can be embedded in any website.

## Files

| File | Purpose |
|------|---------|
| `lexer.py` | Tokenises algorithm source code |
| `parser.py` | Builds an AST from tokens |
| `interpreter.py` | Walks the AST and executes the program |
| `web_ui.py` | Flask REST API server (use this in production) |
| `main.py` | CLI runner (for local testing) |

---

## Running the API server

```bash
pip install -r requirements.txt
python web_ui.py
# Server starts on http://0.0.0.0:5000
```

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Port to listen on |
| `FLASK_DEBUG` | `false` | Set to `true` for debug mode |
| `ALLOWED_ORIGIN` | `*` | CORS allowed origin — **set this to your website's URL in production**, e.g. `https://yoursite.com`. Leaving it as `*` allows any domain to call the API. |

---

## API Reference

### `POST /run`

Execute an algorithm and return its output.

**Request body** (JSON):

```json
{
  "code": "Algorithme hello\ndebut\n  Ecrire(\"Bonjour\")\nfin",
  "inputs": "5,10"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Full algorithm source code |
| `inputs` | string | Comma-separated input values (fed to `Lire()` calls) |

**Success response** `200`:

```json
{ "output": "Bonjour" }
```

**Error response** `400`:

```json
{ "error": "description of parse/runtime error" }
```

### `GET /health`

Returns `{"status": "ok"}` — useful for uptime checks.

---

## File-management API

Algorithm files can be saved on the server, executed, downloaded, or deleted without sending the full source code every time.

### `GET /files`

List all saved files.

```json
{ "files": ["hello.algo", "sort.algo"] }
```

### `POST /files`

Save a new file.

**Request body** (JSON):

```json
{ "name": "hello.algo", "content": "Algorithme hello\n..." }
```

**Success** `201`: `{ "name": "hello.algo", "size": 42 }`  
**Error** `409` if the file already exists (use `PUT` to update it).

### `GET /files/<name>`

Retrieve the content of a saved file.

**Success** `200`: `{ "name": "hello.algo", "content": "..." }`

### `PUT /files/<name>`

Overwrite (or clear) a file's content. Send `"content": ""` to empty the file without deleting it.

**Request body** (JSON): `{ "content": "..." }`  
**Success** `200`: `{ "name": "hello.algo", "size": 30 }`

### `DELETE /files/<name>`

Permanently delete a saved file.

**Success** `200`: `{ "deleted": "hello.algo" }`

### `POST /files/<name>/run`

Execute the algorithm stored in the named file.

**Request body** (JSON, optional): `{ "inputs": "5,10" }`  
**Success** `200`: `{ "output": "120" }`  
**Error** `400`: `{ "error": "..." }`

### `GET /files/<name>/download`

Download the raw `.algo` file. The browser will be prompted to save it.

---

## Calling from your website (JavaScript)

**Run code inline:**

```js
const response = await fetch('https://your-api-host/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: `Algorithme factorielle
debut
  Lire(n)
  f <-- 1
  pour i de 1 a n faire
    f <-- f * i
  fin pour
  Ecrire(f)
fin`,
    inputs: '5'
  })
});

const data = await response.json();
if (data.error) {
  console.error('Error:', data.error);
} else {
  console.log('Output:', data.output); // "120"
}
```

**Save a file, run it, then download it:**

```js
const BASE = 'https://your-api-host';

// 1 – Save the file
await fetch(`${BASE}/files`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'fact.algo', content: sourceCode })
});

// 2 – Run it
const runRes = await fetch(`${BASE}/files/fact.algo/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ inputs: '5' })
});
const { output, error } = await runRes.json();

// 3 – Download it (triggers browser save dialog)
window.location.href = `${BASE}/files/fact.algo/download`;

// 4 – Delete it when done
await fetch(`${BASE}/files/fact.algo`, { method: 'DELETE' });
```

---

## CLI usage (local testing)

```bash
python main.py path/to/algo.algo --inputs "5,10,3"
```
