__author__ = 'Dave Horsefield'

from procgame.dmd.layers import SolidLayer, HDTextLayer, ScriptlessLayer, GroupedLayer, ScaledLayer
from procgame.dmd import TransitionLayer
from procgame.game import AdvancedMode


class TrophyMode(AdvancedMode):

    _trophy_icon = None
    """ Icon to use for trophy """

    _solid_layer = None
    """ A layer to hold behind the trophy text """

    _trophy_text = None
    """ Text layer to describe the current trophy """

    def __init__(self, game, priority=69):
        super(TrophyMode, self).__init__(game, priority=priority, mode_type=AdvancedMode.Ball)

        self.layer = None
        self._solid_layer = SolidLayer(self.game.dmd.width, 50, (128, 128, 128, 192), False)
        self._solid_layer.set_target_position(2, self.game.dmd.height - 20)

        self._trophy_text = HDTextLayer(0, self.game.dmd.height / 2,
                                        self.game.fonts['small'], width=self.game.dmd.width, height=self.game.dmd.height)

    def mode_started(self):
        pass

    def mode_stopped(self):
        pass

    def _build_trophy_scripted_layer(self, key, trop_data):
        """ Returns a scripted layer with rect, text, icon. Fades in/out"""

        # The icon, if not found use the default trophy icon
        icon = trop_data['Trophys'][key]['icon']
        if not icon:
            icon = 'trophy'
        self._trophy_icon = self.game.animations[icon]
        self._trophy_icon = ScaledLayer(20, 40, self._trophy_icon)
        self._trophy_icon.set_target_position(2, self.game.dmd.height - self._trophy_icon.height + 4)

        # Text to display, Set the position to the width of the new scaled trophy icon layer
        self._trophy_text.set_text(trop_data['Trophys'][key]['description'])
        self._trophy_text.set_target_position(self._trophy_icon.width + 5, self.game.dmd.height - 16)

        # Group the icon and text
        group = GroupedLayer(558, 300, [self._solid_layer, self._trophy_icon, self._trophy_text])

        fade_in = TransitionLayer(None, group, 'CrossFadeTransition', None, 12.5)
        fade_out = TransitionLayer(group, None, 'CrossFadeTransition', None, 12.5)

        # Build script layer
        sl = ScriptlessLayer(self.game.dmd.width, self.game.dmd.height)
        sl.append(fade_in, 2)
        sl.append(fade_out, 3)

        return sl

    def is_trophy_complete(self, key):
        """ Returns the complete date """
        if self.game.current_player().trophy is not None:
            return self.game.current_player().trophy.is_trophy_completed(key)

    def set_and_display_trophy_completed(self, key):
        """ Sets the trophy to completed and displays it to the player """

        trophy = self.game.current_player().trophy
        if trophy is not None:

            trophy.set_completed(key)

            # Clear layer delay if running already
            self.cancel_delayed('clear_layer')

            self.game.sound.play('ss_successV')

            # clear layer from duration of script layer we get back
            self.layer = self._build_trophy_scripted_layer(key, trophy.player_data)
            self.delay('clear_layer', None, self.layer.duration(), self.clear_display)

    def clear_display(self):
        self.layer = None
