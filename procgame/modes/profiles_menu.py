from procgame.highscore import HD_InitialEntryMode

import procgame.game
from procgame.game import Mode

__author__ = 'Dave Horsefield'


class ProfileMenu(Mode):
    """ A menu to create, load & save player profiles """

    _players = {1: 'Empty', 2: 'Empty', 3: 'Empty', 4: 'Empty'}
    """ A list of default players for the menu"""

    _main_menu_items = {0: ['Quick Start', 'Start a Quick Game'],
                        1: ['Players', 'Manage players'],
                        2: ['Exit', 'Back To Attract']}
    """ main menu items """

    _current_menu = 0
    """ The selected menu """

    _last_selected_menu = 0

    _selected_player = 1
    """ The selected player """

    _selected_profile = 0
    """ The selected profile """

    _selectable_players = []

    _selected_frame = 0
    """ Keeps track of the selected text layer in a menu """

    _blinkingItem = {0: True, 1: False, 2: False, 3: False, 4: False, 5: False}

    def __init__(self, game, priority=125):
        super(ProfileMenu, self).__init__(game=game, priority=priority)

        # Get the profile manager from skeleton game
        self.profile_manager = game.profile_manager

        # Game title
        # self.game_title = title

        # Prepare the layers, we can use set text later
        self.initialize_layers()

        # Update the text layers to display the first menu
        self.update_layers()

        self.layer = self._get_grouped_layers(0)

    def mode_started(self):
        # reset the menu making sure we're top most.
        self._current_menu = 0
        self._selected_player = 1
        self._selected_frame = 0
        self._last_selected_menu = 0
        self.update_layers()
        pass

    def initialize_layers(self):
        _width = self.game.dmd.width
        _height = self.game.dmd.height

        self.bg_layer = self.game.animations['chrome']
        self._title_layer = self.generate_text_layer(_width/2, 2, 'med')

        self._menu_top_layer = self.generate_text_layer(_width/2, _height / 3)
        self._menu_mid_layer = self.generate_text_layer(_width/2, _height / 2)
        self._menu_bottom_layer = self.generate_text_layer(_width/2, (_height / 2) + (_height / 5))
        self._start_game = self.generate_text_layer(_width - (_width / 4), (_height / 2) + (_height / 3))

        self._controls_info_layer = self.generate_text_layer(_width / 2, _height / 6, 'tiny')
        self._info_layer = self.generate_text_layer(_width / 2, _height - (_height / 10), 'tiny')

        # Player layers
        self._plr1 = self.generate_text_layer(4, _height / 4, justify='left')
        self._plr2 = self.generate_text_layer(_width / 4, _height / 4, justify='left')
        self._plr3 = self.generate_text_layer(_width - (_width / 2), _height / 4, justify='left')
        self._plr4 = self.generate_text_layer(_width - (_width / 4), _height / 4, justify='left')

        self._plr1Name = self.generate_text_layer(4, _height / 2, justify='left')
        self._plr2Name = self.generate_text_layer(_width / 4, _height / 2, justify='left')
        self._plr3Name = self.generate_text_layer(_width - (_width / 2), _height / 2, justify='left')
        self._plr4Name = self.generate_text_layer(_width - (_width / 4), _height / 2, justify='left')

        pass

    def generate_text_layer(self, x=20, y=100, font='small', justify='center', vert_justify='top'):
        return procgame.dmd.HDTextLayer(x, y, self.game.fonts[font], justify, vert_justify)

    def update_layers(self):
        _curr_menu = self._current_menu

        # Blink the selected text frame
        for item in self._blinkingItem:
            if self._selected_frame == item:
                self._blinkingItem[item] = True
            else:
                self._blinkingItem[item] = False

        _height = self.game.dmd.height
        _width = self.game.dmd.width

        if _curr_menu == 0:
            self._title_layer.set_text('Game Title', None, force_update=True)
            self._controls_info_layer.set_text("Flippers change item - Start to select", None)
            self._menu_top_layer.set_text(self._main_menu_items[0][0], None, self._blinkingItem[0], force_update=True)
            self._menu_mid_layer.set_text(self._main_menu_items[1][0], None, self._blinkingItem[1], force_update=True)
            self._menu_bottom_layer.set_text(self._main_menu_items[2][0], None, self._blinkingItem[2],
                                             force_update=True)
            self._menu_top_layer.set_target_position(self.game.dmd.width / 2, _height / 3)

            # Show info for each selected item
            self._info_layer.set_text(self._main_menu_items[self._selected_frame][1])

        elif _curr_menu == 1:
            self._menu_top_layer.set_text('Back', None, self._blinkingItem[0], force_update=True)
            self._menu_top_layer.set_target_position(0 + (_width / 4), (_height / 2) + (_height / 3))
            # self._menu_top_layer.set_target_position(self.game.dmd.width / 2, 2)
            self._plr1.set_text('Player 1', None, force_update=True)
            self._plr2.set_text('Player 2', None, force_update=True)
            self._plr3.set_text('Player 3', None, force_update=True)
            self._plr4.set_text('Player 4', None, force_update=True)
            self._plr1Name.set_text(self._players[1], None, self._blinkingItem[1], force_update=True)
            self._plr2Name.set_text(self._players[2], None, self._blinkingItem[2], force_update=True)
            self._plr3Name.set_text(self._players[3], None, self._blinkingItem[3], force_update=True)
            self._plr4Name.set_text(self._players[4], None, self._blinkingItem[4], force_update=True)
            self._start_game.set_text("Start game", None, self._blinkingItem[5], force_update=True)
            self._info_layer.set_text('')
        elif _curr_menu == 2:
            self._menu_top_layer.set_text('Back', None, self._blinkingItem[0], force_update=True)
            self._menu_mid_layer.set_text('Load', None, self._blinkingItem[1], force_update=True)
            self._menu_bottom_layer.set_text('New', None, self._blinkingItem[2], force_update=True)
            self._start_game.set_text('Remove', None, self._blinkingItem[3], force_update=True)
            self._start_game.set_target_position(_width / 2, (_height / 2) + (_height / 3))
        elif _curr_menu == 3:
            self._menu_top_layer.set_text('Back', None, self._blinkingItem[0], force_update=True)

            self._menu_mid_layer.set_text(self.game.profile_manager.profiles[self._selected_profile - 1].player_name, None,
                                          self._blinkingItem[1], force_update=True)
            self._menu_bottom_layer.set_text('', None, self._blinkingItem[2], force_update=True)
            self._start_game.set_text('', None, self._blinkingItem[3], force_update=True)


        self.game.log("Selected frame {}".format(self._selected_frame))

        if self._last_selected_menu != _curr_menu:
            self.layer = None
            self._last_selected_menu = _curr_menu
            self.layer = self._get_grouped_layers(_curr_menu)

    def _get_grouped_layers(self, menu_number):
        # Main Menu
        if menu_number == 0:
            return procgame.dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
                                             [self.bg_layer, self._title_layer, self._controls_info_layer,
                                              self._info_layer, self._menu_top_layer, self._menu_mid_layer,
                                              self._menu_bottom_layer])
        # Players Menu
        elif menu_number == 1:
            return procgame.dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
                                             [self.bg_layer, self._title_layer, self._controls_info_layer,
                                              self._info_layer, self._menu_top_layer,
                                              self._plr1, self._plr2, self._plr3, self._plr4,
                                              self._plr1Name, self._plr2Name, self._plr3Name, self._plr4Name,
                                              self._start_game])

        elif menu_number == 2 or menu_number == 3:
            return procgame.dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
                                             [self.bg_layer, self._title_layer, self._controls_info_layer,
                                              self._info_layer, self._menu_top_layer, self._menu_mid_layer,
                                              self._menu_bottom_layer, self._start_game])
        # return procgame.dmd.GroupedLayer(self.game.dmd.width, self.game.dmd.height,
        #                                  [self.bg_layer, self._title_layer,
        #                                   self.controlinfoLayer, self.infoText,
        #                                   self._menu_top_layer, self._menu_mid_layer, self._menu_bottom_layer,
        #                                   self.player1, self.player2, self.player3, self.player4,
        #                                   self.playerName1, self.playerName2,
        #                                   self.playerName3, self.playerName4,
        #                                   self.startGame])

    def load_menu(self, menu_number):
        self.game.sound.play('service_enter')
        # Reset the current frame and load menu from incoming number
        #self._selected_frame = 0
        self._current_menu = menu_number
        self.update_layers()
        pass

    def load_entry_mode(self):
        """ Runs the HD Initials Entry mode to get the players name """
        _enter_initials = HD_InitialEntryMode(self.game, self.priority + 1, ["User"], ["Entry"],
                                              self.entry_mode_complete)
        _enter_initials.name = "New Profile"
        self.game.modes.add(_enter_initials)

    def entry_mode_complete(self, mode, inits):
        """ Create a new profile if doesn't already exist """
        self.game.modes.remove(mode)
        self.game.log('Saving name entry profile: {}'.format(inits))
        self._selected_frame = self._selected_player
        print(self.game.profile_manager.profiles)

        # No initials filled or created one called empty, lol, return and don't save
        if not inits or inits.upper() == 'EMPTY':
            self.load_menu(1)
            return

        for player_name in self.profile_manager.profiles:
            if player_name.player_name == inits:
                self.game.log('Profile already exists for {}'.format(inits))
                self.load_menu(1)
                return

        self.game.log('Creating new profile for {}'.format(inits))
        self.game.profile_manager.create(inits)
        self.game.trophy_manager.create(inits)
        self._players[self._selected_player] = inits
        self.load_menu(1)
        pass

    def start_game_add_players(self):
        """ Starts a game and adds all the players that were added in the profile menu list """

        _playerList = [player for player in self._players.itervalues() if not player == "Empty"]

        i = 0
        for player in _playerList:
            """If this is the first entry we have to start game.
                If not just add player because game is ready"""

            if i == 0:
                # Add the first player
                self.game.add_player()
                # Start the ball.  This includes ejecting a ball from the trough.
                self.game.start_ball()
            else:
                self.game.add_player()

            self.game.log("Added player from profile_loader: {}".format(player))
            _profile = [profile for (profile) in self.game.profile_manager.profiles if profile.player_name == player]
            self.game.players[i].name = player
            self.game.players[i].profile = _profile[0]

            if self.game.use_player_trophys:
                _trophy = [trophy for (trophy) in self.game.trophy_manager.trophys if trophy.player_name == player]
                self.game.players[i].trophy = _trophy[0]
            i += 1

        # Set the menu back to the main menu and remove the mode
        self._selected_frame = 0
        self.load_menu(0)

        self.game.modes.remove(self)

    def sw_startButton_active(self, sw):
        if self._current_menu == 0:
            # Quick start
            if self._selected_frame == 0:
                self.game.modes.remove(self)
                # Add the first player
                self.game.add_player()
                # Start the ball.  This includes ejecting a ball from the trough.
                self.game.start_ball()
            # Load players menu number 1
            elif self._selected_frame == 1:
                self.load_menu(1)
            # Back to Attract
            elif self._selected_frame == 2:
                self.game.game_ended()
                self.game.modes.remove(self)
        # Players Menu
        elif self._current_menu == 1:
            # Main Menu
            if self._selected_frame == 0:
                #self.infoListStart = ['Start quick game', 'Select player player profiles', 'Exit to attract mode']
                self.load_menu(0)
            # Start game add players
            elif self._selected_frame == 5:
                self.start_game_add_players()
            # Load profile edit menu
            elif self._selected_frame > 0:
                self._selected_player = self._selected_frame
                self.load_menu(2)
                pass
        elif self._current_menu == 2:
            if self._selected_frame == 0:
                self.load_menu(1)
            # Load profile
            elif self._selected_frame == 1:
                # Load profile selection
                if self.profile_manager.profiles:
                    self.load_menu(3)
                pass
            # New profile - Load HD Entry
            elif self._selected_frame == 2:
                self.load_entry_mode()
            # Remove profile
            elif self._selected_frame == 3:
                self._players[self._selected_player] = "Empty"
                self.load_menu(2)
        elif self._current_menu == 3:
            if self._selected_frame == 0:
                self.load_menu(2)
            elif self._selected_frame == 1:
                self._players[self._selected_player] = self._menu_mid_layer.text
                self.load_menu(1)

        return procgame.game.SwitchStop

    def sw_flipperLwL_active(self, sw):
        self.game.sound.play('service_previous')

        # Main menu
        if self._current_menu == 0:
            if self._selected_frame > 0:
                self._selected_frame -= 1
                self.update_layers()

        # Player selection
        elif self._current_menu == 1:
            if self._selected_frame > 0:
                if self._selected_frame == 5:
                    self._selected_frame = 1
                else:
                    self._selected_frame -= 1

                self.update_layers()
            pass
        elif self._current_menu == 2:
            if 3 >= self._selected_frame > 0:
                self._selected_frame -= 1
                self.update_layers()
            pass
        # Profile selection
        elif self._current_menu == 3:
            if self._selected_frame == 1:
                if self._selected_profile > 0:
                    self._selected_profile -= 1
                else:
                    self._selected_frame = 0
                self.update_layers()

        return procgame.game.SwitchStop

    def sw_flipperLwR_active(self, sw):
        self.game.sound.play('service_next')
        self.game.log("Selected frame {}".format(self._selected_frame))
        # Main menu
        if self._current_menu == 0:
            if self._selected_frame <= 1:
                self._selected_frame += 1
                self.update_layers()
        # Players Menu
        elif self._current_menu == 1:
            if self._selected_frame == 0:
                self._selected_frame += 1
                self.update_layers()
            elif 1 <= self._selected_frame <= 4:
                if self._players[self._selected_frame] != "Empty":
                    self._selected_frame += 1
                else:
                    if self._players[1] != "Empty":
                        self._selected_frame = 5

                self.update_layers()

        elif self._current_menu == 2:
            if self._selected_frame >= 0 and not self._selected_frame > 3:
                self._selected_frame += 1
                self.update_layers()
            pass

        # Profile selection
        elif self._current_menu == 3:
            if self._selected_frame == 0:
                self._selected_frame = 1
            elif self._selected_frame == 1:
                if self._selected_profile < len(self.game.profile_manager.profiles):
                    self._selected_profile += 1
                else:
                    self._selected_profile = 0
                self.update_layers()
        pass

        return procgame.game.SwitchStop
