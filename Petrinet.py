'''
Installation of Graphviz and its Python interface module is needed for graphical visualization.
see https://www.graphviz.org/download/ for installation instructions.
Interface module is available at:
'pip3 install graphviz' in Win OS.
'brew install graphviz' in Mac OS.
'''


'''
Overall structure of the source code:
The two main classes are:
    1. Class Petrinet
    2. Class TranSys
The behaviors of Petri nets revolves around smaller classes:
    1. Class Place
    2. Class Transition
    3. Class Arc
The TranSys class is instantiated with a Petrinet object to adapt to the requirement 
of the Assignment.
'''

import graphviz
from copy import deepcopy
from IPython import display
from PIL import Image
from random import randint
import time
#===============================================================================

class Arc:
    """An arc of the Petri net"""

    def __init__(self, name):
        """ Initialization through Petri net.
            >>> net = Petrinet()
            >>> a = net.arc("a")
        """
        self.name = name
        self.frm = None
        self.to = None
        self.status = None

    def initialize(self, frm, to, status):
        self.frm = frm
        self.to = to
        self.status = status

    def __str__(self):
        return self.name
   
#===============================================================================

class Transition:
    """A transition of the Petri net"""

    def __init__(self,name):
        """ Initialization through Petri net.
            >>> net = Petrinet()
            >>> t = net.transition("t")
        """
        self.name = name
        self.incoming_arcs = []
        self.outgoing_arcs =[]

    def can_fire(self,state,placeindex):
        """Check if Petri net can fire with the current marking
            @param state: current marking
            @param placeindex: index of places in the Petri net
        """

        for arc in self.outgoing_arcs:
            if state[placeindex[arc.to]] == arc.to.bound:
                return False
        for arc in self.incoming_arcs:
            if state[placeindex[arc.frm]] == 0:
                return False
        return True

    def fire(self,marking,placeindex):
        """Fire the transition with the current marking
            @param marking: current marking
            @param placeindex: index of places in the Petri net
        """
        tmp = []
        for x in marking:
            tmp.append(x)
        for arc in self.incoming_arcs:
            tmp[placeindex[arc.frm]]-=1
        for arc in self.outgoing_arcs:
            tmp[placeindex[arc.to]]+=1
        return tmp

    def add_arc(self,arc):
        """Add an arc to the transition
            @param arc: an arc of the Petri net
        """
        if arc.status == "input":
            self.incoming_arcs.append(arc)
        else:
            self.outgoing_arcs.append(arc)

    def describe(self):
        """Print the description of the transition
            Made for debugging purposes
        """
        print("Transition ",self.name)
        print("Preset = { ")
        for arc in self.incoming_arcs:
            print(arc.frm, ", ", end="")
        print("}\nPostset = { ")
        for arc in self.outgoing_arcs:
            print(arc.to, ", ", end="")
        print("}\n")

    def __str__(self):
        return self.name

#===============================================================================  
    
class Place:
    """A place of the Petri net"""

    def __init__(self,name, start = 0, bound = 1):
        """ Initialization through Petri net.
            >>> net = Petrinet()
            >>> p = net.place("p")
        """
        self.name = name
        self.tokens = start
        self.bound = bound

    def get_tokens(self):
        return self.tokens

    def __str__(self):
        return self.name

#===============================================================================

def printListWithDelimiter(lst, delimiter):
    """Static function for printing a list"""
    print("{", end="")
    for x in lst:
        print(x, end=delimiter)
    print("}\n")


