from dataclasses import dataclass, field
from typing import List, Optional, Any
from lexer import Token, TT

@dataclass
class Program:
    tdnt: dict
    procedures: list
    functions: list
    algo_name: str
    body: list

@dataclass
class ProcDef:
    name: str
    params: list
    body: list

@dataclass
class FuncDef:
    name: str
    params: list
    return_type: str
    body: list

@dataclass
class Assign:
    target: object
    value: object

@dataclass
class If:
    condition: object
    then_block: list
    elif_list: list
    else_block: object

@dataclass
class For:
    var: str
    start: object
    end: object
    body: list

@dataclass
class While:
    condition: object
    body: list

@dataclass
class Repeat:
    body: list
    condition: object

@dataclass
class Return:
    value: object

@dataclass
class ProcCall:
    name: str
    args: list

@dataclass
class FuncCall:
    name: str
    args: list

@dataclass
class ArrayAccess:
    name: str
    indices: list

@dataclass
class BinOp:
    op: str
    left: object
    right: object

@dataclass
class UnaryOp:
    op: str
    operand: object

@dataclass
class Literal:
    value: object

@dataclass
class Var:
    name: str

@dataclass
class EcrireStmt:
    args: list

@dataclass
class LireStmt:
    args: list

class ParseError(Exception):
    pass

