from flask import Flask, render_template_string, request, jsonify
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

app = Flask(__name__)

HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Interpréteur Algo</title>
    <style>
        body { font-family: monospace; max-width: 900px; margin: 40px auto; padding: 20px; }
        textarea { width: 100%; height: 300px; font-family: monospace; font-size: 14px; }
        input[type=text] { width: 100%; padding: 5px; }
        button { padding: 10px 20px; margin-top: 10px; cursor: pointer; }
        #output { background: #1e1e1e; color: #d4d4d4; padding: 15px; min-height: 100px; white-space: pre; margin-top: 10px; }
        .error { color: #f44; }
    </style>
</head>
<body>
    <h1>&#x1F5A5;&#xFE0F; Interpréteur Algorithmique</h1>
    <textarea id="code" placeholder="Écrivez votre algorithme ici..."></textarea>
    <br>
    <label>Entrées (séparées par virgules): <input type="text" id="inputs" placeholder="ex: 5,10,3"></label>
    <br>
    <button onclick="run()">&#x25B6; Exécuter</button>
    <div id="output">Prêt.</div>
    <script>
    async function run() {
        const code = document.getElementById('code').value;
        const inputs = document.getElementById('inputs').value;
        const out = document.getElementById('output');
        out.textContent = 'Exécution...';
        try {
            const resp = await fetch('/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code, inputs})
            });
            const data = await resp.json();
            if (data.error) {
                out.innerHTML = '<span class="error">Erreur: ' + data.error + '</span>';
            } else {
                out.textContent = data.output || '(pas de sortie)';
            }
        } catch(e) {
            out.innerHTML = '<span class="error">' + e + '</span>';
        }
    }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    source = data.get('code', '')
    inputs_str = data.get('inputs', '')

    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        input_queue = [x.strip() for x in inputs_str.split(',')] if inputs_str else []

        from unittest.mock import patch
        output_lines = []

        def mock_print(*args, **kwargs):
            sep = kwargs.get('sep', ' ')
            output_lines.append(sep.join(str(a) for a in args))

        interp = Interpreter(program, input_queue)
        with patch('builtins.print', mock_print):
            interp.run()

        return jsonify({'output': '\n'.join(output_lines)})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)
