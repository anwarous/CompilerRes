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
    declarations: list = field(default_factory=list)

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

# ── Declaration AST nodes ────────────────────────────────────────────────────

@dataclass
class VarDecl:
    name: str
    type_name: str       # 'entier', 'réel', 'booléen', 'caractère', 'chaîne'

@dataclass
class ArrayDecl:
    name: str
    rows: object         # expr – number of elements (1-D) or rows (2-D)
    cols: object         # None for 1-D, expr for 2-D
    element_type: str

@dataclass
class RecordField:
    name: str
    type_name: str

@dataclass
class RecordDecl:
    name: str
    fields: list         # List[RecordField]

@dataclass
class FileDecl:
    name: str
    file_type: str       # 'texte' or element-type string

@dataclass
class TypeDef:
    """User-defined type: Nom_type = <TypeSpec>"""
    name: str
    definition: object   # ArrayDecl | RecordDecl | FileDecl | str

# ── Statement AST nodes ──────────────────────────────────────────────────────

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
    step: object         # None → default step of 1
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
    name: object         # str OR FieldAccess for record-array fields
    indices: list

@dataclass
class FieldAccess:
    obj: object          # Var | FieldAccess
    field: str

@dataclass
class RangeValue:
    """Represents the range v1 .. v2 used as a Selon case value."""
    start: object
    end: object

@dataclass
class SeIonCase:
    values: list         # list of expr | RangeValue
    body: list

@dataclass
class SeIon:
    expr: object
    cases: list          # List[SeIonCase]
    otherwise: object    # Optional[list]

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
    newline: bool = True

@dataclass
class LireStmt:
    args: list

@dataclass
class AvecStmt:
    record_name: str
    body: list

class ParseError(Exception):
    pass

