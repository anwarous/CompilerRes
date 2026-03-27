from parser import (Program, ProcDef, FuncDef, Assign, If, For, While, Repeat,
                    Return, ProcCall, FuncCall, ArrayAccess, BinOp, UnaryOp,
                    Literal, Var, EcrireStmt, LireStmt)

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class InterpreterError(Exception):
    pass

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

        for proc in program.procedures:
            self.procedures[proc.name.lower()] = proc
        for func in program.functions:
            self.functions[func.name.lower()] = func

    def run(self):
        self.exec_block(self.program.body, self.global_env)

    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, stmt, env):
        if isinstance(stmt, Assign):
            val = self.eval_expr(stmt.value, env)
            self.assign_target(stmt.target, val, env)

        elif isinstance(stmt, EcrireStmt):
            parts = []
            for a in stmt.args:
                v = self.eval_expr(a, env)
                parts.append(self.to_str(v))
            line = ''.join(parts)
            print(line)
            self.output.append(line)

        elif isinstance(stmt, LireStmt):
            for arg in stmt.args:
                if self.input_index < len(self.input_queue):
                    val_str = self.input_queue[self.input_index]
                    self.input_index += 1
                else:
                    val_str = input()
                val = self.parse_input(val_str)
                self.assign_target(arg, val, env)

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
            start = self.eval_expr(stmt.start, env)
            end = self.eval_expr(stmt.end, env)
            if isinstance(start, float):
                start = int(start)
            if isinstance(end, float):
                end = int(end)
            for i in range(start, end + 1):
                env.set(stmt.var, i)
                self.exec_block(stmt.body, env)

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

        elif isinstance(stmt, Return):
            val = self.eval_expr(stmt.value, env)
            raise ReturnException(val)

        elif isinstance(stmt, ProcCall):
            self.call_proc_or_builtin(stmt.name, stmt.args, env)

    def call_proc_or_builtin(self, name, args, env):
        name_lower = name.lower()
        if name_lower == 'ecrire':
            parts = []
            for a in args:
                v = self.eval_expr(a, env)
                parts.append(self.to_str(v))
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

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Var):
            return env.get(expr.name)

        if isinstance(expr, ArrayAccess):
            arr = env.get(expr.name)
            if isinstance(arr, str):
                # String indexing: mdp[i]
                idx = self.eval_expr(expr.indices[0], env)
                if isinstance(idx, float):
                    idx = int(idx)
                return arr[idx] if 0 <= idx < len(arr) else ''
            if not isinstance(arr, dict):
                arr = {}
                env.set(expr.name, arr)
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

    def eval_func_call(self, expr, env):
        name = expr.name.lower()
        args = expr.args

        # Builtins
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
        if name == 'ecrire':
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

    def assign_target(self, target, value, env):
        if isinstance(target, Var):
            env.set_existing(target.name, value)
        elif isinstance(target, ArrayAccess):
            arr = env.get(target.name)
            if not isinstance(arr, dict):
                arr = {}
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
            env.set_existing(target.name, arr)

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
