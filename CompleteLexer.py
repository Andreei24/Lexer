

class Concat:
    def __init__(self,first,second):
        self.first = first
        self.second = second
    
    def toString(self):
        print("Concat")

class Union:
    def __init__(self,first,second):
        self.first = first
        self.second = second
    
    def toString(self):
        print("Union")

class Star:
    def __init__(self,first):
        self.first = first
    
    def toString(self):
        print("Star")

class Plus:
    def __init__(self,first):
        self.first = Concat(first,Star(first))

    def toString(self):
        print("plus")

class Atom:
    def __init__(self,char):
        self.char = char

    def toString(self):
        print(self.char)

class Bracket:
    def __init__(self,first):
        self.first = first
    
    def toString(self):
        print("Bracket")

class OpenBracket:
    
    def toString(self):
        print("OpenBracket")

class nfa:

    def __init__(self):
        self.alphabet = set()
        self.states = set()
        self.q0 = None
        self.qf = []
        self.delta = dict()
        self.token = ""
        self.state = ""

    def add_transition(self,from_state,to_state,symbol):
        if isinstance(symbol,str):
            symbol = set([symbol])
        
        self.states.add(from_state)
        self.states.add(to_state)

        if from_state in self.delta:
            if to_state in self.delta[from_state]:
                self.delta[from_state][to_state] = self.delta[from_state][to_state].union(symbol)
            else:
                self.delta[from_state][to_state] = symbol
        else:
            self.delta[from_state] = {to_state:symbol}

    def merge_transitions(self,transitions,offset = 0):
        for from_state,to_state in transitions.items():
            for state in to_state:
                self.add_transition(from_state + offset, state + offset, to_state[state])

    def set_q0(self,state):
        self.q0 = state
        self.states.add(state)
    
    def add_qf(self,state):
        if state not in self.qf:
            self.qf.append(state)
        self.states.add(state)
    
    def set_qf(self,state):
        self.qf.clear()
        
        if isinstance(state,int):
            if state not in self.qf:
                self.qf.append(state)
            
            self.states.add(state)
        else:
            self.qf = state

    def last_state(self):
        return len(self.states) - 1

    def get_epsilon_closure(self,state,visited,epsilon_states):
        
        if state in visited:
            return []
        
        visited.append(state)

        if state in self.delta:
            to_state = self.delta[state]
        
            for aux in to_state:
                if nfa.epsilon() in to_state[aux]:
                    self.get_epsilon_closure(aux,visited, epsilon_states)

        epsilon_states.add(state)
   
    @staticmethod    
    def epsilon():
        return ":e:"

    def add_sink_transitions(self):
        sink_state = self.last_state() + 1
        self.states.add(sink_state)
        for from_state in self.delta:
            found = set()
            for to_state in self.delta[from_state]:
                found = set.union(found,self.delta[from_state][to_state])
            
            for char in self.alphabet:
                if char not in found:
                    self.add_transition(from_state,sink_state,char)
        
        for state in self.states:
            if state not in self.delta:
                for char in self.alphabet:
                    self.add_transition(state,sink_state,char)

#function to turn the stack of Structures in Prenex form
def print_reg(reg,print_stack):
    if isinstance(reg,Concat):
        print_stack.append("CONCAT ")
        print_reg(reg.first,print_stack)
        print_reg(reg.second,print_stack)

        
    elif isinstance(reg,Star):
        print_stack.append("STAR ")
        print_reg(reg.first,print_stack)

        
    elif isinstance(reg,Union):
        print_stack.append("UNION ")
        print_reg(reg.first,print_stack)
        print_reg(reg.second,print_stack)

        
    elif isinstance(reg,Atom):
        if reg.char == ' ':
            print_stack.append("\'"+reg.char +"\' ")
        else:
            print_stack.append(reg.char +" ")

    # elif isinstance(reg,OpenBracket):
    #     print_reg(reg.second,print_stack)
    
    elif isinstance(reg,Plus):
        print_stack.append("PLUS ")
        print_reg(reg.first,print_stack)

    elif isinstance(reg,Bracket):
        print_reg(reg.first,print_stack)

