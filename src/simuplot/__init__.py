import os

# Define paths
BASE_PATH = os.path.dirname(os.path.dirname(__file__))
UI_PATH = os.path.join(BASE_PATH, 'resources/ui')
I18N_PATH = os.path.join(BASE_PATH, 'i18n/ts')


class SimuplotError(Exception):
    """Base Exception class for all Exceptions in the project"""
