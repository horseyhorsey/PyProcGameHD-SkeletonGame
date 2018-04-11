from os import listdir, path
from procgame.profiles import gamedata
import time

__author__ = 'Dave Horsefield'


class Trophy(gamedata.GameDataItem):

    def __init__(self, name):
        super(Trophy, self).__init__(name)

    def save(self, save_dir):
        """ Saves the profile to disk """
        TrophyManager.save_data_to_disk(self.player_data, path.join(save_dir, self.player_name + '.yaml'))

    def is_trophy_completed(self, key):
        """ Returns whether a trophy is completed """

        # Check first to see if there is data loaded for the trophy
        if bool(self.player_data):
            if not self.player_data['Trophys'][key]['completedDate']:
                return False
            else:
                return True

    def set_completed(self, key):
        """ adds the current datetime to the complete date"""
        if bool(self.player_data):
            self.player_data['Trophys'][key]['completedDate'] = time.asctime()


class TrophyManager(gamedata.GameData):

    trophys = []

    def __init__(self, template_file, saved_profiles_dir):
        super(TrophyManager, self).__init__(template_file, saved_profiles_dir)

    def create(self, name):
        """ Creates a trophy file for the player """
        _empty_data = self._get_template_keys({})
        trophy = Trophy(name)
        trophy.player_data = _empty_data
        self.save_data_to_disk(trophy.player_data, path.join(self.save_dir, trophy.player_name + '.yaml'))
        self.trophys.append(trophy)

    def populate_trophy_from_directory(self):
        """ Clears current list and loads all trophy's found on disk into the local trophys list """

        self.trophys = []

        # Go over all the files and create a profile object
        _trophy_files = listdir(self.save_dir)

        for trophy_filename in _trophy_files:
            # Only check for .yaml files
            if path.splitext(trophy_filename)[1] == '.yaml':
                # Get the data and create a new trophy
                _file_data = self._load_data_from_file(path.join(self.save_dir, trophy_filename))
                _trophy = Trophy(path.splitext(trophy_filename)[0])
                _trophy.player_data = _file_data
                self.trophys.append(_trophy)