#function to turn the regex in prenex form
def regex_to_prenex(regex):
    stack = []
    print_stack = []
    prev = ""
    
    #reach each char form regex until the end of string
    while regex != "":
        char = regex[0]
        regex = regex[1:]

        
        #check for special symbols and build the char that needs to be checked accordingly
        if char =='\'':
            
            if regex[0] == '\\':
                char = '\\n'
                regex = regex[3:]
            else:
                char = regex[0]
                regex = regex[2:]

        #when an open bracket is found and the last char is one with a single argument (eg: Star, Atom..)
        #it means that there is a concatenation of whatever the previous regex is and what is to be read from now
        #so the last element of the stack is popped and replaced with a Concat structure with said element as it's first argument
        #and a open bracket is added on the stack afterwards
        if char == "(":
            if isinstance(prev,Bracket) | isinstance(prev,Atom) | isinstance(prev,Star) | isinstance(prev,Plus):
                op1 = stack.pop()
                aux = Concat(op1,None)
                stack.append(aux)
                op2 = OpenBracket()
                stack.append(op2)
            #if not, then just an open bracked is added on the stack
            else:
                op1 = OpenBracket()
                stack.append(op1)
        
        elif char == "*":
            elem = stack.pop()
            op1 = Star(elem)
            stack.append(op1)
        
        elif char == "+":
            elem = stack.pop()
            op1 = Plus(elem)
            stack.append(op1)
        
        elif char == "|":
            elem = stack.pop()
            op1 = Union(elem,None)
            stack.append(op1)
       
        elif char == "+":
            elem = stack.pop()
            op1 = Plus(elem)
            stack.append(op1)

        #when a closing bracket is found, a reduction is applied, meaning that we merge
        #every 2 structures on the stack until the open bracket is found
        #the merged structure will be added as an argument to the Bracket structure
        elif char == ")":
            
            op1 = stack.pop()
            op2 = stack.pop()
            
            found = 0
            
            while found == 0:
                if not isinstance(op2,OpenBracket):
                    op2.second = op1
                    stack.append(op2)
                else:
                    aux = Bracket(op1)
                    stack.append(aux)
                    found = 1
                    break
                
                op1 = stack.pop()
                op2 = stack.pop()

        #same as with open bracket, if the previous element of the regex is a single argument structure,
        #the current Atom is replaced with a Concat of Atom and what will follow
        elif isinstance(prev,Atom) | isinstance(prev,Bracket) | isinstance(prev,Star) | isinstance(prev,Plus):        
            elem = stack.pop()
            op1 = Concat(elem,None)
            stack.append(op1)
            op2 = Atom(char)
            stack.append(op2)
        else:
            op1 = Atom(char)
            stack.append(op1)

        prev = stack[-1]


    #reduce the stack after the regex is finised reading to 1 element, the root of the structure tree
    while(len(stack) > 1):
        op1 = stack.pop()
        op2 = stack.pop()
        
        op2.second = op1
        stack.append(op2)
        
    #turn the structure tree into a stack of prenex forms
    print_reg(stack[0],print_stack)

    prenex = ""

    #build the final prenex string from the stack returned earlier
    for elem in print_stack:
        prenex += elem

    return prenex

def read(input_string):
    elem = input_string.pop(0)

    if elem == "UNION":
        op1 = read(input_string)
        op2 = read(input_string)

        aux = Union(op1,op2)
        return aux
    else:
        if elem == "CONCAT":
            op1 = read(input_string)
            op2 = read(input_string)

            aux = Concat(op1,op2)
            return aux
        else:
            if elem == "STAR":
                op = read(input_string)
                
                aux = Star(op)
                
                return aux
            else:
                if elem == "PLUS":
                    op = read(input_string)

                    aux = Plus(op)

                    return aux
                else:
                    aux = Atom(elem)
                    return aux

