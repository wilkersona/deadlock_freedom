from dataclasses import dataclass

@dataclass
class St_State:
	actor1: int
	actor2: int
	session_type: str

	def __init__(self, actor1_, actor2_, session_type_):
		if (actor1_>actor2_):
			self.actor1=actor1_
			self.actor2=actor2_
		else:
			self.actor1=actor2_
			self.actor2=actor1_
		self.session_type=session_type_
		return

@dataclass
class Msg:
	sender: int
	recipient: int
	session_type: str

	def __init__(self, sender_, recipient_, session_type_):
		self.sender=sender_
		self.recipient=recipient_
		self.session_type=session_type_
		return

@dataclass
class Step_Option:
	start_state: list[St_State]
	receive: Msg
	sends: list[Msg]
	end_state: list[St_State]

	def __init__(self, ss, r, s, es):
		self.start_state=ss
		self.receive=r
		self.sends=s
		self.end_state=es
		return

@dataclass
class Actor_Steps:
	steps: list[Step_Option]
	name: str

	def __init__(self, steps_, name_):
		self.steps = steps_
		self.name = name_
		return

@dataclass
class Actor:
	name: str
	actor_type: str
	rel_names: list[str]

	def __init__(self, name_, type_, rel_names_):
		self.name = name_
		self.actor_type = type_
		self.rel_names = rel_names_

@dataclass
class Start_Msg:
	sender: str
	recipient: str
	session_type: str

	def __init__(self, sender_, recipient_, session_type_):
		self.sender=sender_
		self.recipient=recipient_
		self.session_type=session_type_
		return

@dataclass
class St_Pair:
	actor1: str
	actor2: str
	type1: str
	type2: str

	def __init__(self, actor1_, actor2_, type1_="", type2_=""):
		if (actor1_>actor2_):
			self.actor1=actor1_
			self.actor2=actor2_
			self.type1=type1_
			self.type2=type2_
		else:
			self.actor1=actor2_
			self.actor2=actor1_
			self.type1=type2_
			self.type2=type1_
		return

	def compare(self, other):
		if (self.actor1>other.actor1 or (self.actor1==other.actor1 and self.actor2>other.actor2)):
			return 1
		elif (self.actor1==other.actor1 and self.actor2==other.actor2):
			return 0
		else:
			return -1

def read_file(filename):
	important_lines = []
	with open(filename, "r") as in_file:
		lines = in_file.readlines()
		for line in lines:
			if "//@" in line:
				important_lines.append(line)
				#print(line)
	return important_lines

def filter_intro(string):
	result = string[string.find("//@")+3:]
	while result[0] == ' ':
		result = result[1:]
	return result

def filter_commas(string):
	cur_str = string
	result = []
	while "," in cur_str:
		result.append(cur_str[:cur_str.find(",")])
		cur_str = cur_str[cur_str.find(",")+2:]
	result.append(cur_str)
	return result

def print_commas(arr):
	if (len(arr)==0):
		print()
		return
	result=""
	for i in range(len(arr)-1):
		result+=str(arr[i])
		result+=", "
	result+=str(arr[len(arr)-1])
	#result+="\n"
	print(result)
	return

def print_state(start_states, st_arr, actor_names, msg_lookup):
	result = []
	for i in range(len(st_arr)):
		result.append(chr(65+i))
	for stst in start_states:
		cur_pair = St_Pair(actor_names[stst.actor1+1], actor_names[stst.actor2+1])
		for i in range(len(st_arr)):
			if (cur_pair.compare(st_arr[i])==0):
				result[i] = str(msg_lookup[stst.session_type])

	return result

def print_msg(msg, sr_arr, actor_names, msg_lookup):
	result = []
	result.append(sr_arr.index(actor_names[msg.sender+1]))
	result.append(sr_arr.index(actor_names[msg.recipient+1]))
	result.append(msg_lookup[msg.session_type])
	return result

