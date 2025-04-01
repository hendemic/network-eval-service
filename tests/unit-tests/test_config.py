import unittest
import os
import sys
import importlib
from unittest import mock

# Add the main project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestConfigModule(unittest.TestCase):
    """Test the configuration module."""
    
    def test_config_dictionary(self):
        """Test that the config dictionary contains expected environments."""
        # Import the config module
        from backend.config import config, DevelopmentConfig
        
        self.assertIn('development', config)
        self.assertIn('production', config)
        self.assertIn('testing', config)
        self.assertIn('default', config)
        
        # Default should be development
        self.assertEqual(config['default'], DevelopmentConfig)
    
    def test_environment_configs(self):
        """Test that each environment config has the expected attributes."""
        # Import the config module
        from backend.config import config
        
        # Test development config
        self.assertTrue(config['development'].DEBUG)
        
        # Test production config
        self.assertFalse(config['production'].DEBUG)
        
        # Test testing config
        self.assertTrue(config['testing'].DEBUG)
        self.assertTrue(config['testing'].TESTING)
        self.assertEqual(config['testing'].SQLALCHEMY_DATABASE_URI, 'sqlite:///:memory:')
        self.assertEqual(config['testing'].SQLALCHEMY_ENGINE_OPTIONS, {})
    
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_default_values(self):
        """Test that default values are used when environment variables are missing."""
        # Reload the config module with empty environment
        importlib.reload(sys.modules['backend.config'])
        from backend.config import Config
        
        # Check default values
        self.assertEqual(Config.POSTGRES_USER, 'postgres')
        self.assertEqual(Config.POSTGRES_PASSWORD, 'postgres')
        self.assertEqual(Config.POSTGRES_HOST, 'localhost')
        self.assertEqual(Config.POSTGRES_PORT, '5432')
        self.assertEqual(Config.POSTGRES_DB, 'network_tests')
        self.assertEqual(Config.POSTGRES_SCHEMA, 'network_eval')
        
        # Check derived values
        expected_uri = f'postgresql://postgres:postgres@localhost:5432/network_tests'
        self.assertEqual(Config.SQLALCHEMY_DATABASE_URI, expected_uri)
        
        # App settings
        self.assertFalse(Config.DEBUG)
        self.assertEqual(Config.SECRET_KEY, 'dev-key-change-in-production')
        
        # Test settings
        self.assertEqual(Config.TEST_TARGET, '1.1.1.1')
        self.assertEqual(Config.TEST_COUNT, 100)
        self.assertEqual(Config.PING_INTERVAL, '0.1')
        self.assertEqual(Config.TEST_INTERVAL, '60')
    
    @mock.patch.dict(os.environ, {
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_password',
        'POSTGRES_HOST': 'test_host',
        'POSTGRES_PORT': '5433',
        'POSTGRES_DB': 'test_db',
        'POSTGRES_SCHEMA': 'test_schema',
        'DEBUG': 'true',
        'SECRET_KEY': 'test_key',
        'TEST_TARGET': '8.8.8.8',
        'TEST_COUNT': '200',
        'PING_INTERVAL': '0.5',
        'TEST_INTERVAL': '120'
    })
    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        # Reload the config module with mock environment
        importlib.reload(sys.modules['backend.config'])
        from backend.config import Config
        
        # Check environment-provided values
        self.assertEqual(Config.POSTGRES_USER, 'test_user')
        self.assertEqual(Config.POSTGRES_PASSWORD, 'test_password')
        self.assertEqual(Config.POSTGRES_HOST, 'test_host')
        self.assertEqual(Config.POSTGRES_PORT, '5433')
        self.assertEqual(Config.POSTGRES_DB, 'test_db')
        self.assertEqual(Config.POSTGRES_SCHEMA, 'test_schema')
        
        # Check derived values
        expected_uri = f'postgresql://test_user:test_password@test_host:5433/test_db'
        self.assertEqual(Config.SQLALCHEMY_DATABASE_URI, expected_uri)
        
        # App settings
        self.assertTrue(Config.DEBUG)
        self.assertEqual(Config.SECRET_KEY, 'test_key')
        
        # Test settings
        self.assertEqual(Config.TEST_TARGET, '8.8.8.8')
        self.assertEqual(Config.TEST_COUNT, 200)
        self.assertEqual(Config.PING_INTERVAL, '0.5')
        self.assertEqual(Config.TEST_INTERVAL, '120')
    
    def test_debug_flag_parsing(self):
        """Test that the DEBUG flag is correctly parsed from string to boolean."""
        # Test with 'true' (should be True)
        with mock.patch.dict(os.environ, {'DEBUG': 'true'}):
            importlib.reload(sys.modules['backend.config'])
            from backend.config import Config
            self.assertTrue(Config.DEBUG)
        
        # Test with 'True' (should be True, case insensitive)
        with mock.patch.dict(os.environ, {'DEBUG': 'True'}):
            importlib.reload(sys.modules['backend.config'])
            from backend.config import Config
            self.assertTrue(Config.DEBUG)
        
        # Test with 'false' (should be False)
        with mock.patch.dict(os.environ, {'DEBUG': 'false'}):
            importlib.reload(sys.modules['backend.config'])
            from backend.config import Config
            self.assertFalse(Config.DEBUG)
        
        # Test with invalid value (should default to False)
        with mock.patch.dict(os.environ, {'DEBUG': 'invalid'}):
            importlib.reload(sys.modules['backend.config'])
            from backend.config import Config
            self.assertFalse(Config.DEBUG)

if __name__ == '__main__':
    unittest.main()