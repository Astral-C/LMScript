import sys
from lex import lex
from parse import parse
from ast import *


tokenList = lex(sys.argv[1])
parser_out = parse(tokenList)
event_ast = parser_out[0]
state =  parser_out[1]

event = None
csv = None
if(len(sys.argv) == 3):
    event = open(sys.argv[2], 'w')
    csv = open(sys.argv[2].replace('txt','csv'), 'w')

else:
    event = open(sys.argv[1].replace('lms','txt'), 'w')
    csv = open(sys.argv[1].replace('lms','csv'), 'w')

event_ast.write(event, state)
for l in state['csv_text']:
    csv.write(l+'\n')