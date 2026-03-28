import math
import random
import struct
import os

from parser import (Program, ProcDef, FuncDef, Assign, If, For, While, Repeat,
                    Return, ProcCall, FuncCall, ArrayAccess, FieldAccess,
                    RangeValue, SeIon, SeIonCase,
                    BinOp, UnaryOp, Literal, Var, EcrireStmt, LireStmt,
                    VarDecl, ArrayDecl, RecordDecl, RecordField, FileDecl, TypeDef)

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class InterpreterError(Exception):
    pass

class FileHandle:
    """Wraps a Python file object together with its open mode and type."""
    def __init__(self, path, mode, binary=False):
        self.path = path
        self.mode = mode
        self.binary = binary
        self._file = None

    def open(self):
        self._file = open(self.path, self.mode)

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def is_eof(self):
        if self._file is None:
            return True
        pos = self._file.tell()
        ch = self._file.read(1)
        if not ch:
            return True
        self._file.seek(pos)
        return False

class Environment:
    def __init__(self, parent=None, isolated=False):
        self.vars = {}
        self.parent = parent
        # isolated=True means this is a function/procedure scope: writes never
        # leak to the parent scope (only reads fall through for globals).
        self.isolated = isolated

    def get(self, name):
        name = name.lower()
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        return 0  # default

    def set(self, name, value):
        self.vars[name.lower()] = value

    def set_existing(self, name, value):
        name = name.lower()
        if name in self.vars:
            self.vars[name] = value
            return True
        if self.parent and not self.isolated:
            return self.parent.set_existing(name, value)
        # Isolated scope or top-level: create in current scope
        self.vars[name] = value
        return True

