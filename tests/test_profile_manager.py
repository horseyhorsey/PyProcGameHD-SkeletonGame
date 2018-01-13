from unittest import TestCase

import os

from procgame.profiles.profile import *
from procgame.profiles.trophy import TrophyManager

__author__ = 'Dave Horsefield'


class TestProfileManager(TestCase):
    def test_populate_profiles_from_directory(self):
        _templateFile = os.getcwd() + '/test_data/config/profile_default_data.yaml'
        _profiles_dir = os.getcwd() + '/test_data/config/profiles'

        # Init profile manager
        _profileManager = ProfileManager(_templateFile, _profiles_dir)

        # Populate all the files into profiles
        _profileManager.populate_profiles_from_directory()

        self.assertTrue(2, len(_profileManager.profiles))

        print('profile data for {} {}'.format(_profileManager.profiles[0].player_name,
                                              _profileManager.profiles[0].player_data))
        print('profile data for {} {}'.format(_profileManager.profiles[1].player_name,
                                              _profileManager.profiles[1].player_data))

    def test_populate_trophys_from_directory(self):
        _templateFile = os.getcwd() + '/test_data/config/trophy_default_data.yaml'
        _trophys_dir = os.getcwd() + '/test_data/config/trophys'

        # Init trophy manager
        _trophyManager = TrophyManager(_templateFile, _trophys_dir)

        # Populate all the files into trophys
        _trophyManager.populate_trophy_from_directory()

        self.assertTrue(2, len(_trophyManager.trophys))

        print('profile data for {} {}'.format(_trophyManager.trophys[0].player_name,
                                              _trophyManager.trophys[0].player_data))
        print('profile data for {} {}'.format(_trophyManager.trophys[1].player_name,
                                              _trophyManager.trophys[1].player_data))

