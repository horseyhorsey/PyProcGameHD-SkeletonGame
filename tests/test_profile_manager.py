from unittest import TestCase

import os

from procgame.profiles.profile import *
from procgame.profiles.trophy import TrophyManager

__author__ = 'Dave Horsefield'


class TestProfileManager(TestCase):

    _profileManager = None
    _trophyManager = None
    _profileTemplateFile = None
    _profiles_dir = None
    _trophyTemplateFile = None
    _trophys_dir = None

    def setUp(self):
        self._profileTemplateFile = os.getcwd() + '/test_data/config/profile_default_data.yaml'
        self._profiles_dir = os.getcwd() + '/test_data/config/profiles'
        self._trophyTemplateFile = os.getcwd() + '/test_data/config/trophy_default_data.yaml'
        self._trophys_dir = os.getcwd() + '/test_data/config/trophys'
        pass

    def test_populate_profiles_from_directory(self):

        # Init profile manager
        self._profileManager = ProfileManager(self._profileTemplateFile, self._profiles_dir)

        # Populate all the files into profiles
        self._profileManager.populate_profiles_from_directory()

        self.assertTrue(2, len(self._profileManager.profiles))

        print('profile data for {} {}'.format(self._profileManager.profiles[0].player_name,
                                              self._profileManager.profiles[0].player_data))
        print('profile data for {} {}'.format(self._profileManager.profiles[1].player_name,
                                              self._profileManager.profiles[1].player_data))

    def test_populate_trophys_from_directory(self):

        # Init trophy manager
        self._trophyManager = TrophyManager(self._trophyTemplateFile, self._trophys_dir)

        # Populate all the files into trophys
        self._trophyManager.populate_trophy_from_directory()

        self.assertTrue(2, len(self._trophyManager.trophys))

        print('profile data for {} {}'.format(self._trophyManager.trophys[0].player_name,
                                              self._trophyManager.trophys[0].player_data))
        print('profile data for {} {}'.format(self._trophyManager.trophys[1].player_name,
                                              self._trophyManager.trophys[1].player_data))

    def test_trophy_completed(self):

        # Init trophy manager
        self._trophyManager = TrophyManager(self._trophyTemplateFile, self._trophys_dir)

        # Populate all the files into trophys
        self._trophyManager.populate_trophy_from_directory()

        # completed should be true
        _isCompleted = self._trophyManager.trophys[0].is_trophy_completed('Welcome')
        self.assertTrue(_isCompleted, 'Trophy is complete')

        # completed should be false
        _isCompleted = self._trophyManager.trophys[1].is_trophy_completed('Welcome')
        self.assertFalse(_isCompleted, "Trophy isn't complete")

        # completed should be true after setting to it completed
        self._trophyManager.trophys[1].set_completed('Welcome')
        _isCompleted = self._trophyManager.trophys[1].is_trophy_completed('Welcome')
        self.assertTrue(_isCompleted, 'Trophy is complete')
