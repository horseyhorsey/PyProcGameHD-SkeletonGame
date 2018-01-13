__author__ = 'Dave Horsefield'

import copy
from os import path, remove
import yaml


class GameData(object):
    """ Base class for saving game data to files """

    _template = {}
    """ Hold values for the template"""

    template_file = ''
    """ Template file to get default values from  """

    save_dir = ''
    """ Where the data files for a game / player is saved """

    def __init__(self, template_file, save_dir):
        super(GameData, self).__init__()

        self.template_file = template_file
        self.save_dir = save_dir

        self._initialize_template_and_saved_directory()

    def _initialize_template_and_saved_directory(self):
        """ Makes sure directory exists for profiles and loads the template values """
        if not path.exists(self.save_dir):
            raise OSError.NotADirectoryError("Couldn't find profiles directory {}").format(self.save_dir)

        if not path.isfile(self.template_file):
            raise OSError.FileNotFoundError("Profile template file not found {}").format(self.template_file)

        self._template = yaml.load(open(self.template_file, 'r'))

    def _get_template_keys(self, game_data):
        """ Checks the incoming game_data against the loaded template.
            Fixes missing keys in the game_data
         """
        if self._template:
            for key, value in self._template.iteritems():
                if key not in game_data:
                    game_data[key] = copy.deepcopy(value)

            return game_data

    def _load_data_from_file(self, filename):
        """ Loads the data from a given file
            If file data doesn't match template any missing keys are copied over
            If file data doesn't match at all or is representing file data then an empty dict is returned
        """
        _file_data = yaml.load(open(filename, 'r'))

        # If this fails and can't copy keys over from saved file then load an empty one in.
        try:
            _loaded_file_data = self._get_template_keys(_file_data)
        except:
            _loaded_file_data = self._get_template_keys({})
            pass

        return _loaded_file_data

    @staticmethod
    def save_data_to_disk(data, filename):
        """ Removes the file data from disk and writes a new one"""

        GameData._delete_game_data_file(filename)

        # open new stream
        stream = open(filename, 'w')

        # dump the data to file stream
        yaml.dump(data, stream)
        file.close(stream)

    @staticmethod
    def _delete_game_data_file(_filename):
        if path.exists(_filename):
            remove(_filename)


class GameDataItem(object):

    player_name = ''

    player_data = {}

    def __init__(self, name):
        super(GameDataItem, self).__init__()

        self.player_name = name

