from lex import Tokens

class AstNode():
    pass

class ProgramNode(AstNode):
    def __init__(self):
        self.nodes = []

    def write(self, out, state):
        for node in self.nodes:
            node.write(out, state)
        
        out.write("<END>")

class IfNode(AstNode):
    def __init__(self, check, true, false):
        self.condition = check
        self.true_nodes = true
        self.false_nodes = false

    def write(self, out, state):
        out.write("<CHECKFLAG>({0})\"{0}on\"\"{0}off\"\n".format(self.condition.lexeme))
        out.write("<CASE>\"{0}on\"\n".format(self.condition.lexeme))
        for node in self.true_nodes:
            node.write(out, state)
        out.write("<RAMDOMJMP>\"{0}over\"\n".format(self.condition.lexeme))
        
        out.write("<CASE>\"{0}off\"\n".format(self.condition.lexeme))
        if(self.false_nodes != None):
            for node in self.false_nodes:
                node.write(out, state)
        out.write("<RAMDOMJMP>\"{0}over\"\n".format(self.condition.lexeme))

        out.write("<CASE>\"{0}over\"\n".format(self.condition.lexeme))

class ChoiceNode(AstNode):
    def __init__(self, actor, text):
        self.text = text
        self.actor = actor
        self.option_nodes = []

    def write(self, out, state):
        actor = state['actors'][self.actor.lexeme]
        ChoiceEndHash = str(hex(hash(actor['id'].lexeme + self.text.lexeme)))
        out.write("<WINDOW>({0})<COLOR>({1})<SAY><COLOR>(0){2}\n".format(actor['pos'].lexeme, actor['color'].lexeme, self.text.lexeme))
        out.write("<CHOICE>")
        for option in self.option_nodes:
            out.write("\"{0}\"({1})".format(option.opt_name.lexeme, state['csv_text'].index(option.opt_name.lexeme)))
        out.write("<LISTEND>\n")
        for option in self.option_nodes:
            option.write(out, state)
            out.write("<RAMDOMJMP>\"{}\"\n".format(ChoiceEndHash))
        
        out.write("<CASE>\"{}\"\n".format(ChoiceEndHash))

        #out.write("<CLOSEWINDOW>({0})\n".format(actor['pos'].lexeme))

class OptionNode(AstNode):
    def __init__(self, name):
        self.nodes = []
        self.opt_name = name

    def write(self, out, state):
        out.write("<CASE>\"{0}\"\n".format(self.opt_name.lexeme))

        for node in self.nodes:
            node.write(out, state)

class SetNode(AstNode):
    def __init__(self, ts, v):
        self.set = ts
        self.value = v

    def write(self, out, state):
        onoff = "ON" if self.value.token == Tokens.ON else "OFF"
        if(self.set.token == Tokens.ICONST):
            out.write("<FLAG{0}>({1})\n".format(onoff, self.set.lexeme))
        elif(self.set.token == Tokens.HUD):
            if(self.value.token == Tokens.ON):
                out.write("<NORMALSCREEN>\n")
            else:
                out.write("<FULLSCREEN>\n")
        else:
            out.write("<{0}{1}>\n".format(self.set.lexeme.upper(), onoff))

class FrameNode(AstNode):
    def __init__(self, nodes):
        self.nodes = nodes

    def write(self, out, state):
        out.write("<FRAMESTART>\n")

        for node in self.nodes:
            node.write(out, state)

        out.write("<FRAMEEND>\n")

class ActorNode(AstNode):
    def __init__(self, cientry, aid, position, color):
        self.id = aid
        self.textbox_color = color
        self.textbox_pos = position
        self.character_info_entry = cientry

    def write(self, out, state):
        pass #Never gets processed beyond this converter

class ActNode(AstNode):
    def __init__(self, actor, action, action_value):
        self.actor = actor
        self.action = action
        self.action_value = action_value

    def write(self, out, state):
        actor = state['actors'][self.actor.lexeme]

        if(self.action_value.token == Tokens.SEMICOLON):
            out.write("<ACTOR>\"{0}\"<{1}>\n".format(actor['model'].lexeme, self.action.lexeme.upper()))
        elif(self.action.lexeme == 'say'):
            out.write("<WINDOW>({0})<COLOR>({1})<SAY><COLOR>(0){2}\n<ANYKEY>\n<CLOSEWINDOW>({0})\n".format(actor['pos'].lexeme, actor['color'].lexeme, self.action_value.lexeme))
        elif(self.action.lexeme == 'speak'):
            out.write("<WINDOW>({0})<COLOR>({1})<SPEAK>({2})\n<ANYKEY>\n<CLOSEWINDOW>({0})\n".format(actor['pos'].lexeme,actor['color'].lexeme, state['csv_text'].index(self.action_value.lexeme)))
        elif(self.action.lexeme == 'target'):
            out.write("<CAMTARGET>\"{0}\"({1})\n".format(actor['model'].lexeme, self.action_value.lexeme))
        else:
            out.write("<ACTOR>\"{0}\"<{1}>\"{2}\"\n".format(actor['model'].lexeme, self.action.lexeme.upper(), self.action_value.lexeme))

class GenericNode(AstNode):
    def __init__(self, lexitem):
        self.lexitem = lexitem

    def write(self, out, state):
        out.write("<{}>\n".format(self.lexitem.lexeme.upper()))

class DirectNode(AstNode):
    def __init__(self, lexitem, args):
        self.lexitem = lexitem
        self.args = args

    def write(self, out, state):
        out.write("<{}>".format(self.lexitem.lexeme.upper()))
        for arg in self.args:
            if(arg.token == Tokens.ICONST):
                out.write("({})".format(arg.lexeme))
            elif(arg.token == Tokens.SCONST):
                out.write("\"{}\"".format(arg.lexeme))
                
        out.write("\n")