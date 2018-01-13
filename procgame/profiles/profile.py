__author__ = 'Dave Horsefield'

from os import path, listdir, remove
import yaml
import copy


class Profile(object):
    """ Game data for a player"""

    player_name = ''

    player_data = {}

    def __init__(self, name):
        super(Profile, self).__init__()

        self.player_name = name


class ProfileManager(object):
    """ Manages profiles"""

    _template = {}
    """ Hold values for the template"""

    profiles = []
    """ A list of all profiles for the game """

    template_file = ''
    """ Template file to get default values from  """

    saved_profiles_dir = ''
    """ Where the user profiles are saved """

    def __init__(self, template_file, saved_profiles_dir):
        super(ProfileManager, self).__init__()

        self.template_file = template_file
        self.saved_profiles_dir = saved_profiles_dir

        self._initialize_template_and_saved_directory()

    def _initialize_template_and_saved_directory(self):
        """ Makes sure directory exists for profiles and loads the template values """
        if not path.exists(self.saved_profiles_dir):
            raise OSError.NotADirectoryError("Couldn't find profiles directory {}").format(self.saved_profiles_dir)

        if not path.isfile(self.template_file):
            raise OSError.FileNotFoundError("Profile template file not found {}").format(self.template_file)

        self._template = yaml.load(open(self.template_file, 'r'))

    def _get_template_keys(self, profile_data):
        """ Gets template keys and if any keys are missing adds them from the template into the players profile """
        if self._template:
            for key, value in self._template.iteritems():
                if key not in profile_data:
                    profile_data[key] = copy.deepcopy(value)

            return profile_data

    @staticmethod
    def save_profile_to_disk(profile):
        """ Removes the profile file from disk and writes a new one from the given profiles data"""

        _filename = ProfileManager._get_profile_filename(profile)
        ProfileManager._delete_profile(_filename)

        # open new stream
        stream = open(_filename, 'w')

        # dump the data to file stream
        yaml.dump(profile.player_data, stream)
        file.close(stream)

    def remove_saved_profile(self, profile):
        """ Removes a saved profile from the list and from disk"""
        self.profiles.remove(profile)
        ProfileManager._delete_profile(ProfileManager._get_profile_filename(profile))

    @staticmethod
    def _get_profile_filename(profile):
        return profile.player_name + '.yaml'

    @staticmethod
    def _delete_profile(_filename):
        if path.exists(_filename):
            remove(_filename)

    def _load_profile(self, profile_name, profile_file):
        """ private method for loading a profile """

        _profile = yaml.load(open(profile_file, 'r'))

        # If this fails and can't copy keys over from saved file then load an empty one in.
        try:
            _loaded_profile_data = self._get_template_keys(_profile)
        except:
            _loaded_profile_data = self._get_template_keys({})
            pass

        loaded_profile = Profile(profile_name)
        loaded_profile.player_data = _loaded_profile_data

        return loaded_profile

    def load_template_values(self, profile_template):
        pass

    def populate_profiles_from_directory(self):
        """ Clears current list and loads all profiles found on disk into the local profiles list """

        self.profiles = []

        # Go over all the files and create a profile object
        _profile_files = listdir(self.saved_profiles_dir)

        for profile_filename in _profile_files:
            if path.splitext(profile_filename)[1] == '.yaml':
                self.profiles.append(self._load_profile(profile_filename,
                                                        path.join(self.saved_profiles_dir, profile_filename)))



