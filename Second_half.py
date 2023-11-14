from dataclasses import dataclass

@dataclass
class Msg:
	sender: int
	recipient: int
	session_type: int

	def __init__(self, sender_, recipient_, session_type_):
		self.sender=sender_
		self.recipient=recipient_
		self.session_type=session_type_
		return

	#def __str__(self):
	#	return ("Sender: "+str(self.sender))+"\n"+("Recipt: "+str(self.recipient))+"\n"+("SesTyp: "+str(self.session_type))

@dataclass
class State:
	actor_states: list[str]

	def __init__(self, states):
		self.actor_states = states
		return

	def __str__(self):
		return "States: "+str(self.actor_states)

@dataclass
class Option:
	start_state: State
	in_msg: Msg
	out_msg: list[Msg]
	end_state: State

	def __init__(self, ss, im, om, es):
		self.start_state = ss
		self.in_msg = im
		self.out_msg = om
		self.end_state = es
		return

	def __str__(self):
		return "Starting State:\n"+str(self.start_state)+"\nIncoming Message:\n"+str(self.in_msg)+"\nOutgoing Message(s):\n"+str(self.out_msg)+"\nEnding State:\n"+str(self.end_state)+"\n"

@dataclass
class Program_State:
	state: State
	msgs: list[Msg]

	def __init__(self, state_, msgs_):
		self.state = state_
		self.msgs = msgs_


def read_state(line, max_kleene):
	i=0
	states = []
	while (i<len(line)):
		j=i
		while (line[j]!="," and line[j]!="\n"):
			j+=1
		temp = line[i:j]
		if (temp.isnumeric()):
			temp=str(int(temp)%max_kleene)
		states.append(temp)
		i=j+2
	return State(states)

def read_msg(line, max_kleene):
	i=0
	nums = []
	while (i<len(line)):
		j=i
		while (line[j]!="," and line[j]!="\n"):
			j+=1
		temp = line[i:j]
		if (temp.isnumeric()):
			temp=str(int(temp)%max_kleene)
		nums.append(temp)
		i=j+2
	return Msg(nums[0], nums[1], nums[2])

def parse_start(lines, num_starting_messages):
	start_state = read_state(lines[0], len(lines[0]))
	start_msgs = []
	for i in range(num_starting_messages):
		start_msgs.append(read_msg(lines[1+i], len(lines[1+i])))
	return Program_State(start_state, start_msgs)

def read_option(lines, option_start, max_kleene):
	ss = read_state(lines[option_start], max_kleene)
	im = read_msg(lines[option_start+1], max_kleene)
	om = []
	i = 2
	while(len(lines[option_start+i+1])>=3):
		om.append(read_msg(lines[option_start+i], max_kleene))
		i+=1
	es = read_state(lines[option_start+i], max_kleene)
	return i, Option(ss, im, om, es)

def read_file(filename, num_starting_messages):
	with open(filename, "r") as in_file:
		lines = in_file.readlines()
		program_state = parse_start(lines, num_starting_messages)
		options = []
		i = num_starting_messages+2
		while (i<len(lines)):
			temp, option = read_option(lines, i, len(program_state.state.actor_states))
			i+=temp+2
			options.append(option)
	return program_state, options

def check_option_valid(test_option, program_state):
	global prevstates
	if (test_option, program_state) in prevstates:
		return False
	for state in range(len(test_option.start_state.actor_states)):
		if (test_option.start_state.actor_states[state].isnumeric() and test_option.start_state.actor_states[state]!=program_state.state.actor_states[state]):
			return False
	for msg in program_state.msgs:
		if (msg.sender==test_option.in_msg.sender and msg.recipient==test_option.in_msg.recipient and msg.session_type==test_option.in_msg.session_type):
			prevstates.append((test_option, program_state))
			#print(prevstates)
			return True
	return False

def step(program_state, chosen_option):
	#if (check_option_valid(chosen_option, program_state)):
	new_msgs = []
	for msg in program_state.msgs:
		if not (msg.sender==chosen_option.in_msg.sender and msg.recipient==chosen_option.in_msg.recipient and msg.session_type==chosen_option.in_msg.session_type):
			new_msgs.append(msg)
	for msg in chosen_option.out_msg:
		new_msgs.append(msg)
	new_states = []
	for state in range(len(program_state.state.actor_states)):
		if not chosen_option.end_state.actor_states[state].isnumeric():
			new_states.append(program_state.state.actor_states[state])
		else:
			new_states.append(chosen_option.end_state.actor_states[state])
	return Program_State(State(new_states), new_msgs)
	#return None

def recurse(program_state, options):
	#print(program_state.state)
	if (len(program_state.msgs)==0):
		return (program_state.msgs, None)
	for option in options:
		if check_option_valid(option, program_state):
			recursion = recurse(step(program_state, option), options)
			if recursion != "Success":
				return (program_state.msgs, recursion)
			else:
				return recursion
	return "Success"

def pretty_print(result, names):
	if result == "Success":
		print("No circular dependencies found!")
	else:
		t = 0
		while result != None:
			print("Messages in queue at time t = " + str(t))
			for msg in result[0]:
				print("\tFrom: "+names[0][int(msg.sender)]+", \tTo: "+names[0][int(msg.recipient)]+", \tSession Type: "+names[1][int(msg.session_type)])
			t+=1
			result = result[1]



program_state, options = read_file("demo.txt", 2)
prevstates = []
result = recurse(program_state, options)
names = (["c1", "c2", "p1", "p2"], ["get()", "gotStick()", "release()", "token"])
pretty_print(result, names)

### TO DO: ###
# Kleene Star Implementation
# Record lookup of previous states to improve performance
# Use graph to give more detailed explanation of failure