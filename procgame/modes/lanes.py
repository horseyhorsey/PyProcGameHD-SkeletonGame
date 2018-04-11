__author__ = 'Dave Horsefield'
__version__ = 1.0

import collections
import logging
import procgame
from procgame.game.advancedmode import AdvancedMode


class Lanes(AdvancedMode):

    """ Lanes mode with rotating lamps

    Parameters:

        'game': game
        'priority': mode priority
        'switch_list': list of procgame switches
        'lamps': list of procgame lamps
        'reset_on_new_ball': bool to reset the variables on mode starting
     """

    lane_count = 3
    """ The amount of lane triggers """

    switch_list = []
    """ List of the switches to provide handlers for"""

    target_lamps = []
    """ List of lamps that match the count of the lanes"""

    switch_variables = []
    """ The rollover triggers. A list of Boolean values"""

    reset_on_new_ball = True
    """ Reset the lane variables when a new ball starts?"""

    def __init__(self, game, priority=2, switch_list=[], lamps=[], reset_on_new_ball=True):
        super(Lanes, self).__init__(game=game, priority=priority, mode_type=AdvancedMode.Ball)

        self.logger = logging.getLogger('LanesMode')

        self.reset_on_new_ball = reset_on_new_ball
        self.lane_count = len(switch_list)
        self.switch_list = switch_list

        for i in range(0, self.lane_count):
            self.switch_variables.append(False)

        self.switch_variables = collections.deque(self.switch_variables)

        for switch in switch_list:
            self.add_switch_handler(name=switch.name, event_type='closed',
                                        delay=None, handler=self.lane_switch_callback)

        self.target_lamps = lamps

    def mode_started(self):
        if self.reset_on_new_ball:
            self.reset_lanes()

    def lane_switch_callback(self, sw):
        self.logger.debug("lane callback switch {}".format(sw.name))

        index = self.switch_list.index(sw)
        if not self.switch_variables[index]:
            self.switch_variables[index] = True
            self.update_lamps()
        return procgame.game.SwitchContinue

    def check_lanes_completed(self):
        """ Are the lanes completed?"""
        if False not in self.switch_variables:
            return True
        else:
            return False

    def reset_lanes(self):
        """ Resets the switch variables and updates lamps"""
        for i in range(0, self.lane_count-1):
            self.switch_variables[i] = False

        self.update_lamps()

    def sw_flipperLwL_active(self, sw):
        """ Changes lanes left"""
        self.change_lanes_left()
        return procgame.game.SwitchContinue

    def sw_flipperLwR_active(self, sw):
        """ Changes lanes right"""
        self.change_lanes_right()
        return procgame.game.SwitchContinue

    def update_lamps(self):
        """ Updates lamps depending on if the lane is enabled """
        for target, lamp in zip(self.switch_variables, self.target_lamps):
            if target:
                lamp.enable()
            else:
                lamp.disable()

    def change_lanes_left(self):
        """ Changes the target_switches left """
        self.switch_variables.rotate(-1)
        self.update_lamps()

    def change_lanes_right(self):
        """ Changes the lamps right """
        self.switch_variables.rotate(1)
        self.update_lamps()
