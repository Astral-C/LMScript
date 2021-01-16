from lex import Tokens
from ast import *

def parse(tokens):
    
    state = {
        'curtoken' : 0,
        'actors' : {},
        'local_vars' : {}, #Bad? Due to possible adding extremely simple pass-by-value 'functions' would need to have real scoping not, well not this.
        'in_for': False,
        'csv_text' : ['Next']
    }

    root = Program(tokens, state)

    if(root == None):
        print("Parsing Failed, root {}".format(root))

    return [root, state]
    

def Program(tokens, state):
    n = ProgramNode()
    if(tokens[state['curtoken']].token != Tokens.BEGIN):
        print("First Token Was Not Begin, it was {}".format(tokens[state['curtoken']].token))
        return None

    state['curtoken'] += 1

    s = Statements(tokens, state)
    if(s != None):
        n.nodes.extend(s)
    else:
        print("No statements in program")
        return None

    if(tokens[-1].token != Tokens.END):
        print("Last Token Was Not End")
        return None

    return n
   
def Statements(tokens, state):
    statements = []
    s = Statement(tokens, state)
    if(s != None):
        statements.append(s)
    else:
        return None

    if(tokens[state['curtoken']].token != Tokens.END and tokens[state['curtoken']].token != Tokens.ELSE):
        s = Statements(tokens, state)
        if(s != None):
            statements.extend(s)
        else:
            return None

    return statements

def Statement(tokens, state):
    item = tokens[state['curtoken']]
    state['curtoken'] += 1
    if(item.token == Tokens.IF):
        return IfStatement(tokens, state)
    elif(item.token == Tokens.SET):
        return SetStatement(tokens, state)
    elif(item.token == Tokens.CHOICE):
        return ChoiceStmt(tokens, state)
    elif(item.token == Tokens.ACTOR):
        return NewActStmt(tokens, state)
    #the only identifiers/scripting that actually happens because of actors being defineable
    elif(item.token == Tokens.IDENT): 
        return ActStmt(tokens, state)
    elif(item.token == Tokens.FRAME):
        return FrameStmt(tokens, state)
    elif(item.token == Tokens.FOR):
        return ForStatement(tokens, state)

    #No such thing as an invalid statement, this allows for direct translation tokens for event <=> lms
    elif(item.token == Tokens.DIRECT):
        return DirectStmt(tokens, state)

    else:
        return GenericNode(item)

def SetStatement(tokens, state):
    toset = tokens[state['curtoken']]
    value = tokens[state['curtoken'] + 1]

    if(toset.token != Tokens.MENU and toset.token != Tokens.HUD and toset.token != Tokens.NECK and toset.token != Tokens.ICONST and toset.lexeme not in state['local_vars']):
        print("Invalid Set Statement: {} not settable".format(toset.lexeme))
        return None
    if(value.token != Tokens.ON and value.token != Tokens.OFF):
        print("Invalid Value in Set Statement: {}".format(value.lexeme))
        return None
    
    state['curtoken'] += 2
    return SetNode(toset, value)

def IfStatement(tokens, state):
    condition = tokens[state['curtoken']]
    if(condition.token != Tokens.ICONST and condition.lexeme not in state['local_vars']):
        print("Invalid Condition {} for if statement".format(condition.token))
        return None
    
    state['curtoken'] += 1
    true = Statements(tokens, state)

    false = None
    t = tokens[state['curtoken']]
    
    if(t.token == Tokens.ELSE):
        state['curtoken'] += 1
        false = Statements(tokens, state)
        
        t = tokens[state['curtoken']]
        state['curtoken'] += 1
        if(t.token != Tokens.END):
            print("Missing end after if statement")
            return None
        
    elif(t.token == Tokens.END):
        state['curtoken'] += 1

    else:
        print("Missing else or end after if statement")
        return None


    return IfNode(condition, true, false)

def ChoiceStmt(tokens, state):
    actor_talk = tokens[state['curtoken']]
    choice_text = tokens[state['curtoken'] + 1]
    n = ChoiceNode(actor_talk, choice_text)

    state['curtoken'] += 2
    while(tokens[state['curtoken']].token == Tokens.OPT):
        state['curtoken'] += 1
        o = Options(tokens, state)
        if(o == None):
            print("Invalid Options in Choice Statement")

        else:
            n.option_nodes.append(o)

    if(len(n.option_nodes) == 0):
        print("No Options in Choice Statement")
        return None    

    return n

def Options(tokens, state):
    option_text = tokens[state['curtoken']]
    o = OptionNode(option_text)
    state['csv_text'].append(option_text.lexeme)
    state['curtoken'] += 1
    
    s = Statements(tokens, state)
    if(s == None):
        print("No Statements in Option")
        return None
    else:
        o.nodes.extend(s)
    
    state['curtoken'] += 1 #consume's statement list's end token

    return o

def FrameStmt(tokens, state):
    f = FrameNode(Statements(tokens, state))
    state['curtoken'] += 1
    return f

