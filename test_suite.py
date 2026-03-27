import pytest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def run_algo(filename, inputs_str=''):
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    input_queue = [x.strip() for x in inputs_str.split(',')] if inputs_str else []

    output_lines = []
    def mock_print(*args, **kwargs):
        sep = kwargs.get('sep', ' ')
        output_lines.append(sep.join(str(a) for a in args))

    interp = Interpreter(program, input_queue)
    with patch('builtins.print', mock_print):
        interp.run()
    return output_lines

BASE = os.path.join(os.path.dirname(__file__), 'algos')

def test_ex01_pour():
    lines = run_algo(f'{BASE}/ex01_pour.algo', '5')
    expected = [str(i) for i in range(5, 16)]
    valid_nums = {str(i) for i in range(0, 100)}
    actual_nums = [l for l in lines if l.strip() in valid_nums]
    assert actual_nums == expected

def test_ex02_addition():
    lines = run_algo(f'{BASE}/ex02_addition.algo', '3,5,2,0')
    assert any('10' in l for l in lines)

def test_ex03_puissance():
    lines = run_algo(f'{BASE}/ex03_puissance.algo', '2,10')
    assert any('1024' in l for l in lines)

def test_ex04_somme_pairs():
    lines = run_algo(f'{BASE}/ex04_somme_pairs.algo', '4,3,6,0')
    assert any('10' in l for l in lines)

def test_ex05_inverse():
    lines = run_algo(f'{BASE}/ex05_inverse.algo', '1234')
    assert any('4321' in l for l in lines)

def test_ex06_parite_signe_pair_pos():
    lines = run_algo(f'{BASE}/ex06_parite_signe.algo', '4')
    assert any('Pair' in l and 'Positif' in l for l in lines)

def test_ex06_parite_signe_impair_neg():
    lines = run_algo(f'{BASE}/ex06_parite_signe.algo', '-3')
    assert any('Impair' in l and 'Negatif' in l for l in lines)

def test_ex07_puissance2():
    lines = run_algo(f'{BASE}/ex07_puissance2.algo', '3,4')
    assert any('81' in l for l in lines)

def test_ex08_max_min():
    lines = run_algo(f'{BASE}/ex08_max_min.algo', '3,7,1,9,4')
    assert any('9' in l and 'max' in l.lower() for l in lines)
    assert any('1' in l and 'min' in l.lower() for l in lines)

def test_ex09_moyenne():
    lines = run_algo(f'{BASE}/ex09_moyenne.algo', '10,20,30,40,50')
    assert any('30' in l for l in lines)

def test_ex10_budget():
    lines = run_algo(f'{BASE}/ex10_budget.algo', '100,30,non')
    assert any('70' in l for l in lines)

def test_ex11_somme_chiffres():
    lines = run_algo(f'{BASE}/ex11_somme_chiffres.algo', '123')
    assert any('6' in l for l in lines)

def test_ex12_tableau_ops():
    inputs = '6,1,2,3,4,5,6'
    lines = run_algo(f'{BASE}/ex12_tableau_ops.algo', inputs)
    assert any('6' in l and 'max' in l for l in lines) or any('21' in l for l in lines)

def test_ex13_contient_numero_yes():
    lines = run_algo(f'{BASE}/ex13_contient_numero.algo', 'abc3def')
    assert any('contient' in l and 'chiffre' in l for l in lines)

def test_ex13_contient_numero_no():
    lines = run_algo(f'{BASE}/ex13_contient_numero.algo', 'abcdef')
    assert any('ne contient pas' in l for l in lines)

def test_ex14_leaders():
    inputs = '5,1,2,3,4,5'
    lines = run_algo(f'{BASE}/ex14_leaders.algo', inputs)
    combined = ' '.join(lines)
    assert '5' in combined

def test_ex15_fusion():
    inputs = '3,1,3,5,3,2,4,6'
    lines = run_algo(f'{BASE}/ex15_fusion.algo', inputs)
    nums = [l.strip() for l in lines if l.strip().isdigit()]
    assert nums == ['1','2','3','4','5','6']

def test_ex16_factorielle():
    lines = run_algo(f'{BASE}/ex16_factorielle.algo', '5')
    assert any('120' in l for l in lines)

def test_ex17_fibonacci():
    lines = run_algo(f'{BASE}/ex17_fibonacci.algo', '8')
    nums = [l.strip() for l in lines if l.strip().isdigit() or l.strip() == '0']
    assert '0' in nums
    assert '13' in nums