class Interpreter:
    # Guard against infinite loops: raise RuntimeError after this many iterations
    # in a single repeter/tant-que/pour loop.
    MAX_ITERATIONS = 1_000_000

    def __init__(self, program, input_queue=None):
        self.program = program
        self.input_queue = input_queue or []
        self.input_index = 0
        self.global_env = Environment()
        self.procedures = {}
        self.functions = {}
        self.output = []
        self.type_defs = {}       # user-defined type name → definition

        for proc in program.procedures:
            self.procedures[proc.name.lower()] = proc
        for func in program.functions:
            self.functions[func.name.lower()] = func

        # Process declarations: build type registry then initialise globals
        self._process_declarations(program.declarations, self.global_env)

    # ── Declarations ─────────────────────────────────────────────────────────

    def _process_declarations(self, declarations, env):
        for decl in declarations:
            if isinstance(decl, TypeDef):
                self.type_defs[decl.name.lower()] = decl.definition
            elif isinstance(decl, VarDecl):
                env.set(decl.name, self._default_value(decl.type_name))
            elif isinstance(decl, ArrayDecl):
                env.set(decl.name, {})
            elif isinstance(decl, RecordDecl):
                env.set(decl.name, self._make_record(decl))
            elif isinstance(decl, FileDecl):
                env.set(decl.name, None)  # file handle initialised by Ouvrir()

    def _default_value(self, type_name):
        t = type_name.lower()
        if t in ('entier',):
            return 0
        if t in ('réel', 'reel', 'r\u00e9el'):
            return 0.0
        if t in ('booléen', 'booleen', 'bool\u00e9en'):
            return False
        if t in ('caractère', 'caractere', 'caract\u00e8re'):
            return ''
        if t in ('chaîne', 'chaine', 'cha\u00eene', 'chaîne de caractères'):
            return ''
        return 0

    def _make_record(self, record_decl):
        """Create a dict representing a record with default field values."""
        rec = {}
        for f in record_decl.fields:
            rec[f.name.lower()] = self._default_value(f.type_name)
        return rec

    def _make_record_from_type(self, type_name):
        """Create a record from a named user-defined type."""
        td = self.type_defs.get(type_name.lower())
        if isinstance(td, RecordDecl):
            return self._make_record(td)
        return {}

    # ── Execution ─────────────────────────────────────────────────────────────

    def run(self):
        self.exec_block(self.program.body, self.global_env)

    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, stmt, env):
        if isinstance(stmt, Assign):
            val = self.eval_expr(stmt.value, env)
            # Deep-copy records on assignment to avoid shared references
            if isinstance(val, dict):
                val = val.copy()
            self.assign_target(stmt.target, val, env)

        elif isinstance(stmt, EcrireStmt):
            self._exec_ecrire(stmt, env)

        elif isinstance(stmt, LireStmt):
            self._exec_lire(stmt, env)

        elif isinstance(stmt, If):
            cond = self.eval_expr(stmt.condition, env)
            if cond:
                self.exec_block(stmt.then_block, env)
            else:
                done = False
                for elif_cond, elif_block in stmt.elif_list:
                    if self.eval_expr(elif_cond, env):
                        self.exec_block(elif_block, env)
                        done = True
                        break
                if not done and stmt.else_block is not None:
                    self.exec_block(stmt.else_block, env)

        elif isinstance(stmt, For):
            self._exec_for(stmt, env)

        elif isinstance(stmt, While):
            count = 0
            while self.eval_expr(stmt.condition, env):
                self.exec_block(stmt.body, env)
                count += 1
                if count > self.MAX_ITERATIONS:
                    raise InterpreterError("Infinite loop detected in while")

        elif isinstance(stmt, Repeat):
            count = 0
            while True:
                self.exec_block(stmt.body, env)
                count += 1
                if count > self.MAX_ITERATIONS:
                    raise InterpreterError("Infinite loop detected in repeat")
                if self.eval_expr(stmt.condition, env):
                    break

        elif isinstance(stmt, SeIon):
            self._exec_selon(stmt, env)

        elif isinstance(stmt, Return):
            val = self.eval_expr(stmt.value, env)
            raise ReturnException(val)

        elif isinstance(stmt, ProcCall):
            self.call_proc_or_builtin(stmt.name, stmt.args, env)

    def _exec_ecrire(self, stmt, env):
        """Handle Écrire / Écrire_nl — also handles file writes when first arg is a FileHandle."""
        args = stmt.args
        # File write: Écrire(nom_fichier, valeur)
        if args:
            first = self.eval_expr(args[0], env)
            if isinstance(first, FileHandle):
                fh = first
                for a in args[1:]:
                    v = self.eval_expr(a, env)
                    s = self.to_str(v)
                    if fh._file:
                        fh._file.write(s)
                return
        # Console output
        parts = [self.to_str(self.eval_expr(a, env)) for a in args]
        line = ''.join(parts)
        print(line)
        self.output.append(line)

    def _exec_lire(self, stmt, env):
        """Handle Lire — also handles file reads when first arg is a FileHandle."""
        args = stmt.args
        # File read: Lire(nom_fichier, variable)
        if args and isinstance(args[0], Var):
            maybe_fh = env.get(args[0].name)
            if isinstance(maybe_fh, FileHandle):
                fh = maybe_fh
                for target in args[1:]:
                    if fh._file:
                        line = fh._file.readline()
                        val = self.parse_input(line)
                    else:
                        val = 0
                    self.assign_target(target, val, env)
                return
        # Console read
        for arg in args:
            if self.input_index < len(self.input_queue):
                val_str = self.input_queue[self.input_index]
                self.input_index += 1
            else:
                val_str = input()
            val = self.parse_input(val_str)
            self.assign_target(arg, val, env)

    def _exec_for(self, stmt, env):
        start = self.eval_expr(stmt.start, env)
        end = self.eval_expr(stmt.end, env)
        step = self.eval_expr(stmt.step, env) if stmt.step is not None else 1
        if isinstance(start, float):
            start = int(start)
        if isinstance(end, float):
            end = int(end)
        if isinstance(step, float):
            step = int(step)
        if step == 0:
            raise InterpreterError("Pour loop step cannot be zero")
        count = 0
        if step > 0:
            i = start
            while i <= end:
                env.set(stmt.var, i)
                self.exec_block(stmt.body, env)
                i += step
                count += 1
                if count > self.MAX_ITERATIONS:
                    raise InterpreterError("Infinite loop detected in pour")
        else:
            i = start
            while i >= end:
                env.set(stmt.var, i)
                self.exec_block(stmt.body, env)
                i += step
                count += 1
                if count > self.MAX_ITERATIONS:
                    raise InterpreterError("Infinite loop detected in pour")

    def _exec_selon(self, stmt, env):
        selector = self.eval_expr(stmt.expr, env)
        for case in stmt.cases:
            for cv in case.values:
                if isinstance(cv, RangeValue):
                    lo = self.eval_expr(cv.start, env)
                    hi = self.eval_expr(cv.end, env)
                    if lo <= selector <= hi:
                        self.exec_block(case.body, env)
                        return
                else:
                    v = self.eval_expr(cv, env)
                    if selector == v:
                        self.exec_block(case.body, env)
                        return
        if stmt.otherwise is not None:
            self.exec_block(stmt.otherwise, env)

    # ── Procedure / Function calls ───────────────────────────────────────────

    def call_proc_or_builtin(self, name, args, env):
        name_lower = name.lower()

        if name_lower in ('ecrire', '\u00e9crire'):
            parts = [self.to_str(self.eval_expr(a, env)) for a in args]
            line = ''.join(parts)
            print(line)
            self.output.append(line)
            return

        if name_lower in ('ecrire_nl', '\u00e9crire_nl'):
            parts = [self.to_str(self.eval_expr(a, env)) for a in args]
            line = ''.join(parts)
            print(line)
            self.output.append(line)
            return

        if name_lower == 'lire':
            for arg in args:
                if self.input_index < len(self.input_queue):
                    val_str = self.input_queue[self.input_index]
                    self.input_index += 1
                else:
                    val_str = input()
                val = self.parse_input(val_str)
                self.assign_target(arg, val, env)
            return

        # File operations
        if name_lower == 'ouvrir':
            self._builtin_ouvrir(args, env)
            return
        if name_lower == 'fermer':
            self._builtin_fermer(args, env)
            return
        if name_lower in ('lire_ligne',):
            self._builtin_lire_ligne(args, env)
            return
        if name_lower in ('ecrire_nl',):
            self._builtin_ecrire_nl_file(args, env)
            return

        if name_lower in self.procedures:
            self.call_proc(self.procedures[name_lower], args, env)
            return
        raise InterpreterError(f"Unknown procedure: {name}")

    def call_proc(self, proc_def, call_args_nodes, caller_env):
        local_env = Environment(parent=self.global_env, isolated=True)
        ref_params = []

        for (by_ref, param_name, param_type), arg_node in zip(proc_def.params, call_args_nodes):
            val = self.eval_expr(arg_node, caller_env)
            local_env.set(param_name, val)
            if by_ref:
                ref_params.append((param_name, arg_node, caller_env))

        try:
            self.exec_block(proc_def.body, local_env)
        except ReturnException:
            pass

        # Write back reference parameters
        for (local_name, arg_node, c_env) in ref_params:
            new_val = local_env.vars.get(local_name.lower(), local_env.get(local_name))
            self.assign_target(arg_node, new_val, c_env)

    def call_func(self, func_def, call_args_nodes, caller_env):
        local_env = Environment(parent=self.global_env, isolated=True)

        for (by_ref, param_name, param_type), arg_node in zip(func_def.params, call_args_nodes):
            val = self.eval_expr(arg_node, caller_env)
            local_env.set(param_name, val)

        try:
            self.exec_block(func_def.body, local_env)
        except ReturnException as e:
            return e.value

        return 0

    # ── Expression evaluation ─────────────────────────────────────────────────

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Var):
            return env.get(expr.name)

        if isinstance(expr, FieldAccess):
            obj = self.eval_expr(expr.obj, env)
            if isinstance(obj, dict):
                return obj.get(expr.field.lower(), 0)
            raise InterpreterError(f"Cannot access field '{expr.field}' on non-record value")

        if isinstance(expr, ArrayAccess):
            return self._eval_array_access(expr, env)

        if isinstance(expr, FuncCall):
            return self.eval_func_call(expr, env)

        if isinstance(expr, BinOp):
            return self.eval_binop(expr, env)

        if isinstance(expr, UnaryOp):
            if expr.op == '-':
                return -self.eval_expr(expr.operand, env)
            if expr.op == 'non':
                return not self.eval_expr(expr.operand, env)

        return 0

    def _eval_array_access(self, expr, env):
        # expr.name can be a string OR a FieldAccess (for record array fields)
        if isinstance(expr.name, str):
            arr = env.get(expr.name)
        else:
            arr = self.eval_expr(expr.name, env)

        if isinstance(arr, str):
            # String indexing: Ch[i]  (0-based per convention)
            idx = self.eval_expr(expr.indices[0], env)
            if isinstance(idx, float):
                idx = int(idx)
            return arr[idx] if 0 <= idx < len(arr) else ''

        if not isinstance(arr, dict):
            arr = {}

        if len(expr.indices) == 1:
            idx = self.eval_expr(expr.indices[0], env)
            if isinstance(idx, float):
                idx = int(idx)
            return arr.get(idx, 0)
        else:
            indices = []
            for i in expr.indices:
                iv = self.eval_expr(i, env)
                if isinstance(iv, float):
                    iv = int(iv)
                indices.append(iv)
            return arr.get(tuple(indices), 0)

    def eval_func_call(self, expr, env):
        name = expr.name.lower()
        args = expr.args

        # ── Built-in functions ──────────────────────────────────────────────

        # String functions
        if name == 'convch':
            v = self.eval_expr(args[0], env)
            return self.to_str(v)
        if name == 'long':
            v = self.eval_expr(args[0], env)
            if isinstance(v, str):
                return len(v)
            return len(str(v))
        if name == 'majus':
            v = self.eval_expr(args[0], env)
            return str(v).upper()
        if name == 'pos':
            ch1 = self.to_str(self.eval_expr(args[0], env))
            ch2 = self.to_str(self.eval_expr(args[1], env))
            idx = ch2.find(ch1)
            return idx  # returns -1 if not found
        if name == 'estnum':
            v = self.to_str(self.eval_expr(args[0], env))
            try:
                float(v)
                return True
            except ValueError:
                return False
        if name == 'valeur':
            v = self.to_str(self.eval_expr(args[0], env))
            try:
                return int(v)
            except ValueError:
                try:
                    return float(v)
                except ValueError:
                    raise InterpreterError(f"Valeur: '{v}' is not numeric")
        if name in ('sous_chaine', 'souschaine'):
            ch = self.to_str(self.eval_expr(args[0], env))
            d = int(self.eval_expr(args[1], env))
            f = int(self.eval_expr(args[2], env))
            return ch[d:f]
        if name == 'effacer':
            ch = self.to_str(self.eval_expr(args[0], env))
            d = int(self.eval_expr(args[1], env))
            f = int(self.eval_expr(args[2], env))
            return ch[:d] + ch[f:]

        # Numeric functions
        if name == 'arrondi':
            v = self.eval_expr(args[0], env)
            return round(float(v))
        if name in ('racinecarre', 'racinecarr\u00e9', 'racine_carre', 'racine_carr\u00e9e'):
            v = self.eval_expr(args[0], env)
            return math.sqrt(float(v))
        if name in ('al\u00e9a', 'alea'):
            vi = int(self.eval_expr(args[0], env))
            vf = int(self.eval_expr(args[1], env))
            return random.randint(vi, vf)
        if name == 'ent':
            v = self.eval_expr(args[0], env)
            return int(float(v))
        if name == 'abs':
            v = self.eval_expr(args[0], env)
            return abs(v)

        # Character functions
        if name == 'ord':
            v = self.eval_expr(args[0], env)
            s = self.to_str(v)
            return ord(s[0]) if s else 0
        if name == 'chr':
            v = int(self.eval_expr(args[0], env))
            return chr(v)

        # File functions
        if name in ('fin_fichier', 'fin_fich'):
            fh = self.eval_expr(args[0], env)
            if isinstance(fh, FileHandle):
                return fh.is_eof()
            return True

        if name in ('ecrire', '\u00e9crire'):
            parts = [self.to_str(self.eval_expr(a, env)) for a in args]
            line = ''.join(parts)
            print(line)
            self.output.append(line)
            return None

        if name in ('ecrire_nl', '\u00e9crire_nl'):
            parts = [self.to_str(self.eval_expr(a, env)) for a in args]
            line = ''.join(parts)
            print(line)
            self.output.append(line)
            return None

        # User-defined function
        if name in self.functions:
            return self.call_func(self.functions[name], args, env)

        # Try as procedure
        if name in self.procedures:
            self.call_proc(self.procedures[name], args, env)
            return None

        raise InterpreterError(f"Unknown function: {expr.name}")

    # ── File operation helpers ────────────────────────────────────────────────

    def _builtin_ouvrir(self, args, env):
        path = self.to_str(self.eval_expr(args[0], env))
        file_var_node = args[1]
        mode = self.to_str(self.eval_expr(args[2], env))
        binary = 'b' in mode
        fh = FileHandle(path, mode, binary)
        try:
            fh.open()
        except OSError as e:
            raise InterpreterError(f"Ouvrir: {e}")
        self.assign_target(file_var_node, fh, env)

    def _builtin_fermer(self, args, env):
        fh = self.eval_expr(args[0], env)
        if isinstance(fh, FileHandle):
            fh.close()

    def _builtin_lire_ligne(self, args, env):
        fh = self.eval_expr(args[0], env)
        target = args[1]
        if isinstance(fh, FileHandle) and fh._file:
            line = fh._file.readline()
            if line.endswith('\n'):
                line = line[:-1]
            self.assign_target(target, line, env)

    def _builtin_ecrire_nl_file(self, args, env):
        fh = self.eval_expr(args[0], env)
        val = self.to_str(self.eval_expr(args[1], env))
        if isinstance(fh, FileHandle) and fh._file:
            fh._file.write(val + '\n')

    # ── Binary operations ─────────────────────────────────────────────────────

    def eval_binop(self, expr, env):
        # Short-circuit logical ops
        if expr.op == 'et':
            left = self.eval_expr(expr.left, env)
            if not left:
                return False
            return bool(self.eval_expr(expr.right, env))
        if expr.op == 'ou':
            left = self.eval_expr(expr.left, env)
            if left:
                return True
            return bool(self.eval_expr(expr.right, env))

        left = self.eval_expr(expr.left, env)
        right = self.eval_expr(expr.right, env)

        op = expr.op
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return self.to_str(left) + self.to_str(right)
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise InterpreterError("Division by zero")
            return left / right
        if op == 'div':
            if right == 0:
                raise InterpreterError("Division by zero")
            return int(left) // int(right)
        if op == 'mod':
            return int(left) % int(right)
        if op == '^':
            return left ** right
        if op == '=':
            return left == right
        if op in ('!=', '<>'):
            return left != right
        if op == '<':
            return left < right
        if op == '>':
            return left > right
        if op == '<=':
            return left <= right
        if op == '>=':
            return left >= right

        raise InterpreterError(f"Unknown operator: {op}")

    # ── Assignment target ─────────────────────────────────────────────────────

    def assign_target(self, target, value, env):
        if isinstance(target, Var):
            env.set_existing(target.name, value)

        elif isinstance(target, FieldAccess):
            # target.obj must evaluate to a record (dict)
            obj_val = self.eval_expr(target.obj, env)
            if not isinstance(obj_val, dict):
                obj_val = {}
            obj_val[target.field.lower()] = value
            # Write the modified record back
            self._write_back_field(target.obj, obj_val, env)

        elif isinstance(target, ArrayAccess):
            arr = self._get_array_for_write(target.name, env)
            if len(target.indices) == 1:
                idx = self.eval_expr(target.indices[0], env)
                if isinstance(idx, float):
                    idx = int(idx)
                arr[idx] = value
            else:
                indices = []
                for i in target.indices:
                    iv = self.eval_expr(i, env)
                    if isinstance(iv, float):
                        iv = int(iv)
                    indices.append(iv)
                arr[tuple(indices)] = value
            # Write the array back to its container
            self._write_back_array(target.name, arr, env)

    def _get_array_for_write(self, name_or_expr, env):
        if isinstance(name_or_expr, str):
            arr = env.get(name_or_expr)
        else:
            arr = self.eval_expr(name_or_expr, env)
        if not isinstance(arr, dict):
            arr = {}
        return arr

    def _write_back_array(self, name_or_expr, arr, env):
        if isinstance(name_or_expr, str):
            env.set_existing(name_or_expr, arr)
        elif isinstance(name_or_expr, FieldAccess):
            obj_val = self.eval_expr(name_or_expr.obj, env)
            if isinstance(obj_val, dict):
                obj_val[name_or_expr.field.lower()] = arr
            self._write_back_field(name_or_expr.obj, obj_val, env)
        elif isinstance(name_or_expr, Var):
            env.set_existing(name_or_expr.name, arr)

    def _write_back_field(self, obj_expr, updated_record, env):
        """Recursively write a modified record back to its storage location."""
        if isinstance(obj_expr, Var):
            env.set_existing(obj_expr.name, updated_record)
        elif isinstance(obj_expr, FieldAccess):
            parent_val = self.eval_expr(obj_expr.obj, env)
            if isinstance(parent_val, dict):
                parent_val[obj_expr.field.lower()] = updated_record
            self._write_back_field(obj_expr.obj, parent_val, env)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def to_str(self, v):
        if isinstance(v, bool):
            return 'vrai' if v else 'faux'
        if isinstance(v, float):
            if v == int(v):
                return str(int(v))
            return str(v)
        if v is None:
            return ''
        return str(v)

    def parse_input(self, s):
        s = s.strip()
        if s.lower() == 'vrai':
            return True
        if s.lower() == 'faux':
            return False
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s