#actor "demo_luigi" luigi [0, 3];
def NewActStmt(tokens, state):
    entry = tokens[state['curtoken']]
    name = tokens[state['curtoken'] + 1]
    pos = tokens[state['curtoken'] + 3]
    color = tokens[state['curtoken'] + 5]
    
    
    if(tokens[state['curtoken'] + 2].token != Tokens.LPAREN):
        print("Missing Left PAREN in actor definition on line {}".format(entry.line))
        return None
    elif(tokens[state['curtoken'] + 6].token != Tokens.RPAREN):
        print("Missing Right PAREN in actor definition on line {}".format(entry.line))
        return None

    if(entry.token != Tokens.SCONST):
        print("Actor characterinfo entry must be string on line {}".format(entry.line))
        return None

    if(name.token != Tokens.IDENT):
        print("Actor definition missing id on line {}".format(name.line))
        return None

    if(pos.token != Tokens.ICONST):
        print("Textbox position must be integer on line {}".format(pos.line))
        return None

    if(color.token != Tokens.ICONST):
        print("Textbox color must be integer on line {}".format(color.line))
        return None
    
    if(name.lexeme in state['actors']):
        print("Can't redefine actor on line {}".format(entry.line))
        return None

    state['curtoken'] += 7
    state['actors'][name.lexeme] = {'id':name, 'model':entry, 'pos':pos, 'color':color}
    return ActorNode(entry, name, pos, color)

def ActStmt(tokens, state):
    actor = tokens[state['curtoken'] - 1]
    action = tokens[state['curtoken'] + 1]
    action_value = tokens[state['curtoken'] + 2]

    if(actor.lexeme not in state['actors']):
        print("Undefined Actor {} on line {}".format(actor.lexeme, actor.line))
        return None

    if(tokens[state['curtoken']].token != Tokens.DOT):
        print("Missing Dot Token in Action Statement on line {}".format(actor.line))
        return None

    if(action_value.token != Tokens.SEMICOLON and action_value.token != Tokens.SCONST):
        print("Invalid Action Command {} on line {}".format(action_value.lexeme, action_value.line))
        return None

    if(action.lexeme == 'speak' and not action_value.lexeme in state['csv_text']):
        state['csv_text'].append(action_value.lexeme)

    state['curtoken'] += 3
    return ActNode(actor, action, action_value)

def DirectStmt(tokens, state):
    args = []
    cmd = tokens[state['curtoken']]
    state['curtoken'] += 1
    
    if(tokens[state['curtoken']].token != Tokens.LPAREN):
        print("Missing argument list in direct")
        return None

    state['curtoken'] += 1
    
    while(tokens[state['curtoken'] + 1].token == Tokens.COMA):
        args.append(tokens[state['curtoken']])
        state['curtoken'] += 2

    if(tokens[state['curtoken']].token == Tokens.ICONST or tokens[state['curtoken']].token == Tokens.SCONST or tokens[state['curtoken']].token == Tokens.IDENT):
        args.append(tokens[state['curtoken']])
        state['curtoken'] += 1
    else:
        print("Invalid argument type for direct {}".format(tokens[state['curtoken']].lexeme))
        return None

    if(tokens[state['curtoken']].token != Tokens.RPAREN):
        print("Expected right paren after args, got {}".format(tokens[state['curtoken']].lexeme))
        return None
    
    state['curtoken'] += 1
    return DirectNode(cmd, args)
    
#Very hacked together but works for these purposes
def ForStatement(tokens, state):
    sentinal = tokens[state['curtoken']]
    
    if(sentinal.token != Tokens.IDENT):
        print("No sentinal value in for loop")
        return None


    if(tokens[state['curtoken']].lexeme in state['actors'] or tokens[state['curtoken']].lexeme in state['local_vars']): #not allowing actors and sentinals to use same name for obvious reasons
        print(f"Sentinal variable '{tokens[state['curtoken']].lexeme}' already defined")
        return None


    state['curtoken'] += 1
    if(tokens[state['curtoken']].token != Tokens.COMA): 
        print("Missing comma in For loop")
        return None
    
    state['curtoken'] += 1
    if(tokens[state['curtoken']].token != Tokens.ICONST and tokens[state['curtoken'] + 1].token != Tokens.COMA and tokens[state['curtoken'] + 2].token != Tokens.ICONST):
        print(f"Incorrect format in for loop range {tokens[state['curtoken']].token} {tokens[state['curtoken'] + 1].token} {tokens[state['curtoken'] + 2].token}")
        return None


    start = int(tokens[state['curtoken']].lexeme)
    end = int(tokens[state['curtoken'] + 2].lexeme)
    state['local_vars'][sentinal.lexeme] = start #very bad, no error handling
    state['curtoken'] += 3


    loop_nodes = Statements(tokens, state)
    
    return ForNode(loop_nodes, sentinal, start, end, True)