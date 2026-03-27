#!/usr/bin/env python3
import sys
import argparse
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def main():
    ap = argparse.ArgumentParser(description='French algo interpreter')
    ap.add_argument('file', help='Algorithm file (.algo)')
    ap.add_argument('--inputs', help='Comma-separated input values', default='')
    args = ap.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        input_queue = []
        if args.inputs:
            input_queue = [x.strip() for x in args.inputs.split(',')]
        interp = Interpreter(program, input_queue)
        interp.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
