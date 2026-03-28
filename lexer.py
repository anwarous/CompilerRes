import unicodedata
from enum import Enum, auto
from dataclasses import dataclass
from typing import List

class TT(Enum):
    INT_LIT = auto()
    FLOAT_LIT = auto()
    STRING_LIT = auto()
    CHAR_LIT = auto()
    ID = auto()
    ALGO = auto()
    DEBUT = auto()
    FIN = auto()
    FIN_SI = auto()
    FIN_POUR = auto()
    FIN_TANTQUE = auto()
    FIN_SELON = auto()
    SI = auto()
    ALORS = auto()
    SINON = auto()
    POUR = auto()
    DE = auto()
    A = auto()
    FAIRE = auto()
    TANT = auto()
    QUE = auto()
    REPETER = auto()
    JUSQUA = auto()
    RETOURNER = auto()
    PROCEDURE = auto()
    FONCTION = auto()
    LIRE = auto()
    ECRIRE = auto()
    ECRIRE_NL = auto()
    DIV = auto()
    MOD = auto()
    ET = auto()
    OU = auto()
    NON = auto()
    VRAI = auto()
    FAUX = auto()
    PROG = auto()
    PRINC = auto()
    TDNT = auto()
    TABLEAU = auto()
    ENTIER = auto()
    REEL = auto()
    BOOLEEN = auto()
    CHAINE = auto()
    CARACTERE = auto()
    ENREGISTREMENT = auto()
    FICHIER = auto()
    TEXTE = auto()
    SELON = auto()
    LIGNES = auto()
    COLONNES = auto()
    PAS = auto()
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    EQ = auto()
    NEQ = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    AT = auto()
    DOT = auto()
    POINT_POINT = auto()
    EOF = auto()

@dataclass
class Token:
    type: TT
    value: str
    line: int
    col: int
    def __repr__(self):
        return f'Token({self.type.name}, {self.value!r}, {self.line}:{self.col})'

