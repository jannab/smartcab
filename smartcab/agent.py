import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.actions = ['forward', 'left', 'right', None]
        self.valid_states = ['forward, red light', 'turn left, red light', 'turn right, red light, someone left', 'turn right, red light, no one left', 'forward, green light', 'turn left, green light, someone oncoming', 'turn left, green light, no one oncoming', 'turn right, green light']
        self.qtable = self.qtable = [[0] * (len(self.actions))] * (len(self.valid_states))
        self.learning_rate = 1.0
        self.discount_factor = 0.01

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        self.update_state(inputs)

        # Select action according to your policy
        action = self.driving_agent()

        # Execute action and get reward
        reward = self.env.act(self, action)

        # Learn policy based on state, action, reward
        self.learn_policy(self.state, action, reward)

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

    def driving_agent(self):
        best_choice = random.choice(self.actions)
        index_state = self.get_state_index(self.state)
        best_choice_index = self.qtable[index_state].index(min(self.qtable[index_state]))
        if self.qtable[index_state][best_choice_index] != 0:
            best_choice = self.actions[best_choice_index]
        # try to not get stuck that much
        if self.qtable[index_state][best_choice_index] == 0:
            best_choice = random.choice(self.actions)
        if (best_choice_index == 3) & (self.qtable[index_state][best_choice_index] < 0.9):
            best_choice = random.choice(self.actions)

        return best_choice

    def update_state(self, inputs):
        if inputs['light'] == 'red':
            if self.next_waypoint == 'forward':
                self.state = self.valid_states[0]
            elif self.next_waypoint == 'left':
                self.state = self.valid_states[1]
            elif self.next_waypoint == 'right':
                if inputs['left'] != None:
                    self.state = self.valid_states[2]
                else:
                    self.state = self.valid_states[3]
        else:
            if self.next_waypoint == 'forward':
                self.state = self.valid_states[4]
            elif self.next_waypoint == 'left':
                if inputs['oncoming'] != None:
                    self.state = self.valid_states[5]
                else:
                    self.state = self.valid_states[6]
            elif self.next_waypoint == 'right':
                self.state = self.valid_states[7]

    def learn_policy(self, state, action, reward):
        index_state = self.get_state_index(state)
        index_action = self.get_action_index(action)

        old_value = self.qtable[index_state][index_action]
        best_next_action_index = self.qtable[index_state].index(max(self.qtable[index_state]))
        estimate_optional_future_value = self.qtable[index_state][best_next_action_index]

        self.qtable[index_state][index_action] = old_value + self.learning_rate * (reward + self.discount_factor * estimate_optional_future_value - old_value)
        #print self.qtable

    def get_state_index(self, state):
        index_state = 8
        for i in range(len(self.valid_states)):
            if self.valid_states[i] == state:
                index_state = i
        return index_state

    def get_action_index(self, action):
        index_action = 3
        for i in range(len(self.actions)):
            if self.valid_states[i] == action:
                index_action = i
        return index_action



def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    #sim = Simulator(e, update_delay=0.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