class Parser:
    # Token types that mark the end of a block
    BLOCK_END_TOKENS = {TT.FIN, TT.FIN_SI, TT.FIN_POUR, TT.FIN_TANTQUE, TT.SINON, TT.JUSQUA, TT.EOF}

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        p = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return self.tokens[-1]  # EOF

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, tt):
        tok = self.peek()
        if tok.type != tt:
            raise ParseError(f"Expected {tt.name} but got {tok.type.name} ({tok.value!r}) at line {tok.line}")
        return self.advance()

    def match(self, *types):
        if self.peek().type in types:
            return self.advance()
        return None

    def parse(self):
        tdnt = {}
        procedures = []
        functions = []

        # Parse optional TDNT block (with or without brackets)
        if self.peek().type == TT.LBRACKET and self.peek(1).type == TT.TDNT:
            self.advance()  # consume [
            tdnt = self.parse_tdnt()
            if self.peek().type == TT.RBRACKET:
                self.advance()
        elif self.peek().type == TT.TDNT:
            tdnt = self.parse_tdnt()

        # Parse procedures and functions (before the main algo)
        while self.peek().type in (TT.PROCEDURE, TT.FONCTION):
            if self.peek().type == TT.PROCEDURE:
                procedures.append(self.parse_procedure())
            else:
                functions.append(self.parse_function())

        # Parse Algorithme header
        self.expect(TT.ALGO)
        algo_name_tok = self.expect(TT.ID)
        algo_name = algo_name_tok.value

        # Optional 'prog princ'
        if self.peek().type == TT.PROG:
            self.advance()
            if self.peek().type == TT.PRINC:
                self.advance()

        # Parse body
        self.expect(TT.DEBUT)
        body = self.parse_block()
        self.expect(TT.FIN)

        return Program(tdnt=tdnt, procedures=procedures, functions=functions,
                       algo_name=algo_name, body=body)

    def parse_tdnt(self):
        if self.peek().type == TT.TDNT:
            self.advance()
        tdnt = {}
        while self.peek().type not in (TT.RBRACKET, TT.EOF, TT.PROCEDURE, TT.FONCTION, TT.ALGO):
            if self.peek().type == TT.ID:
                name = self.advance().value
                self.expect(TT.EQ)
                self.expect(TT.TABLEAU)
                self.expect(TT.DE)
                size_tok = self.expect(TT.INT_LIT)
                size = int(size_tok.value)
                base_type = self.parse_type_name()
                tdnt[name.lower()] = (size, base_type)
            else:
                self.advance()
        return tdnt

    def parse_type_name(self):
        tok = self.peek()
        if tok.type in (TT.ENTIER, TT.REEL, TT.BOOLEEN, TT.CHAINE, TT.TABLEAU):
            return self.advance().value.lower()
        elif tok.type == TT.ID:
            return self.advance().value.lower()
        return 'entier'

    def parse_procedure(self):
        self.expect(TT.PROCEDURE)
        name = self.expect(TT.ID).value
        params = []
        if self.peek().type == TT.LPAREN:
            self.advance()
            params = self.parse_params()
            self.expect(TT.RPAREN)
        self.expect(TT.DEBUT)
        body = self.parse_block()
        self.expect(TT.FIN)
        return ProcDef(name=name, params=params, body=body)

    def parse_function(self):
        self.expect(TT.FONCTION)
        name = self.expect(TT.ID).value
        params = []
        if self.peek().type == TT.LPAREN:
            self.advance()
            params = self.parse_params()
            self.expect(TT.RPAREN)
        self.expect(TT.COLON)
        return_type = self.parse_type_name()
        self.expect(TT.DEBUT)
        body = self.parse_block()
        self.expect(TT.FIN)
        return FuncDef(name=name, params=params, return_type=return_type, body=body)

    def parse_params(self):
        params = []
        while self.peek().type != TT.RPAREN and self.peek().type != TT.EOF:
            by_ref = False
            if self.peek().type == TT.AT:
                self.advance()
                by_ref = True
            param_name = self.expect(TT.ID).value
            self.expect(TT.COLON)
            param_type = self.parse_param_type()
            params.append((by_ref, param_name, param_type))
            if self.peek().type == TT.COMMA:
                self.advance()
        return params

    def parse_param_type(self):
        tok = self.peek()
        if tok.type == TT.TABLEAU:
            self.advance()
            return 'tableau'
        elif tok.type in (TT.ENTIER, TT.REEL, TT.BOOLEEN, TT.CHAINE):
            return self.advance().value.lower()
        elif tok.type == TT.ID:
            return self.advance().value.lower()
        return 'entier'

    def parse_block(self):
        stmts = []
        while self.peek().type not in self.BLOCK_END_TOKENS:
            stmt = self.parse_stmt()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def parse_stmt(self):
        tok = self.peek()

        if tok.type == TT.SI:
            return self.parse_if()

        if tok.type == TT.POUR:
            return self.parse_for()

        if tok.type == TT.TANT:
            return self.parse_while()

        if tok.type == TT.REPETER:
            return self.parse_repeat()

        if tok.type == TT.RETOURNER:
            self.advance()
            val = self.parse_expr()
            return Return(value=val)

        if tok.type == TT.ECRIRE:
            return self.parse_ecrire()

        if tok.type == TT.LIRE:
            return self.parse_lire()

        if tok.type in (TT.ID, TT.A):
            return self.parse_id_stmt()

        # Skip unknown tokens
        self.advance()
        return None

    def parse_if(self):
        self.expect(TT.SI)
        condition = self.parse_expr()
        self.expect(TT.ALORS)
        then_block = self.parse_block()
        elif_list = []
        else_block = None

        while self.peek().type == TT.SINON:
            sinon_line = self.peek().line
            self.advance()  # consume sinon
            # Only treat as elif if SI is on the same line as SINON
            if self.peek().type == TT.SI and self.peek().line == sinon_line:
                self.advance()  # consume si
                elif_cond = self.parse_expr()
                self.expect(TT.ALORS)
                elif_block = self.parse_block()
                elif_list.append((elif_cond, elif_block))
            else:
                else_block = self.parse_block()
                break

        self.expect(TT.FIN_SI)
        return If(condition=condition, then_block=then_block,
                  elif_list=elif_list, else_block=else_block)

    def parse_for(self):
        self.expect(TT.POUR)
        var = self.expect(TT.ID).value
        self.expect(TT.DE)
        start = self.parse_expr()
        self.expect(TT.A)
        end = self.parse_expr()
        self.expect(TT.FAIRE)
        body = self.parse_block()
        self.expect(TT.FIN_POUR)
        return For(var=var, start=start, end=end, body=body)

    def parse_while(self):
        self.expect(TT.TANT)
        self.expect(TT.QUE)
        condition = self.parse_expr()
        self.expect(TT.FAIRE)
        body = self.parse_block()
        self.expect(TT.FIN_TANTQUE)
        return While(condition=condition, body=body)

    def parse_repeat(self):
        self.expect(TT.REPETER)
        body = self.parse_block()
        self.expect(TT.JUSQUA)
        condition = self.parse_expr()
        return Repeat(body=body, condition=condition)

    def parse_ecrire(self):
        self.expect(TT.ECRIRE)
        self.expect(TT.LPAREN)
        args = []
        if self.peek().type != TT.RPAREN:
            args.append(self.parse_expr())
            while self.peek().type == TT.COMMA:
                self.advance()
                args.append(self.parse_expr())
        self.expect(TT.RPAREN)
        return EcrireStmt(args=args)

    def parse_lire(self):
        self.expect(TT.LIRE)
        self.expect(TT.LPAREN)
        args = []
        if self.peek().type != TT.RPAREN:
            args.append(self.parse_lire_target())
            while self.peek().type == TT.COMMA:
                self.advance()
                args.append(self.parse_lire_target())
        self.expect(TT.RPAREN)
        return LireStmt(args=args)

    def parse_lire_target(self):
        # Accept ID or keyword 'a' as variable name
        tok = self.peek()
        if tok.type in (TT.ID, TT.A):
            name = self.advance().value
        else:
            name = self.expect(TT.ID).value
        if self.peek().type == TT.LBRACKET:
            self.advance()
            indices = [self.parse_expr()]
            while self.peek().type == TT.COMMA:
                self.advance()
                indices.append(self.parse_expr())
            self.expect(TT.RBRACKET)
            return ArrayAccess(name=name, indices=indices)
        return Var(name=name)

    def parse_id_stmt(self):
        name = self.advance().value

        # Array access assignment
        if self.peek().type == TT.LBRACKET:
            self.advance()
            indices = [self.parse_expr()]
            while self.peek().type == TT.COMMA:
                self.advance()
                indices.append(self.parse_expr())
            self.expect(TT.RBRACKET)
            target = ArrayAccess(name=name, indices=indices)
            self.expect(TT.ASSIGN)
            value = self.parse_expr()
            return Assign(target=target, value=value)

        # Procedure call
        if self.peek().type == TT.LPAREN:
            self.advance()
            args = []
            if self.peek().type != TT.RPAREN:
                args.append(self.parse_expr())
                while self.peek().type == TT.COMMA:
                    self.advance()
                    args.append(self.parse_expr())
            self.expect(TT.RPAREN)
            return ProcCall(name=name, args=args)

        # Variable assignment
        self.expect(TT.ASSIGN)
        value = self.parse_expr()
        return Assign(target=Var(name=name), value=value)

    # Expression parsing with precedence
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek().type == TT.OU:
            self.advance()
            right = self.parse_and()
            left = BinOp(op='ou', left=left, right=right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek().type == TT.ET:
            self.advance()
            right = self.parse_not()
            left = BinOp(op='et', left=left, right=right)
        return left

    def parse_not(self):
        if self.peek().type == TT.NON:
            self.advance()
            operand = self.parse_not()
            return UnaryOp(op='non', operand=operand)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_add()
        while self.peek().type in (TT.EQ, TT.NEQ, TT.LT, TT.GT, TT.LE, TT.GE):
            op = self.advance().value
            right = self.parse_add()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().type in (TT.PLUS, TT.MINUS):
            op = self.advance().value
            right = self.parse_mul()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek().type in (TT.STAR, TT.SLASH, TT.DIV, TT.MOD):
            op = self.advance().value.lower()
            right = self.parse_unary()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_unary(self):
        if self.peek().type == TT.MINUS:
            self.advance()
            operand = self.parse_power()
            return UnaryOp(op='-', operand=operand)
        return self.parse_power()

    def parse_power(self):
        base = self.parse_primary()
        if self.peek().type == TT.CARET:
            self.advance()
            exp = self.parse_unary()  # right-associative
            return BinOp(op='^', left=base, right=exp)
        return base

    def parse_primary(self):
        tok = self.peek()

        if tok.type == TT.INT_LIT:
            self.advance()
            return Literal(value=int(tok.value))

        if tok.type == TT.FLOAT_LIT:
            self.advance()
            return Literal(value=float(tok.value))

        if tok.type == TT.STRING_LIT:
            self.advance()
            return Literal(value=tok.value)

        if tok.type == TT.VRAI:
            self.advance()
            return Literal(value=True)

        if tok.type == TT.FAUX:
            self.advance()
            return Literal(value=False)

        if tok.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT.RPAREN)
            return expr

        if tok.type == TT.ID:
            name = self.advance().value

            # Function call
            if self.peek().type == TT.LPAREN:
                self.advance()
                args = []
                if self.peek().type != TT.RPAREN:
                    args.append(self.parse_expr())
                    while self.peek().type == TT.COMMA:
                        self.advance()
                        args.append(self.parse_expr())
                self.expect(TT.RPAREN)
                return FuncCall(name=name, args=args)

            # Array access
            if self.peek().type == TT.LBRACKET:
                self.advance()
                indices = [self.parse_expr()]
                while self.peek().type == TT.COMMA:
                    self.advance()
                    indices.append(self.parse_expr())
                self.expect(TT.RBRACKET)
                return ArrayAccess(name=name, indices=indices)

            return Var(name=name)

        # Allow keyword 'a'/'à' as identifier in expression context (e.g., variable named 'a')
        if tok.type == TT.A:
            self.advance()
            name = tok.value
            if self.peek().type == TT.LBRACKET:
                self.advance()
                indices = [self.parse_expr()]
                while self.peek().type == TT.COMMA:
                    self.advance()
                    indices.append(self.parse_expr())
                self.expect(TT.RBRACKET)
                return ArrayAccess(name=name, indices=indices)
            return Var(name=name)

        raise ParseError(f"Unexpected token {tok.type.name} ({tok.value!r}) at line {tok.line}")
