import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from math import log


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.q_table = self.initialize_q_table()
        #print self.q_table
        self.totalReward = 0.0 # totals the rewards for every step
        self.trial_reward = 0.0
        self.totalTime = 0
        self.first_deadline = self.env.get_deadline(self)
        self.trialTime = 0
        self.learning_rate = 0.0
        self.discount_factor = 0.1
        self.exploration_rate = 0


    def reset(self, destination=None):
        print "{},{},{},{},{},{},{}".format(self.learning_rate,self.discount_factor,self.exploration_rate,self.first_deadline,self.trialTime,self.totalReward,self.trial_reward)

        self.planner.route_to(destination)
        self.first_deadline = self.env.get_deadline(self)
        self.trial_reward = 0.0
        self.trialTime = 0
        # Prepare for a new trip; reset any variables here, if required


    def update(self, t):
        #print self.q_table
        self.totalTime += 1
        self.trialTime += 1

        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        state = self.get_the_state(inputs)
        self.state = "Go: {}, lights: {}, oncoming: {}, left: {}".format(self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'])

        # Select action according to your policy
        da = self.driving_agent(state, t, deadline)
        action = da[0]
        #action = random.choice(self.env.valid_actions)

        # Execute action and get reward
        reward = self.env.act(self, action)
        if reward < 0:
            print self.state
        self.totalReward += reward
        self.trial_reward += reward

        # Learn policy based on state, action, reward
        self.learning_policy(self.totalTime, reward, state, action, da[1])

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, total reward = {}".format(deadline, inputs, action, reward, self.totalReward)  # [debug]
        #print "Total reward: {}".format(self.totalReward)
        #print "Trial Reward: {}".format(self.trial_reward)

    def driving_agent(self, state, t, deadline):
        """Find the best next action"""

        #action = random.choice(self.env.valid_actions)

        # Take q values for the actual state plus every possible action
        decision_table = self.get_decision_table(state)

        # take action and corresponding q-value with the maximum q-value from the decision table
        q_value_now, action = max((value, key) for key, value in decision_table.iteritems())

        return (action, q_value_now)

    def initialize_q_table(self):
        """Initializes Q table with random values"""
        planned_states = ['forward', 'left', 'right']
        light_states = ['green', 'red']
        possible_actions = self.env.valid_actions

        q_keys = []
        for action in possible_actions:
            for left in possible_actions:
                for oncoming in possible_actions:
                    for light in light_states:
                        for planned_state in planned_states:
                            q_keys.append((planned_state, light, oncoming, left, action))

        q_initialization_values = []
        for _ in range(0, len(q_keys)):
            q_initialization_values.append(random.random() * 4)

        return dict(zip(q_keys, q_initialization_values))

    def learning_policy(self, t, reward, state, action, q_value_present):
        #self.learning_rate = 1.0
        #self.learning_rate = (1.0 / t) + 0.75
        self.learning_rate = (1.0 / (t + 5)) + 0.75
        learning_rate = self.learning_rate
        #discount_factor = 0.4
        discount_factor = self.discount_factor
        new_state = self.get_the_state(self.env.sense(self))
        new_decision_table = self.get_decision_table(new_state)
        max_future_reward, action = max((value, key) for key, value in new_decision_table.iteritems())

        new_q_value = reward + discount_factor * max_future_reward

        # set q value in q table
        self.q_table[(state + (action,))] = q_value_present + learning_rate * (new_q_value - q_value_present)

    def get_the_state(self, inputs):
        return (self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left'])

    def get_decision_table(self, state):
        return {None: self.q_table[(state + (None,))], 'right': self.q_table[(state + ('right',))], 'left': self.q_table[(state + ('left',))], 'forward': self.q_table[(state + ('forward',))]}

    #def evaluate_trial(self):



def run():
    """Run the agent for a finite number of trials."""
    #import sys
    #f = open("learning_rate_4_5.csv", 'w')
    #sys.stdout = f

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0, display=False)
    #sim = Simulator(e, update_delay=5.0, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
    #f.close()


if __name__ == '__main__':
    run()
