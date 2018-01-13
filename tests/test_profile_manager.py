from unittest import TestCase

import os

from procgame.profiles.profile import *

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