def build_NFA(base):
    if isinstance(base,Atom):
        aux = nfa()
        aux.alphabet.add(base.char)
        aux.add_transition(0,1,base.char)
        aux.q0 = 0
        aux.qf.append(1)
        return aux
    else:
        if isinstance(base,Star):
            aux = build_NFA(base.first)
            final_nfa = nfa()
            final_nfa.alphabet = final_nfa.alphabet.union(aux.alphabet)
           
            final_nfa.add_transition(0,1,nfa.epsilon())
            final_nfa.merge_transitions(aux.delta,1)
            
            final_nfa.add_transition(final_nfa.last_state(), 1, nfa.epsilon())
            final_nfa.add_transition(final_nfa.last_state(),final_nfa.last_state() + 1,nfa.epsilon())
            final_nfa.add_transition(0,final_nfa.last_state(),nfa.epsilon())
            
            final_nfa.set_q0(0)
            final_nfa.set_qf(final_nfa.last_state())
            return final_nfa
        else:
            if isinstance(base,Union):
                op1 = build_NFA(base.first)
                op2 = build_NFA(base.second)

                final_nfa = nfa()

                final_nfa.alphabet = final_nfa.alphabet.union(op1.alphabet)
                final_nfa.alphabet = final_nfa.alphabet.union(op2.alphabet)

                final_nfa.add_transition(0,1,nfa.epsilon())
                final_nfa.merge_transitions(op1.delta,1)

               
                final_nfa.merge_transitions(op2.delta,len(final_nfa.states))
                final_nfa.add_transition(0,final_nfa.last_state() - op2.last_state(),final_nfa.epsilon())

                
                final_nfa.add_transition(op1.last_state() + 1, final_nfa.last_state() + 1,final_nfa.epsilon())
                final_nfa.add_transition(final_nfa.last_state() - 1, final_nfa.last_state(),final_nfa.epsilon())
                
                final_nfa.set_q0(0)
                final_nfa.set_qf(final_nfa.last_state())
                return final_nfa
            else:
                if isinstance(base,Concat):
                    op1 = build_NFA(base.first)
                    op2 = build_NFA(base.second)

                    final_nfa = nfa()

                    final_nfa.alphabet = final_nfa.alphabet.union(op1.alphabet)
                    final_nfa.alphabet = final_nfa.alphabet.union(op2.alphabet)

                    final_nfa.merge_transitions(op1.delta)
                    final_nfa.merge_transitions(op2.delta,len(op1.states))

                    final_nfa.add_transition(op1.last_state(),op2.q0 + len(op1.states),nfa.epsilon())

                    final_nfa.set_q0(op1.q0)
                    final_nfa.set_qf(final_nfa.last_state())
                    
                    return final_nfa
                else:
                    if isinstance(base,Plus):
                        final_nfa = build_NFA(base.first)
                        
                        return final_nfa

def NFA_to_DFA(old_nfa):
    dfa = nfa()
    dfa.alphabet = old_nfa.alphabet
    dfa.set_q0(0)

    queue = []
    visited = []
    epsilon_closure = set()

    old_nfa.get_epsilon_closure(0,visited,epsilon_closure)

    new_states = {0:epsilon_closure}
    queue.append(0)

    while(queue != []):
        
        current_state = queue.pop()
        
        for char in old_nfa.alphabet:
            visited = []
            epsilon_closure = set()
            
            if current_state in  new_states:
                for from_state in new_states[current_state]:
                    if from_state in old_nfa.delta:
                        for to_state in old_nfa.delta[from_state]:
                            if char in old_nfa.delta[from_state][to_state]:
                                epsilon_closure.add(to_state)

                                old_nfa.get_epsilon_closure(to_state,visited,epsilon_closure)
                              
            
            if len(epsilon_closure) != 0:
                if (epsilon_closure not in new_states.values()):
                    count = len(new_states)
                    new_states[count] = epsilon_closure
                    dfa.add_transition(current_state,count,char)
                    queue.append(count)
                else:
                    for aux in new_states:
                        if new_states[aux] == epsilon_closure:
                            dfa.add_transition(current_state,aux,char)
        
    for state in new_states:
        for final_state in old_nfa.qf:
            if final_state in new_states[state]:
                dfa.add_qf(state)       
    
    
    dfa.add_sink_transitions()
    return dfa