class Parser:
    # Token types that mark the end of a block
    BLOCK_END_TOKENS = {TT.FIN, TT.FIN_SI, TT.FIN_POUR, TT.FIN_TANTQUE,
                        TT.FIN_SELON, TT.FIN_AVEC, TT.SINON, TT.JUSQUA, TT.EOF}

    # Token types that are valid simple type keywords
    TYPE_TOKENS = {TT.ENTIER, TT.REEL, TT.BOOLEEN, TT.CHAINE, TT.CARACTERE}

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

        # Parse declarations (between algorithm name and DEBUT)
        declarations = self.parse_declarations()

        # Parse body
        self.expect(TT.DEBUT)
        body = self.parse_block()
        self.expect(TT.FIN)

        return Program(tdnt=tdnt, procedures=procedures, functions=functions,
                       algo_name=algo_name, body=body, declarations=declarations)

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
        if tok.type in (TT.ENTIER, TT.REEL, TT.BOOLEEN, TT.CHAINE, TT.TABLEAU,
                        TT.CARACTERE):
            return self.advance().value.lower()
        elif tok.type == TT.ID:
            return self.advance().value.lower()
        return 'entier'

    # ── Declarations ────────────────────────────────────────────────────────

    def parse_declarations(self):
        """Parse variable/type declarations between the algorithm name and DEBUT."""
        decls = []
        while self.peek().type not in (TT.DEBUT, TT.EOF):
            decl = self.parse_one_declaration()
            if decl is not None:
                decls.append(decl)
        return decls

    def parse_one_declaration(self):
        """Parse a single declaration line.  Returns a decl node or None."""
        tok = self.peek()

        # Skip section headers like "Variables :", "Constantes :", etc.
        if tok.type == TT.ID:
            if self.peek(1).type == TT.COLON:
                # Could be a section header "Objets :" or a record field "x : Type"
                # We're at the top level here, so treat as section header and skip.
                self.advance()  # name
                self.advance()  # colon
                return None

        # Type definition: NomType = TypeSpec
        if tok.type == TT.ID and self.peek(1).type == TT.EQ:
            name = self.advance().value  # consume Name
            self.advance()               # consume =
            return self._parse_type_spec_as_typedef(name)

        # Variable / array / record / file declaration: Name TypeSpec
        if tok.type == TT.ID:
            name = self.advance().value
            return self._parse_type_spec_as_decl(name)

        # Skip unknown tokens in declaration section
        self.advance()
        return None

    def _parse_type_spec_as_decl(self, name):
        """Parse the type specification and return the appropriate Decl node."""
        tok = self.peek()

        if tok.type == TT.TABLEAU:
            return self._parse_array_decl(name)

        if tok.type == TT.ENREGISTREMENT:
            return self._parse_record_decl(name)

        if tok.type == TT.FICHIER:
            return self._parse_file_decl(name)

        # Simple types
        if tok.type in self.TYPE_TOKENS:
            type_name = self.advance().value.lower()
            # Handle "Chaîne de caractères"
            if tok.type == TT.CHAINE:
                if self.peek().type == TT.DE and self.peek(1).type == TT.CARACTERE:
                    self.advance()  # de
                    self.advance()  # caractères
            return VarDecl(name=name, type_name=type_name)

        # Unknown type – skip and return a plain VarDecl with type 'entier'
        return VarDecl(name=name, type_name='entier')

    def _parse_type_spec_as_typedef(self, name):
        """Parse a type definition (NomType = ...)."""
        tok = self.peek()

        if tok.type == TT.TABLEAU:
            decl = self._parse_array_decl(name)
            return TypeDef(name=name, definition=decl)

        if tok.type == TT.ENREGISTREMENT:
            decl = self._parse_record_decl(name)
            return TypeDef(name=name, definition=decl)

        if tok.type == TT.FICHIER:
            decl = self._parse_file_decl(name)
            return TypeDef(name=name, definition=decl)

        # Scalar type alias
        type_name = self.parse_type_name()
        return TypeDef(name=name, definition=type_name)

    def _parse_array_decl(self, name):
        """Parse: Tableau de N [lignes * M colonnes] Type"""
        self.advance()  # consume 'Tableau'
        self.expect(TT.DE)
        rows_expr = self._parse_const_expr()

        # Check for 2-D: "N lignes * M colonnes"
        if self.peek().type == TT.LIGNES:
            self.advance()  # lignes
            self.match(TT.STAR)  # *
            cols_expr = self._parse_const_expr()
            if self.peek().type == TT.COLONNES:
                self.advance()  # colonnes
            elem_type = self.parse_type_name()
            return ArrayDecl(name=name, rows=rows_expr, cols=cols_expr,
                             element_type=elem_type)

        # 1-D
        elem_type = self.parse_type_name()
        return ArrayDecl(name=name, rows=rows_expr, cols=None,
                         element_type=elem_type)

    def _parse_const_expr(self):
        """Parse a simple constant integer or identifier (used in declarations)."""
        if self.peek().type == TT.INT_LIT:
            return Literal(int(self.advance().value))
        if self.peek().type == TT.ID:
            return Var(self.advance().value)
        return Literal(0)

    def _parse_record_decl(self, name):
        """Parse: Enregistrement  field1 : Type1 ...  Fin"""
        self.advance()  # consume 'Enregistrement'
        fields = []
        while self.peek().type not in (TT.FIN, TT.DEBUT, TT.EOF):
            if self.peek().type == TT.ID:
                field_name = self.advance().value
                self.expect(TT.COLON)
                field_type = self.parse_type_name()
                fields.append(RecordField(name=field_name, type_name=field_type))
            else:
                self.advance()
        if self.peek().type == TT.FIN:
            self.advance()  # consume 'Fin'
        return RecordDecl(name=name, fields=fields)

    def _parse_file_decl(self, name):
        """Parse: Fichier Texte  OR  Fichier de Type"""
        self.advance()  # consume 'Fichier'
        if self.peek().type == TT.TEXTE:
            self.advance()
            return FileDecl(name=name, file_type='texte')
        if self.peek().type == TT.DE:
            self.advance()  # de
            elem_type = self.parse_type_name()
            return FileDecl(name=name, file_type=elem_type)
        return FileDecl(name=name, file_type='texte')

    # ── Procedures / Functions ───────────────────────────────────────────────

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
        elif tok.type in (TT.ENTIER, TT.REEL, TT.BOOLEEN, TT.CHAINE, TT.CARACTERE):
            return self.advance().value.lower()
        elif tok.type == TT.ID:
            return self.advance().value.lower()
        return 'entier'

    # ── Block / Statement ────────────────────────────────────────────────────

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

        if tok.type == TT.SELON:
            return self.parse_selon()

        if tok.type == TT.AVEC:
            return self.parse_avec()

        if tok.type == TT.RETOURNER:
            self.advance()
            val = self.parse_expr()
            return Return(value=val)

        if tok.type == TT.ECRIRE:
            return self.parse_ecrire(newline=True)

        if tok.type == TT.ECRIRE_NL:
            return self.parse_ecrire(newline=True)

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
        step = None
        if self.peek().type == TT.PAS:
            self.advance()  # Pas
            self.expect(TT.EQ)
            step = self.parse_expr()
        self.expect(TT.FAIRE)
        body = self.parse_block()
        self.expect(TT.FIN_POUR)
        return For(var=var, start=start, end=end, step=step, body=body)

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

    def parse_selon(self):
        """Parse: Selon <expr>  case1: body1 ... [Sinon bodyN] Fin Selon"""
        self.expect(TT.SELON)
        expr = self.parse_expr()
        self.match(TT.FAIRE)  # optional 'Faire'
        cases = []
        otherwise = None

        while self.peek().type not in (TT.FIN_SELON, TT.EOF):
            if self.peek().type == TT.SINON:
                self.advance()  # consume 'Sinon'
                otherwise = self.parse_selon_body()
                break
            # Parse case values (possibly comma-separated, possibly ranges)
            values = [self.parse_selon_value()]
            while self.peek().type == TT.COMMA:
                self.advance()
                values.append(self.parse_selon_value())
            self.expect(TT.COLON)
            body = self.parse_selon_body()
            cases.append(SeIonCase(values=values, body=body))

        self.expect(TT.FIN_SELON)
        return SeIon(expr=expr, cases=cases, otherwise=otherwise)

    def parse_avec(self):
        """Parse: Avec <record_name> <body> Fin Avec"""
        self.expect(TT.AVEC)
        tok = self.peek()
        if tok.type in (TT.ID, TT.A):
            name = self.advance().value
        else:
            name = self.expect(TT.ID).value  # raises ParseError with a clear message
        body = self.parse_block()
        self.expect(TT.FIN_AVEC)
        return AvecStmt(record_name=name, body=body)

    def parse_selon_value(self):
        """Parse a single case value: literal or literal..literal range."""
        neg = False
        if self.peek().type == TT.MINUS:
            self.advance()
            neg = True
        tok = self.peek()
        if tok.type in (TT.INT_LIT, TT.FLOAT_LIT):
            self.advance()
            v = int(tok.value) if tok.type == TT.INT_LIT else float(tok.value)
            if neg:
                v = -v
            start_val = Literal(v)
        elif tok.type == TT.STRING_LIT:
            self.advance()
            start_val = Literal(tok.value)
        elif tok.type == TT.CHAR_LIT:
            self.advance()
            start_val = Literal(tok.value)
        elif tok.type in (TT.VRAI, TT.FAUX):
            self.advance()
            start_val = Literal(tok.type == TT.VRAI)
        elif tok.type == TT.ID:
            self.advance()
            start_val = Var(tok.value)
        else:
            start_val = Literal(0)
        # Check for range  v1 .. v2
        if self.peek().type == TT.POINT_POINT:
            self.advance()
            neg2 = False
            if self.peek().type == TT.MINUS:
                self.advance()
                neg2 = True
            tok2 = self.peek()
            if tok2.type in (TT.INT_LIT, TT.FLOAT_LIT):
                self.advance()
                v2 = int(tok2.value) if tok2.type == TT.INT_LIT else float(tok2.value)
                if neg2:
                    v2 = -v2
                end_val = Literal(v2)
            else:
                end_val = Literal(0)
            return RangeValue(start=start_val, end=end_val)
        return start_val

    def parse_selon_body(self):
        """Parse statements for a Selon case body, stopping before next case or FIN_SELON."""
        stmts = []
        while self.peek().type not in (TT.FIN_SELON, TT.EOF):
            if self.peek().type == TT.SINON:
                break
            if self._is_selon_case_start():
                break
            stmt = self.parse_stmt()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def _is_selon_case_start(self):
        """Return True if current position looks like the start of a new Selon case label."""
        i = 0
        # Optional leading minus
        if self.peek(i).type == TT.MINUS:
            i += 1
        tok = self.peek(i)
        if tok.type not in (TT.INT_LIT, TT.FLOAT_LIT, TT.STRING_LIT,
                             TT.CHAR_LIT, TT.VRAI, TT.FAUX, TT.ID):
            return False
        i += 1
        # Optional range  .. val
        if self.peek(i).type == TT.POINT_POINT:
            i += 1
            if self.peek(i).type == TT.MINUS:
                i += 1
            if self.peek(i).type not in (TT.INT_LIT, TT.FLOAT_LIT, TT.STRING_LIT,
                                          TT.CHAR_LIT, TT.VRAI, TT.FAUX, TT.ID):
                return False
            i += 1
        # Allow comma-separated values
        while self.peek(i).type == TT.COMMA:
            i += 1
            if self.peek(i).type == TT.MINUS:
                i += 1
            if self.peek(i).type not in (TT.INT_LIT, TT.FLOAT_LIT, TT.STRING_LIT,
                                          TT.CHAR_LIT, TT.VRAI, TT.FAUX, TT.ID):
                return False
            i += 1
            if self.peek(i).type == TT.POINT_POINT:
                i += 1
                if self.peek(i).type == TT.MINUS:
                    i += 1
                if self.peek(i).type not in (TT.INT_LIT, TT.FLOAT_LIT, TT.STRING_LIT,
                                              TT.CHAR_LIT, TT.VRAI, TT.FAUX, TT.ID):
                    return False
                i += 1
        return self.peek(i).type == TT.COLON

    def parse_ecrire(self, newline=True):
        self.advance()  # consume ECRIRE or ECRIRE_NL
        self.expect(TT.LPAREN)
        args = []
        if self.peek().type != TT.RPAREN:
            args.append(self.parse_expr())
            while self.peek().type == TT.COMMA:
                self.advance()
                args.append(self.parse_expr())
        self.expect(TT.RPAREN)
        return EcrireStmt(args=args, newline=newline)

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
        # Field access
        if self.peek().type == TT.DOT:
            node = Var(name=name)
            while self.peek().type == TT.DOT:
                self.advance()
                field = self.expect(TT.ID).value
                node = FieldAccess(obj=node, field=field)
            if self.peek().type == TT.LBRACKET:
                self.advance()
                indices = [self.parse_expr()]
                while self.peek().type == TT.COMMA:
                    self.advance()
                    indices.append(self.parse_expr())
                self.expect(TT.RBRACKET)
                return ArrayAccess(name=node, indices=indices)
            return node
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

        # Field access chain before assignment
        if self.peek().type == TT.DOT:
            node = Var(name=name)
            while self.peek().type == TT.DOT:
                self.advance()
                field = self.expect(TT.ID).value
                node = FieldAccess(obj=node, field=field)
            # Could be followed by array index
            if self.peek().type == TT.LBRACKET:
                self.advance()
                indices = [self.parse_expr()]
                while self.peek().type == TT.COMMA:
                    self.advance()
                    indices.append(self.parse_expr())
                self.expect(TT.RBRACKET)
                target = ArrayAccess(name=node, indices=indices)
            else:
                target = node
            self.expect(TT.ASSIGN)
            value = self.parse_expr()
            return Assign(target=target, value=value)

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

    # ── Expression parsing with precedence ───────────────────────────────────

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
        base = self.parse_postfix()
        if self.peek().type == TT.CARET:
            self.advance()
            exp = self.parse_unary()  # right-associative
            return BinOp(op='^', left=base, right=exp)
        return base

    def parse_postfix(self):
        """Handle dot field access and array indexing after a primary."""
        node = self.parse_primary()
        while self.peek().type in (TT.DOT, TT.LBRACKET):
            if self.peek().type == TT.DOT:
                self.advance()
                field = self.expect(TT.ID).value
                node = FieldAccess(obj=node, field=field)
            elif self.peek().type == TT.LBRACKET:
                self.advance()
                indices = [self.parse_expr()]
                while self.peek().type == TT.COMMA:
                    self.advance()
                    indices.append(self.parse_expr())
                self.expect(TT.RBRACKET)
                node = ArrayAccess(name=node, indices=indices)
        return node

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

        if tok.type == TT.CHAR_LIT:
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

            # Array access (legacy path – parse_postfix handles the general case)
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
