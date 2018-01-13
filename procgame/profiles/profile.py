__author__ = 'Dave Horsefield'

from procgame.profiles import gamedata
from os import path, listdir


class Profile(gamedata.GameDataItem):
    """ Game data for a player"""

    def __init__(self, name):
        super(Profile, self).__init__(name)


class ProfileManager(gamedata.GameData):
    """ Manages profiles"""

    profiles = []
    """ A list of all profiles for the game """

    def __init__(self, template_file, saved_profiles_dir):
        super(ProfileManager, self).__init__(template_file, saved_profiles_dir)

    def populate_profiles_from_directory(self):
        """ Clears current list and loads all profiles found on disk into the local profiles list """

        self.profiles = []

        # Go over all the files and create a profile object
        _profile_files = listdir(self.save_dir)

        for profile_filename in _profile_files:
            # Only check for .yaml files
            if path.splitext(profile_filename)[1] == '.yaml':
                # Get the data and create a new profile
                _file_data = self._load_data_from_file(path.join(self.save_dir, profile_filename))
                _profile = Profile(path.splitext(profile_filename)[0])
                _profile.player_data = _file_data
                self.profiles.append(_profile)

    def remove_saved_profile(self, profile):
        """ Removes a saved profile from the list and deletes from disk"""

        self.profiles.remove(profile)
        gamedata.GameData._delete_game_data_file(path.join(self.save_dir, profile.player_name + '.yaml'))



