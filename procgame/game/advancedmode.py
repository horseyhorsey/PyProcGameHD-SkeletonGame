from ..game import Mode
import re
from procgame.dmd import GroupedLayer

class AdvancedMode(Mode):
    """Abstraction of a game mode to be subclassed by the game
    programmer.    
    """    
    System  = 0  # added on reset, removed/readded on reset, removed never
    Ball    = 1  # added on ball start, removed on ball end
    Game    = 2  # added on game start, removed on game end
    Manual  = 3  # programmer must add/remove mode

    def __init__(self, game, priority, mode_type=Manual):
        """ initializing an AdvancedMode potentially does a lot more than just creating the mode.
            0. The mode is created
            1. Depending on the "mode_type" the mode is recorded to be automatically added/removed
                when specific game events occur --note: the default type is 'manual' so you're adding
                it yourself...
            2. The mode is scanned for methods that handle specific skeletongame events (prefix: evt_)
                and this mode is recorded as a mode that can handle those sorts of events

            An assumption is made that only one instance of any Mode that you define will only be 
            created _once_ (i.e., Singleton behavior).  Creating a second instance of a game mode
            will result in a runtime error.  Do not "set all your modes to None and 
            re-create them on reset()" in SkeletonGame.  Instead, you may provide a reset() method for your
            AdvancedModes and call that on reset in order to reset any state variables to a clean state.
        """
        super(AdvancedMode, self).__init__(game, priority)

        self.event_map = {}
        self.mode_type = mode_type

        self.mode_init()

        game.notifyOfNewMode(self)

        # discover evt handler functions and log them -- those methods have the format: evt_name(self):
        # handler_func_re = re.compile('evt_(?P<name>[a-zA-Z0-9_]+)?')
        handler_func_re = re.compile('(?P<name>(evt_[a-zA-Z0-9_]+))+?')

        for item in dir(self):
            m = handler_func_re.match(item)
            if m == None:
                continue
            evt_name = m.group('name')
            self.game.add_evt_handler(mode=self, evt_name=evt_name)
            handlerfn = getattr(self, item) # get a reference to the actual method
            self.event_map[evt_name] = handlerfn 

    def mode_init(self):
        """ define this method to set up initial vars/display stuff as needed 
            Note it is called only when this mode is first created (i.e., once, only) 
        """
        pass

    def reset(self):
        """ define this method to clean up anything to give a fresh start.
            this is invoked whenever game.reset() is called.  Use this
            to clear out state vars if you are so inclined (though you 
            can probably get by with evt_ball_starting, evt_game_ending, etc.)
        """
        pass

    def handle_game_event(self, evt_name, params=None):
        """ dispatches a game event of the given type if an evt_ method has been defined """
        fn = self.event_map[evt_name]

        if(params is None):
            return fn()
        else:
            return fn(params)

    def force_event_next(self):
        self.game.notifyNextModeNow(self)

    def play_sequence(self, key, mute_sound=False, mute_lamps=False, overlay_txt=[], font_key=None, font_style=None):
        
        generatedSeq = self.get_sequence(key)

        if generatedSeq is not None:

            self.cancel_delayed('clear_layer')

            generatedSeq.layer.reset()

            text = None
            if overlay_txt:
                text = self.game.generateLayer(overlay_txt, font_key=font_key,font_style=font_style)

            group = GroupedLayer(self.game.dmd.width, self.game.dmd.height, [generatedSeq.layer, text])

            self.layer = group

            if not mute_sound and generatedSeq.sound is not None:
                self.game.sound.play(generatedSeq.sound)

            if not mute_lamps and generatedSeq.lampshow is not None:
                self.game.lampctrl.play_show(generatedSeq.lampshow)

            self.delay("clear_layer", None, generatedSeq.duration, self.clear_layer)
        else:
            self.game.logger.debug("Couldn't find generated sequence for the given key : {}".format(key))

    def get_sequence(self, key):
        """ Gets a Sequence from the games generated_Sequences"""
        if key in self.game.generated_sequences:
            return self.game.generated_sequences[key]
        else:
            return None

    def clear_layer(self):
        self.layer = None