def parse(lines):
	options = []
	msg_lookup = {}
	actor_steps = []
	actors_created = []
	start_msgs = []
	cur_msg = ""

	start_states = []
	receive = None
	sends = []
	end_states = []
	for line in lines:
		if "requires" in line:
			other_actor = int(line[line.find("[")+1:line.find("]")])
			msg = line[line.find("]")+2:]
			start_states.append(St_State(other_actor, -1, msg))
		elif "ensures" in line:
			if "receive" in line:
				other_actor = int(line[line.find("[")+1:line.find("]")])
				msg = line[line.find("]")+2:]
				receive = Msg(other_actor, -1, msg)
			elif "send" in line:
				other_actor = int(line[line.find("[")+1:line.find("]")])
				msg = line[line.find("]")+2:]
				sends.append(Msg(-1, other_actor, msg))
			elif "ST" in line:
				other_actor = int(line[line.find("[")+1:line.find("]")])
				msg = line[line.find("]")+2:]
				end_states.append(St_State(other_actor, -1, msg))
			else:
				print("Parsing Error:")
				print(line)
		elif "also" in line:
			options.append(Step_Option(start_states, receive, sends, end_states))
			start_states = []
			receive = None
			sends = []
			end_states = []
		elif "Msg" in line:
			if (receive!=None):
				options.append(Step_Option(start_states, receive, sends, end_states))
				start_states = []
				receive = None
				sends = []
				end_states = []
				actor_steps.append(Actor_Steps(options, cur_msg))
				options = []
			msg_lookup.update({line[line.find("]")+2:]: int(line[line.find("[")+1:line.find("]")])})
			cur_msg = filter_intro(line[:line.find("[")-4])
		elif "init" in line:
			options.append(Step_Option(start_states, receive, sends, end_states))
			start_states = []
			receive = None
			sends = []
			end_states = []
			actor_steps.append(Actor_Steps(options, cur_msg))
			options = []
		elif "Actor" in line:
			actors_created.append(Actor(line[line.find("Actor")+6:line.find("(")], filter_intro(line[:line.find("Actor")-1]), filter_commas(line[line.find("(")+1:line.find(")")])))
		elif "][" in line:
			start_msgs.append(Start_Msg(line[line.find(" [")+2:line.find("][")], line[line.find("][")+2:line.find("] ")], line[line.find("] ")+2:]))
		else:
			print("Parsing Error:")
			print(line)
	#print(len(actor_steps[0].steps))
	#print(msg_lookup)
	return (actor_steps, msg_lookup, actors_created, start_msgs)

def generate_output(actor_steps, msg_lookup, actors_created, start_msgs):
	#count number of sessions
	num_sessions=0
	for actor in actors_created:
		num_sessions+=len(actor.rel_names)
	num_sessions/=2
	#assign in order
	st_arr = [] #session type array
	sr_arr = [] #send-receive index array
	for actor in actors_created:
		sr_arr.append(actor.name)
		for pair in actor.rel_names:
			cur_pair = St_Pair(actor.name, pair)
			i=0
			while (i<len(st_arr) and cur_pair.compare(st_arr[i])==1):
				i+=1
			if (i==len(st_arr)):
				st_arr.append(cur_pair)
			elif (cur_pair.compare(st_arr[i])==-1):
				st_arr.insert(i, cur_pair)
	sr_arr.sort()
	print_commas([0 for _ in range(int(num_sessions))])
	for msg in start_msgs:
		print_commas([sr_arr.index(msg.sender), sr_arr.index(msg.recipient), msg_lookup[msg.session_type]])
	print_commas([])
	#print(st_arr)
	#print(sr_arr)

	#go through each set of options and determine print
	for actor_step in actor_steps:
		for step in actor_step.steps:
			#for each relevant actor
			for actor in actors_created:
				if (actor.actor_type==actor_step.name):
					print_commas(print_state(step.start_state, st_arr, [actor.name] + actor.rel_names, msg_lookup))
					print_commas(print_msg(step.receive, sr_arr, [actor.name] + actor.rel_names, msg_lookup))
					for send in step.sends:
						print_commas(print_msg(send, sr_arr, [actor.name] + actor.rel_names, msg_lookup))
					print_commas(print_state(step.end_state, st_arr, [actor.name] + actor.rel_names, msg_lookup))
					print_commas([])
	#print_commas([])



lines = read_file("DP_Better.salsa")
actor_steps, msg_lookup, actors_created, start_msgs = parse(lines)
generate_output(actor_steps, msg_lookup, actors_created, start_msgs)