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
        self.totalReward = 0.0 # totals the rewards for every step
        self.possible_actions = ['forward', 'left', 'right', None]


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        state = self.update_state(inputs)

        # Select action according to your policy
        action = self.driving_agent()

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.totalReward += reward

        # TODO: Learn policy based on state, action, reward

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, total reward = {}".format(deadline, inputs, action, reward, self.totalReward)  # [debug]
        print "Total reward: {}".format(self.totalReward)

    def update_state(self, inputs):
        """Updates the state label visable and returns the state"""

        state = [self.next_waypoint, inputs['light'], inputs['oncoming'], inputs['left']]
        self.state = "Go: {}, lights: {}, oncoming: {}, left: {}".format(state[0], state[1], state[2], state[3])

    def driving_agent(self):
        """Find the best next action"""

        best_choice = random.choice(self.possible_actions)
        return best_choice


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.2, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
