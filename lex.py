from enum import Enum
#Actions are ACT and SAY, will add more later
class Tokens(Enum):
    BEGIN = 0
    END = 1
    IDENT = 2
    SCONST = 3
    ICONST = 4
    IF = 5
    ELSE = 6
    CHOICE = 8
    OPT = 9
    ACTOR = 12
    ACTION = 13
    FRAME = 14
    MENU = 16
    NECK = 17
    HUD = 18
    ON = 19
    OFF = 20
    LPAREN = 21
    RPAREN = 22
    COMA = 23
    SET = 24
    SEMICOLON = 25
    DOT = 26
    DIRECT = 27
    FOR = 28
    ERR = 29

ReservedTokens = {
    "begin" : Tokens.BEGIN,
    "end" : Tokens.END,
    "if" : Tokens.IF,
    "else" : Tokens.ELSE,
    "choice" : Tokens.CHOICE,
    "option" : Tokens.OPT,
    "actor" : Tokens.ACTOR,
    "action" : Tokens.ACTION,
    "frame" : Tokens.FRAME,
    "menu" : Tokens.MENU,
    "neck" : Tokens.NECK,
    "hud" : Tokens.HUD,
    "on" : Tokens.ON,
    "off" : Tokens.OFF,
    "for" : Tokens.FOR,
    "(" : Tokens.LPAREN,
    ")" : Tokens.RPAREN,
    "," : Tokens.COMA,
    "set" : Tokens.SET,
    ";" : Tokens.SEMICOLON,
    "." : Tokens.DOT,
    "!" : Tokens.DIRECT
}

class LexItem:
    def __init__(self):
        self.token = Tokens.ERR
        self.lexeme = ""
        self.line = -1

    def updateLexeme(self, c):
        self.lexeme += c

    def setToken(self, t):
        self.token = t

    def setLexeme(self, l):
        self.lexeme = l

def lex(path):
    #Lexer States

    tokens = []
    state = "BEGIN"
    file = open(path, 'r')

    done = False
    file.seek(0, 2)
    filesize = file.tell()
    file.seek(0, 0)

    cur_item = LexItem()
    l = 1

    while not done:
        if(file.tell() == filesize):
            break

        curc = file.read(1)

        while(curc.isspace()):
            if(state == "IDENT" or state == "INT"):
                cur_item.line = l
                tokens.append(cur_item)
                cur_item = LexItem()
                state = "BEGIN"

            if(curc == '\n'):
                l+=1

            curc = file.read(1)


        if(state == "BEGIN"):

            if(curc.isalpha()):
                cur_item.setToken(Tokens.IDENT)
                cur_item.updateLexeme(curc)
                state = "IDENT"
            elif(curc.isdigit()  or curc == '-'): # includes negative numbers !
                cur_item.setToken(Tokens.ICONST)
                cur_item.updateLexeme(curc)
                state = "INT"
                
            elif(curc == "\""):
                cur_item.setToken(Tokens.SCONST)
                state = "STRING"

            #comment handler
            elif(curc == "#"):
                while curc != '\n':
                    curc = file.read(1)
                
                continue

            elif(curc in ReservedTokens):
                cur_item.setToken(ReservedTokens[curc])
                cur_item.updateLexeme(curc)
                cur_item.line = l
                tokens.append(cur_item)
                cur_item = LexItem()
                continue

        elif(state == "IDENT"):
            if((cur_item.lexeme+curc) in ReservedTokens):
                cur_item.updateLexeme(curc)
                cur_item.setToken(ReservedTokens[cur_item.lexeme])
                cur_item.line = l
                tokens.append(cur_item)
                cur_item = LexItem()
                state = "BEGIN"

            elif(not curc.isalnum()): #special case for spaces for some
                file.seek(file.tell() - 1, 0)
                cur_item.line = l
                tokens.append(cur_item)
                cur_item = LexItem()
                state = "BEGIN"

            else:
                cur_item.updateLexeme(curc)

        elif(state == "INT"):
            if(not curc.isdigit()):
                file.seek(file.tell() - 1, 0)
                cur_item.line = l
                tokens.append(cur_item)
                cur_item = LexItem()
                state = "BEGIN"

            else:
                cur_item.updateLexeme(curc)

        elif(state == "STRING"):
            while curc != '"':
                if(curc == '\n'):
                    print("LexError: misplaced newline in string constant on line {0}".format(l))
                    cur_item.setToken(Tokens.ERR)
                    done = True
                    break
                else:
                    cur_item.updateLexeme(curc)

                curc = file.read(1)

            cur_item.line = l
            tokens.append(cur_item)
            cur_item = LexItem()
            state = "BEGIN"

        else:
            print("Error: Broken Lexer State!")
            break


    return tokens