def build_DFAs(file,DFAs):
    for line in file:
        
        #build a dfa for each line from the input file
        input = line
        input = input.strip("\n")
        input = input.split(" ",1)
        regex = input[1][:-1]
        token = input[0]

        prenex = regex_to_prenex(regex)
        prenex = prenex.split()

        iter = 0
        while iter != len(prenex):
            if prenex[iter] == "'":
                prenex[iter] =" "
                del prenex[iter+1]
            
            iter += 1

        a = read(prenex)
        b = build_NFA(a)
        c = NFA_to_DFA(b)

        c.token = token
        DFAs.append(c)

def run_dfa(dfa,input,extra):
    config = (dfa.q0,input)
    dfa.state = "SEEKING"
    length = 0
    lastAccepted = 0
    newline = 0

    while dfa.state != "REJECt":
        newline = 0
        found = 0

        if config[1] != '':
            if len(config[1]) >= 2:
                if (config[1][0] =="\\") & (config[1][1] == "n"):
                    aux = (config[0],"\\n")
                    newline = 1
                else:
                    aux = (config[0],config[1][0])
            else:
                aux = (config[0],config[1][0])
        else:
            extra = length
            return lastAccepted,extra
        
        if aux[0] in dfa.delta:
            for state in dfa.delta[aux[0]]:
                if aux[1] in dfa.delta[aux[0]][state]:
                    if newline == 0:
                        config = (state,config[1][1:])
                        found = 1
                    else:
                        config =(state,config[1][2:])
                        length +=1
                        found = 1
            
            if found == 0:
                extra = length
                return lastAccepted,extra
        
            if config[0] != dfa.last_state():
                length +=1

                if config[0] in dfa.qf:
                    lastAccepted = length
            else:
                extra = length
                return lastAccepted,extra
        else:
            dfa.state ="REJECT"
            extra = length
            return lastAccepted,extra   

def runcompletelexer(lex_file,in_file,out_file):
    f = open(lex_file,'r')

    DFAs = []

    build_DFAs(f,DFAs)
    f.close()

    f = open(in_file,"r")
    input_string = str(f.read())
    string_len = len(input_string)
    #replace the \n with \\n for easier parsing of the string in tokens
    input_string = input_string.replace("\n","\\n")

    f.close()

    f = open(out_file,"a")
    output =""
    error_found = 0
    len_input = 0
    extra = 0

    while input_string:
        match_dfa_token = ""
        max_len = 0
        max_extra = 0
        

        for dfa in DFAs:
            (length,extra) = run_dfa(dfa,input_string,extra)
            if(length > max_len):
                    max_len = length
                    match_dfa_token = dfa.token
            if extra > max_extra:
                max_extra = extra

        if max_len != 0:
            len_input += max_len
            output += match_dfa_token + ' ' + input_string[:max_len] +'\n'
            input_string = input_string[max_len:]
        else:
            if (len_input + max_extra) != string_len:
                error_string = "No viable alternative at character " + str(len_input + max_extra) +", line 0\n"
                f.write(error_string)
            else:
                error_string = "No viable alternative at character EOF" + ", line 0\n"
                f.write(error_string)
            error_found = 1
            break

    if not error_found:
        f.write(output)

    f.close
