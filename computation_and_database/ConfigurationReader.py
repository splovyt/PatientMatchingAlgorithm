import yaml


class ConfigurationReader:
    """
    Provide the configuration values to the rest of the application.
    For each value there will simply be a method to retrieve it.
    """
    __CONFIG_FILE_NAME = 'config.yaml'

    def __init__(self):
        with open(self.__CONFIG_FILE_NAME, 'r') as config_file:
            self.__config_contents = yaml.load(config_file)

    @property
    def initial_number_of_patients_per_page(self):
        return self.__config_contents["initial_number_of_patients_per_page"]

    @property
    def base_url(self):
        return self.__config_contents["base_url"]

    @property
    def port_number(self):
        return self.__config_contents["port_number"]