class Petrinet:
    """A Petri net.
        >>> net = Petrinet()
    """
    def __init__(self, bound = 1, name = ""):
        """A Petri net will initially have empty sets and a given token bound"""
        self.places = []
        self.transitions = []
        self.arcs = []
        self.init_marking= []
        self.graph_RG = graphviz.Digraph("reachability_GR"+name)
        self.graph_PN = graphviz.Digraph(name)
        self.bound = bound

    def modify(self, places, transitions, arcs, marking = [], bound = 1):
        """A function that modify the entire Petri net makeup.
           Only used in the merging of Petri nets.
    
        """
        self.places = places
        self.transitions = transitions
        self.arcs = arcs
        self.init_marking = marking
        self.bound = bound

    # function for adding places
    def place(self,placename):
        """Adding a Place object to Petri net
           >>> net = Petrinet()
           >>> p = net.place("p")
        """
        self.graph_PN.node(placename)
        plc = Place(placename, 0, self.bound)
        if plc in self.places:
            raise "repeat error"
        self.places.append(plc)
        self.init_marking.append(plc.get_tokens())
        return plc

    def arc(self, place1, place2, io):
        """Adding an Arc object to Petri net
            >>> net = Petrinet()
            >>> a = net.arc("a", "b", "input")
        """
        arc = Arc("(" + str(place1.name) + ", " + str(place2.name) + ")")
        arc.initialize(place1, place2, io)
        if (io == "input") :
            place2.add_arc(arc)
        else :
            place1.add_arc(arc)
        self.arcs.append(arc)

    def transition(self, transition_name):
        """Adding a Transition object
            >>> net = Petrinet()
            >>> t = net.transition("t")      
        """
        self.graph_PN.node(transition_name,shape = "box")
        t = Transition(transition_name)
        self.transitions.append(t)
        return t

    def get_place_index_mapping(self):
        """Create an index map for each Place"""
        m = {}
        cur=0
        for place in self.places:
            if m.get(place) == None:
                m[place] = cur
                cur+=1
        return m

    def simulate_fire_player(self):
        """Simulate the firing of the Petri net"""
        self.placeindex = self.get_place_index_mapping()
        while self.select_fire():
            pass

    def simulate_fire(self):
        """Fire the Petri net given the steps
            Should prompt the user for the steps
            Also detects terminal states
        """
        while True:
            i = input("Enter firing steps >0: ")
            try: 
                i = int(i)
            except:
                print("Invalid input")
                continue
            if i < 0:
                print("End of simulation")
                continue
            break
        self.placeindex = self.get_place_index_mapping()
        while i:
            i -= 1
            enabled = self.detect_enabled()
            b= len(enabled)
            if b == 0:
                print("Reached Terminal State")
                break
            a = randint(0,b-1)
            v = enabled[a].fire(self.init_marking,self.placeindex)
            print(str(self.init_marking)+"---"+enabled[a].name+"--->"+str(v))
            print("------------------------------------------------")
            self.setInit_marking(v)
            time.sleep(3)

    def select_fire(self):
        """Selects the transition to fire
            Prompts the user for the transition selection
            Returns True if a transition is selected
            Returns False if no transition is selected
        """
        enabled = self.detect_enabled()
        if len(enabled) == 0:
            print("Reached Terminal State")
            return False
        st = "Select transition number in prompt after: \n"
        i = 0
        for ts in enabled:
            st+= str(i)+":  "+ts.name+ "\n"
            i += 1
        st += "-1:  Exit\n"
        b = input(st)
        try:
           a = int(b)
        except:
            print("Invalid input")
            return True
        queue = self.init_marking
        if a == -1:
            return False
        else:
            if abs(a) >= len(enabled):
                print("false select(0<select<"+ str(len(enabled)))
                return True 
            else:
                v = enabled[a].fire(queue,self.placeindex)
        print(str(queue)+"---"+enabled[a].name+"--->"+str(v))
        self.setInit_marking(v)
        return True

    def find_initial_state(self):
        """Return initial marking"""
        self.placeindex = self.get_place_index_mapping()
        return self.init_marking

    def reachability_graph_generate(self, mode = "text", engine = 'dot'):
        """Build a reachability graph and pass it onto graphviz for rendering.
           See http://www.graphviz.org/ for more information.
           @param mode: 'text' or 'graph'.
           @param engine: the graphviz engine to use: 'dot' by default.
        """
        queue = []
        seen = []
        graph_edges = []
        queue.append(self.find_initial_state())
        while len(queue) != 0:
            u = queue.pop(0)
            if u in seen:
                continue
            else:
                seen.append(u)
            self.graph_RG.node(str(u))
            for transition in self.transitions:
                if transition.can_fire(u, self.placeindex):
                    v = transition.fire(u, self.placeindex)
                    graph_edges.append([u, v, transition])
                    if v not in seen:
                        queue.append(v)
        self.print_graph(graph_edges, mode, engine)

    def print_definition(self):
        """Prints the Petri net definition
        """
        print("Definition of the given Petri net: ")
        print("P = ", end = "")
        printListWithDelimiter(self.places,", ")
        print("T = ", end = "")
        printListWithDelimiter(self.transitions,", ")
        print("F = ", end = "")
        printListWithDelimiter(self.arcs,", ")
        try:
            self.print_init_marking()
        except:
            for p in self.places:
                print("0." + str(p.name) + ", ", end = "")
            print("}\n")
        
     
    def print_graph(self, graph_edges, mode ,engine = 'dot'):
        """Prints the Petri net graph via graphviz or text.
            @param graph_edges: the list of edges to be printed
            @param mode: 'text' or 'graph'.
            @param engine: the graphviz engine to use: 'dot' by default.
        """
        if mode == "graph":
            for edge in graph_edges:
                self.graph_RG.edge(str(edge[0]),str(edge[1]),str(edge[2].name))
            self.graph_RG.engine = engine
            display.display(self.graph_RG) 
        else:
            str_graph = ""
            for edge in graph_edges:
                str_graph += str("\n"+str(edge[0])+"---"+str(edge[2].name)+"--->"+str(edge[1]))
            print(str_graph)

    def setInit_marking(self,marking):
        """Set the initial marking of the Petri net"""
        self.init_marking = marking
        l = len(self.places)
        for i in range(0,l):
            self.places[i].token = marking[i]

    def print_init_marking(self):
        """Prints the initial marking of the Petri net"""
        print("Initial Marking = {", end= "")
        place_idx = self.get_place_index_mapping()
        mrk = self.init_marking
        for p in place_idx:
            print(str(mrk[place_idx[p]])+"."+p.name+", ", end="")
        print("}\n")

    def print_current_marking(self):
        """Prints the current marking of the Petri net"""
        place_idx = self.get_place_index_mapping()
        mrk = self.init_marking
        print("(", end="")
        for p in place_idx:
            print(str(mrk[place_idx[p]]) + "." + p.name + ", ", end="")
        print(")", end="")
    
    def draw(self,engine = "dot",fileformat= "png"):
        ''' draws the petri net by adding edges to the graph and then rendering it
        '''
        self.graph_PN.attr('node', shape='circle')
        for place in self.places:
            self.graph_PN.node(place.name)
        self.graph_PN.attr('node', shape='box')
        for transition in self.transitions:
            self.graph_PN.node(transition.name)
        for arc in self.arcs:
            self.graph_PN.edge(arc.frm.name,arc.to.name)
        self.graph_PN.format = fileformat
        self.graph_PN.engine = engine
        display.display(self.graph_PN)
        
    def set_init_from_string(self, marking):
        ''' set initial marking from string
            ex: [1.place1,2.place2,3.place3]
        '''
        marking = marking[1:-1]
        marking = marking.split(",")
        self.init_marking = [0]*len(self.places)
        place_idx = self.get_place_index_mapping()
        for i in marking:
            token = int(i[0])
            i = i[2:]
            place = self.get_place_by_name(i)
            if place == None:
                raise Exception("Place "+ i +" not found")
            place.tokens = token
            self.init_marking[place_idx[place]] = token
    
    def detect_enabled(self):
        """Detects the enabled transitions in the Petri net
            Looping through the transitions and checking if they can fire
        """
        ts = []
        for t in self.transitions:
            if t.can_fire(self.init_marking, self.get_place_index_mapping()):
                print("\nTransition " + str(t.name) + " is enabled")
                ts.append(t)
        return ts
    
    def print_placemap(self):
        """Prints the places and their corresponding orders in a marking"""
        place_idx = self.get_place_index_mapping()
        idx = []
        for p in place_idx:
            idx.append(str(place_idx[p]) + ": " + str(p))
    #   idx = sorted(idx, key=lambda x: int(x.split(":")[0]))
        printListWithDelimiter(idx,", ")
            
    def get_place_by_name(self, name):
        """Returns the place with the given name"""
        for place in self.places:
            if place.name == name:
                return place
        return None

    def merge_net(self, net):
        """Construct a new Petrinet object as a merged net of two Petri nets
            @param net: the Petri net to be merged with the current Petri net
            Using deepcopy to copy the net object
            Simply adding the places and transitions of the net to the current net
        """
        merged_trans = []
        merged_places = []
        merged_arcs = []

        t1 = self.transitions.copy()
        t2 = net.transitions.copy()
        t1_names = []
        t2_names = []

        for t in t1:
            t1_names.append(t.name)

        for t in t2:
            t2_names.append(t.name)

        for t in t1:
            new_t = Transition(t.name)
            if t.name in t2_names:
                t2t = next((x for x in t2 if x.name == t.name), None)

                in_arcs1 = t.incoming_arcs.copy()
                in_arcs2 = t2t.incoming_arcs.copy()
                out_arcs1 = t.outgoing_arcs.copy()
                out_arcs2 = t2t.outgoing_arcs.copy()

                for a in in_arcs1:
                    tmp = next((x for x in merged_places if x.name == a.frm.name), None)
                    if tmp == None:
                        new_p = deepcopy(a.frm)
                    else:
                        new_p = tmp
                    new_a = deepcopy(a)
                    new_a.frm = new_p
                    new_a.to = new_t
                    new_t.add_arc(new_a)
                    merged_arcs.append(new_a)
                    if tmp == None:
                        merged_places.append(new_p)
                for a in in_arcs2:
                    tmp = next((x for x in merged_places if x.name == a.frm.name), None)
                    if tmp == None:
                        new_p = deepcopy(a.frm)
                    else:
                        new_p = tmp
                    new_a = deepcopy(a)
                    new_a.frm = new_p
                    new_a.to = new_t
                    new_t.add_arc(new_a)
                    merged_arcs.append(new_a)
                    if tmp == None:
                        merged_places.append(new_p)
                for a in out_arcs1:
                    tmp = next((x for x in merged_places if x.name == a.to.name), None)
                    if tmp == None:
                        new_p = deepcopy(a.to)
                    else:
                        new_p = tmp
                    new_a = deepcopy(a)
                    new_a.frm = new_t
                    new_a.to = new_p
                    new_t.add_arc(new_a)
                    merged_arcs.append(new_a)
                    if tmp == None:
                        merged_places.append(new_p)
                for a in out_arcs2:
                    tmp = next((x for x in merged_places if x.name == a.to.name), None)
                    if tmp == None:
                        new_p = deepcopy(a.to)
                    else:
                        new_p = tmp
                    new_a = deepcopy(a)
                    new_a.frm = new_t
                    new_a.to = new_p
                    new_t.add_arc(new_a)
                    merged_arcs.append(new_a)
                    if tmp == None:
                        merged_places.append(new_p)

                seen = set()
                seen_add = seen.add
                merged_places = [x for x in merged_places if not (x in seen or seen_add(x))]
                merged_places = list(set(merged_places))
                merged_trans.append(new_t)

            else:

                in_arcs = t.incoming_arcs.copy()
                for a in in_arcs:
                    tmp = next((x for x in merged_places if x.name == a.frm.name), None)
                    if tmp == None:
                        new_p = deepcopy(a.frm)
                    else:
                        new_p = tmp
                    new_a = deepcopy(a)
                    new_a.frm = new_p
                    new_a.to = new_t
                    new_t.add_arc(new_a)
                    merged_arcs.append(new_a)
                    if tmp == None:
                        merged_places.append(new_p)
                out_arcs = t.outgoing_arcs.copy()
                for a in out_arcs:
                    tmp = next((x for x in merged_places if x.name == a.to.name), None)
                    if tmp == None:
                        new_p = deepcopy(a.to)
                    else:
                        new_p = tmp
                    new_a = deepcopy(a)
                    new_a.frm = new_t
                    new_a.to = new_p
                    new_t.add_arc(new_a)
                    merged_arcs.append(new_a)
                    if tmp == None:
                        merged_places.append(new_p)
                merged_trans.append(new_t)
            
    
        merged_net = Petrinet(self.bound)
        merged_net.modify(merged_places, merged_trans, merged_arcs)

        return merged_net
   

