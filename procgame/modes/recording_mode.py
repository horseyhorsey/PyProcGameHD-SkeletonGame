__author__ = 'Dave Horsefield'

import logging
from procgame.game.advancedmode import AdvancedMode


class RecordingMode(AdvancedMode):
    """ A mode to display that the game is recording """

    def __init__(self, game):
        super(RecordingMode, self).__init__(game=game, priority=23452, mode_type=AdvancedMode.System)

        self.logger = logging.getLogger('RecordingMode')

    def mode_started(self):
        self.game.start_recording()
        self.txtLayer = self.game.generateLayer("Recording")
        self.txtLayer.set_target_position(self.game.dmd.width / 2, 15)
        self.layer = self.txtLayer


