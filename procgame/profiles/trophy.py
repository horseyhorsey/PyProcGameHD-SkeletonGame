from os import listdir, path

__author__ = 'Dave Horsefield'

from procgame.profiles import gamedata


class Trophy(gamedata.GameDataItem):

    def __init__(self, name):
        super(Trophy, self).__init__(name)


class TrophyManager(gamedata.GameData):

    trophys = []

    def __init__(self, template_file, saved_profiles_dir):
        super(TrophyManager, self).__init__(template_file, saved_profiles_dir)

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
                _trophy = Trophy(trophy_filename[0])
                _trophy.player_data = _file_data
                self.trophys.append(_trophy)