#===============================================================================

class TranSys:
    """A State-transition system.
       To be constructed from a Petri net object.
    """

    def __init__(self,net):
        """Inherits most of the Petri net attributes.
           >>> ts = TranSys(net)
        """
        self.net = net
        self.places = net.places
        self.transitions = net.transitions
        self.arcs = net.arcs
        self.init_marking = net.init_marking
        self.placeindex = net.get_place_index_mapping()
        self.marking = self.init_marking
        self.graph_TS = graphviz.Digraph("TS1b")
        self.graph_TS.engine = 'dot'
        self.statespace = []
        self.actions = self.transitions
        self.transitions_relation = []
        self.bound = net.bound
        self.silent_marking = []
        self.build_statespace()
        self.build_transition_relation()

    def all_possible_combinations_of_tuple(self,size, min = 0, max = 1):
        """Simple recursive function to generate state space
            @param size: the size of the tuple
            @param min: the minimum number of tokens
            @param max: the maximum number of tokens
            @return: a list of all possible combinations of the tuple
            Takes exponential time in the size of the tuple
        """
        if size == 1:
            return [[i] for i in range(min,max+1)]
        else:
            return [x + [i] for i in range(min,max+1) for x in self.all_possible_combinations_of_tuple(size-1, min, max)]
        
    def set_init_from_string(self, marking):
        ''' set initial marking from string
        '''
        marking = marking[1:-1]
        marking = marking.split(",")
        self.init_marking = [0]*len(self.places)
        place_idx = self.get_place_index_mapping()
        for i in marking:
            token = int(i[0])
            i = i[2:]
            place = self.get_place_by_name(i)
            if place == None:
                raise Exception("Place "+ i +" not found")
            place.tokens = token
            self.init_marking[place_idx[place]] = token
            
    def build_transition_relation(self):
        """Generate the relation between places and transitions"""
        queue = []
        seen = []
        relation = []
        queue_space= deepcopy(self.statespace)
        while queue_space:
            u = queue_space.pop(0)
            if u in seen:
                continue
            queue.append(u)
            while len(queue) != 0:
                u = queue.pop(0)
                if u in seen:
                    continue
                else:
                    seen.append(u)
                for transition in self.transitions:
                    if transition.can_fire(u, self.placeindex):
                        v = transition.fire(u, self.placeindex)
                        relation.append([u, transition, v])
                        if v not in seen:
                            queue.append(v)
        # transition_relation: ([1,1,0], start, [1,0,1])
        self.transitions_relation = deepcopy(relation)
        for mar,tra,mar1 in relation:
            if mar in seen:
                seen.remove(mar)
            if mar1 in seen:
                seen.remove(mar1)
        self.silent_marking = seen
    
    def build_transys_sequence_from_marking(self, marking):
        """Generate a set of markings from a given initial marking"""
        queue = []
        seen = []
        queue.append(marking)
        while len(queue) != 0:
            u = queue.pop(0)
            if u in seen:
                continue
            else:
                seen.append(u)
            for transition in self.transitions:
                if transition.can_fire(u, self.placeindex):
                    v = transition.fire(u, self.placeindex)
                    if v not in seen:
                        queue.append(v)  
        return seen

    def get_place_index_mapping(self):
        """Place index map, works for both Petri nets and TranSys"""
        m = {}
        cur=0
        for place in self.places:
            if m.get(place) == None:
                m[place] = cur
                cur+=1
        return m
    
    def find_initial_state(self):
        """Find the initial state of the system"""
        self.placeindex = self.get_place_index_mapping()
        return self.init_marking

    def build_statespace(self):
        """Generate the state space of the system
            Bound are set by the Petri net bound
        """
        self.statespace = self.all_possible_combinations_of_tuple(len(self.places), 0, self.bound)

    def transition_relation_dump(self):
        """Dump the transition relation"""
        print("TR = {", end="")
        for x in self.transitions_relation:
            print("(" + str(x[0]) + "," + x[1].name + "," + str(x[2]) + "),", end="")
        print("}\n")


    def fire(self,transition):
        """Fire a transition and return the new marking"""
        if transition.can_fire(self.marking, self.placeindex):
            self.marking = transition.fire(self.marking, self.placeindex)
            return self.marking
        else:
            print("Transition cannot be fired")
            return self.marking

    def state_space_dump(self):
        print("S = {", end="")
        for x in self.statespace:
            print("[" + str(x[0]) + "," + str(x[1]) + "," + str(x[2]) + "], ", end="")
        print("}\n")
    
    def print_marking(self):
        print("{", end = "")
        place_idx = self.placeindex
        mrk = self.marking

        for p in place_idx:
            print(str(mrk[place_idx[p]]) ,  ", ", end="")
        print("}\n")
    
    def print_definition(self):
        """Print the definition to console"""
        self.state_space_dump()
        print("A = ", end = "")
        printListWithDelimiter(self.transitions,", ")
        self.transition_relation_dump()

    def set_init_marking(self,marking):
        self.init_marking = marking
        l = len(self.places)
        for i in range(0,l):
            self.places[i].token = marking[i]

    def print_placemap(self):
        """Prints the places and their corresponding orders in a marking"""
        place_idx = self.placeindex.copy()
        idx = []
        for p in place_idx:
            idx.append(str(place_idx[p]) + ": " + str(p))
        idx = sorted(idx, key=lambda x: int(x.split(":")[0]))
        printListWithDelimiter(idx,", ")
    

    def ts_graph_build(self,init_mrk = None, mode = "text"):
        """Builds and prints the TS as text or as image.
        """
        if mode == "text":
            print("State-transition system of given Petri net: \n")
            print("The position of each place: ", end="")
        self.print_placemap()
        seen = []
        tmp = []
        if init_mrk != None:
            seen = (self.build_transys_sequence_from_marking(init_mrk))
            for s in self.statespace:
                if s not in seen:
                    tmp = (self.build_transys_sequence_from_marking(s))
                    for t in tmp:
                        seen.append(t)
                    self.ts_graph_generate(tmp,mode)
        else:
            for place in self.silent_marking:
                if mode == "text":
                    print(str(place) + "--" + "None" + "-->")
                else:
                    self.graph_TS.node(str(place))
            self.ts_graph_generate(self.statespace,mode)
            
        if mode == "graph":
            display.display(self.graph_TS)
            self.graph_TS.clear()
            
    def ts_graph_generate(self, init, mode):
        if mode == "text":
            self.ts_graph_generate_text(init)
        elif mode == "graph":
            self.ts_graph_generate_graph(init)
            
    def ts_graph_generate_text(self,init):
        """Generate the TS as text
            Looping through initial marking and transition relation
        """
        found = False
        for i in init:
            for y in self.transitions_relation:
                if i == y[0]:
                    found = True
                    print(str(i) + "--" + y[1].name + "-->" + str(y[2]))
        if not found:
            print(str(init[0]) + "--" + "None" + "-->")
            
    def ts_graph_generate_graph(self,init):
        """Generate the TS as graph
            Looping through initial marking and transition relation
        """
        found = False
        for i in init:
            for y in self.transitions_relation:
                if i == y[0]:
                    found = True
                    self.graph_TS.edge(str(i),str(y[2]),y[1].name)
        if not found:
            self.graph_TS.node(str(init[0]))