KEYWORDS = {
    'algorithme': TT.ALGO,
    'algo': TT.ALGO,
    'debut': TT.DEBUT,
    'd\u00e9but': TT.DEBUT,
    'fin': TT.FIN,
    'si': TT.SI,
    'alors': TT.ALORS,
    'sinon': TT.SINON,
    'pour': TT.POUR,
    'de': TT.DE,
    'a': TT.A,
    '\u00e0': TT.A,
    'faire': TT.FAIRE,
    'tant': TT.TANT,
    'que': TT.QUE,
    'repeter': TT.REPETER,
    'r\u00e9p\u00e9ter': TT.REPETER,
    'retourner': TT.RETOURNER,
    'procedure': TT.PROCEDURE,
    'proc\u00e9dure': TT.PROCEDURE,
    'fonction': TT.FONCTION,
    'lire': TT.LIRE,
    'ecrire': TT.ECRIRE,
    '\u00e9crire': TT.ECRIRE,
    'ecrire_nl': TT.ECRIRE_NL,
    '\u00e9crire_nl': TT.ECRIRE_NL,
    'div': TT.DIV,
    'mod': TT.MOD,
    'et': TT.ET,
    'ou': TT.OU,
    'non': TT.NON,
    'vrai': TT.VRAI,
    'faux': TT.FAUX,
    'prog': TT.PROG,
    'princ': TT.PRINC,
    'tdnt': TT.TDNT,
    'tableau': TT.TABLEAU,
    'entier': TT.ENTIER,
    'reel': TT.REEL,
    'r\u00e9el': TT.REEL,
    'booleen': TT.BOOLEEN,
    'bool\u00e9en': TT.BOOLEEN,
    'chaine': TT.CHAINE,
    'cha\u00eene': TT.CHAINE,
    'caractere': TT.CARACTERE,
    'caract\u00e8re': TT.CARACTERE,
    'caract\u00e8res': TT.CARACTERE,
    'enregistrement': TT.ENREGISTREMENT,
    'fichier': TT.FICHIER,
    'texte': TT.TEXTE,
    'selon': TT.SELON,
    'lignes': TT.LIGNES,
    'colonnes': TT.COLONNES,
    'pas': TT.PAS,
}

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def peek(self, offset=0):
        p = self.pos + offset
        if p < len(self.source):
            return self.source[p]
        return ''

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def is_letter(self, ch):
        if not ch:
            return False
        cat = unicodedata.category(ch)
        return cat.startswith('L') or ch == '_'

    def is_digit(self, ch):
        return ch.isdigit()

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch in ' \t\r\n':
                self.advance()
            elif ch == '/' and self.peek(1) == '/':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.advance()
            else:
                break

    def read_word(self):
        start = self.pos
        while self.pos < len(self.source) and (self.is_letter(self.source[self.pos]) or self.is_digit(self.source[self.pos])):
            self.advance()
        return self.source[start:self.pos]

    def save_state(self):
        return (self.pos, self.line, self.col)

    def restore_state(self, state):
        self.pos, self.line, self.col = state

    def skip_all_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r\n':
            self.advance()

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break

            ch = self.source[self.pos]
            line, col = self.line, self.col

            # Character literal 'x'
            if ch == "'":
                self.advance()
                c = self.advance() if self.pos < len(self.source) and self.source[self.pos] != "'" else ''
                if self.pos < len(self.source) and self.source[self.pos] == "'":
                    self.advance()  # closing '
                self.tokens.append(Token(TT.CHAR_LIT, c, line, col))
                continue

            # String literal
            if ch == '"':
                self.advance()
                s = []
                while self.pos < len(self.source) and self.source[self.pos] != '"':
                    s.append(self.advance())
                if self.pos < len(self.source):
                    self.advance()  # closing "
                self.tokens.append(Token(TT.STRING_LIT, ''.join(s), line, col))
                continue

            # Number literal
            if self.is_digit(ch) or (ch == '.' and self.peek(1).isdigit()):
                num_str = []
                is_float = False
                while self.pos < len(self.source) and self.is_digit(self.source[self.pos]):
                    num_str.append(self.advance())
                if self.pos < len(self.source) and self.source[self.pos] == '.':
                    is_float = True
                    num_str.append(self.advance())
                    while self.pos < len(self.source) and self.is_digit(self.source[self.pos]):
                        num_str.append(self.advance())
                s = ''.join(num_str)
                if is_float:
                    self.tokens.append(Token(TT.FLOAT_LIT, s, line, col))
                else:
                    self.tokens.append(Token(TT.INT_LIT, s, line, col))
                continue

            # Identifiers and keywords
            if self.is_letter(ch):
                word = self.read_word()
                word_lower = word.lower()

                # Special: jusqu'a / jusqu'à
                if word_lower == 'jusqu':
                    if self.pos < len(self.source) and self.source[self.pos] in ("'", '\u2019'):
                        self.advance()  # consume apostrophe
                        rest = self.read_word()
                        rest_lower = rest.lower()
                        if rest_lower in ('a', '\u00e0'):
                            self.tokens.append(Token(TT.JUSQUA, "jusqu'a", line, col))
                            continue
                    self.tokens.append(Token(TT.ID, word, line, col))
                    continue

                # Special: fin - look ahead for compound tokens
                if word_lower == 'fin':
                    state = self.save_state()
                    self.skip_all_whitespace()
                    next_word = self.read_word()
                    next_lower = next_word.lower()
                    if next_lower == 'si':
                        self.tokens.append(Token(TT.FIN_SI, 'fin si', line, col))
                        continue
                    elif next_lower == 'pour':
                        self.tokens.append(Token(TT.FIN_POUR, 'fin pour', line, col))
                        continue
                    elif next_lower == 'selon':
                        self.tokens.append(Token(TT.FIN_SELON, 'fin selon', line, col))
                        continue
                    elif next_lower == 'tant':
                        state2 = self.save_state()
                        self.skip_all_whitespace()
                        que_word = self.read_word()
                        if que_word.lower() == 'que':
                            self.tokens.append(Token(TT.FIN_TANTQUE, 'fin tant que', line, col))
                            continue
                        else:
                            self.restore_state(state2)
                            self.tokens.append(Token(TT.FIN_TANTQUE, 'fin tant que', line, col))
                            continue
                    elif next_lower in ('tantque', 'fintantque'):
                        self.tokens.append(Token(TT.FIN_TANTQUE, 'fin tant que', line, col))
                        continue
                    else:
                        self.restore_state(state)
                        self.tokens.append(Token(TT.FIN, 'fin', line, col))
                        continue

                # Compound finsi, finpour, fintantque, finselon (no space)
                if word_lower == 'finsi':
                    self.tokens.append(Token(TT.FIN_SI, 'finsi', line, col))
                    continue
                if word_lower == 'finpour':
                    self.tokens.append(Token(TT.FIN_POUR, 'finpour', line, col))
                    continue
                if word_lower == 'fintantque':
                    self.tokens.append(Token(TT.FIN_TANTQUE, 'fintantque', line, col))
                    continue
                if word_lower == 'finselon':
                    self.tokens.append(Token(TT.FIN_SELON, 'finselon', line, col))
                    continue

                if word_lower in KEYWORDS:
                    self.tokens.append(Token(KEYWORDS[word_lower], word, line, col))
                else:
                    self.tokens.append(Token(TT.ID, word, line, col))
                continue

            # Operators
            if ch == '<':
                if self.peek(1) == '-' and self.peek(2) == '-':
                    self.advance(); self.advance(); self.advance()
                    self.tokens.append(Token(TT.ASSIGN, '<--', line, col))
                elif self.peek(1) == '-':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TT.ASSIGN, '<-', line, col))
                elif self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TT.LE, '<=', line, col))
                elif self.peek(1) == '>':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TT.NEQ, '<>', line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TT.LT, '<', line, col))
                continue

            if ch == '>':
                if self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TT.GE, '>=', line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TT.GT, '>', line, col))
                continue

            if ch == '!':
                if self.peek(1) == '=':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TT.NEQ, '!=', line, col))
                else:
                    self.advance()
                continue

            if ch == '=':
                self.advance()
                self.tokens.append(Token(TT.EQ, '=', line, col))
                continue

            if ch == '+':
                self.advance()
                self.tokens.append(Token(TT.PLUS, '+', line, col))
                continue

            if ch == '-':
                self.advance()
                self.tokens.append(Token(TT.MINUS, '-', line, col))
                continue

            if ch == '*':
                self.advance()
                self.tokens.append(Token(TT.STAR, '*', line, col))
                continue

            if ch == '/':
                self.advance()
                self.tokens.append(Token(TT.SLASH, '/', line, col))
                continue

            if ch == '^':
                self.advance()
                self.tokens.append(Token(TT.CARET, '^', line, col))
                continue

            if ch == '(':
                self.advance()
                self.tokens.append(Token(TT.LPAREN, '(', line, col))
                continue

            if ch == ')':
                self.advance()
                self.tokens.append(Token(TT.RPAREN, ')', line, col))
                continue

            if ch == '[':
                self.advance()
                self.tokens.append(Token(TT.LBRACKET, '[', line, col))
                continue

            if ch == ']':
                self.advance()
                self.tokens.append(Token(TT.RBRACKET, ']', line, col))
                continue

            if ch == ',':
                self.advance()
                self.tokens.append(Token(TT.COMMA, ',', line, col))
                continue

            if ch == ':':
                self.advance()
                self.tokens.append(Token(TT.COLON, ':', line, col))
                continue

            if ch == '@':
                self.advance()
                self.tokens.append(Token(TT.AT, '@', line, col))
                continue

            if ch == '.':
                if self.peek(1) == '.':
                    self.advance(); self.advance()
                    self.tokens.append(Token(TT.POINT_POINT, '..', line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TT.DOT, '.', line, col))
                continue

            # Skip unknown characters
            self.advance()

        self.tokens.append(Token(TT.EOF, '', self.line, self.col))
        return self.tokens
