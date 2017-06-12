"""
    Testing the crawl.py script
"""
import os
import pytest
import crawl

from importlib import reload

JAHIA_HOST = "https://fake-jahia.epfl.ch"
JAHIA_ROOT_USER = "root"
JAHIA_ROOT_PASSWORD = "FAKE"


@pytest.fixture()
def environment(request):
    """
    Load fake environment variables for every test
    """
    os.environ["JAHIA_ROOT_PASSWORD"] = JAHIA_ROOT_PASSWORD
    os.environ["JAHIA_ROOT_USER"] = JAHIA_ROOT_USER
    os.environ["JAHIA_HOST"] = JAHIA_HOST
    reload(crawl)
    return os.environ


def delete_environment():
    """
        Delete all env. vars
    """
    del os.environ["JAHIA_ROOT_PASSWORD"]
    del os.environ["JAHIA_ROOT_USER"]
    del os.environ["JAHIA_HOST"]


class TestSetup:

    def test_required_env_password(self, environment):
        """
            Delete all env. vars and check that module raise an exception on load
        """
        delete_environment()
        with pytest.raises(SystemExit):
            reload(crawl)

    def test_default_env(self, environment):
        """
            Check default values for JAHIA _USER and _HOST
        """
        delete_environment()
        os.environ["JAHIA_ROOT_PASSWORD"] = "TEST"
        reload(crawl)
        assert crawl.HOST == 'localhost'
        assert crawl.ID_POST_PARAMS == {
            'login_username': 'root',
            'login_password': "TEST",
        }

    def test_loaded_env(self, environment):
        # values have been set in os.environ by fixture
        assert crawl.HOST == JAHIA_HOST
        assert crawl.ID_POST_PARAMS == {
            'login_username': JAHIA_ROOT_USER,
            'login_password': JAHIA_ROOT_PASSWORD,
        }
