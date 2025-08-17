"""
Configuration module for Guardian Seven Best Shows Monitor.
Loads configuration from config.ini file and secrets from .env file.
"""

import os
import configparser
from pathlib import Path
from dotenv import load_dotenv
import logging
from datetime import datetime

class Config:
    """Configuration class that loads settings from config.ini and secrets from .env."""
    
    def __init__(self, config_path: str = None, env_path: str = None):
        """
        Initialize configuration by loading from config files.
        
        Args:
            config_path: Path to config.ini file. Defaults to project root.
            env_path: Path to .env file. Defaults to project root.
        """
        self.project_root = Path(__file__).parent.parent
        
        # Load environment variables (secrets)
        self._load_env_file(env_path)
        
        # Load configuration from INI file
        self._load_config_file(config_path)
        
        # Validate configuration
        self._validate_config()
    
    def _load_env_file(self, env_path: str = None):
        """Load environment variables from .env file."""
        if env_path:
            load_dotenv(env_path)
        else:
            env_file = self.project_root / '.env'
            if env_file.exists():
                load_dotenv(env_file)
            else:
                load_dotenv()  # Load from system environment
        
        # Load secrets from environment
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    def _load_config_file(self, config_path: str = None):
        """Load configuration from INI file."""
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self.project_root / 'config.ini'
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Guardian Configuration
        guardian_section = config['guardian']
        self.guardian_series_url = guardian_section.get('series_url')
        self.guardian_base_url = guardian_section.get('base_url')
        
        # Application Settings
        app_section = config['application']
        self.send_error_notifications = app_section.getboolean('send_error_notifications')
        
        # Storage Settings
        storage_section = config['storage']
        self.data_directory = storage_section.get('data_directory')
        
        # HTTP Settings
        http_section = config['http']
        self.request_timeout = http_section.getint('request_timeout')
        self.user_agent = http_section.get('user_agent')
        self.retry_attempts = http_section.getint('retry_attempts')
        self.retry_delay = http_section.getint('retry_delay')
        
        # Logging Settings
        logging_section = config['logging']
        self.log_level = logging_section.get('log_level').upper()
        self.log_to_file = logging_section.getboolean('log_to_file')
        self.log_file = logging_section.get('log_file')
    
    def _validate_config(self):
        """Validate configuration values."""
        # Check required settings
        if not self.discord_webhook_url:
            logging.warning("DISCORD_WEBHOOK_URL not configured - Discord notifications will be disabled")
        
        # Validate numeric values
        if self.request_timeout < 1:
            self.request_timeout = 10
            logging.warning("REQUEST_TIMEOUT must be at least 1 second, using default of 10")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            self.log_level = 'INFO'
            logging.warning(f"Invalid LOG_LEVEL, using default 'INFO'")
        
        # Validate URLs
        if not self.guardian_series_url.startswith('http'):
            raise ValueError(f"Invalid guardian series URL: {self.guardian_series_url}")
        
        if not self.guardian_base_url.startswith('http'):
            raise ValueError(f"Invalid guardian base URL: {self.guardian_base_url}")
    
    def setup_logging(self):
        """Setup logging based on configuration."""
        # Convert log level string to logging constant
        log_level = getattr(logging, self.log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)
        
        # Setup file handler if enabled
        if self.log_to_file:
            try:
                # Create logs directory if it doesn't exist
                log_path = Path(self.log_file)
                if not log_path.is_absolute():
                    log_path = self.project_root / self.log_file
                
                log_dir = log_path.parent
                log_dir.mkdir(parents=True, exist_ok=True)
                
                # Create timestamped log file for this run
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                timestamped_log = log_dir / f"guardian_monitor_{timestamp}.log"
                
                file_handler = logging.FileHandler(timestamped_log)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                
                logging.info(f"Logging to file: {timestamped_log}")
                
                # Clean up old log files (keep only 10 most recent)
                self._cleanup_old_logs(log_dir)
                
            except Exception as e:
                logging.error(f"Failed to setup file logging: {e}")
    
    def _cleanup_old_logs(self, log_dir: Path, max_logs: int = 10):
        """Clean up old log files, keeping only the most recent ones."""
        try:
            # Get all Guardian monitor log files
            log_pattern = "guardian_monitor_*.log"
            log_files = list(log_dir.glob(log_pattern))
            
            if len(log_files) <= max_logs:
                return  # No cleanup needed
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Keep only the most recent max_logs files
            files_to_keep = log_files[:max_logs]
            files_to_delete = log_files[max_logs:]
            
            # Delete old log files
            deleted_count = 0
            for log_file in files_to_delete:
                try:
                    log_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logging.warning(f"Failed to delete old log {log_file.name}: {e}")
            
            if deleted_count > 0:
                logging.info(f"Cleaned up {deleted_count} old log files, kept {len(files_to_keep)} most recent")
                
        except Exception as e:
            logging.warning(f"Error during log cleanup: {e}")
    
    def get_data_directory_path(self) -> Path:
        """
        Get the full path to the data directory.
        
        Returns:
            Path object for data directory
        """
        if os.path.isabs(self.data_directory):
            return Path(self.data_directory)
        else:
            # Relative to project root
            return self.project_root / self.data_directory
    
    def is_discord_configured(self) -> bool:
        """
        Check if Discord is properly configured.
        
        Returns:
            True if Discord webhook URL is available
        """
        return bool(self.discord_webhook_url)
    
    def get_summary(self) -> dict:
        """
        Get configuration summary for logging/debugging.
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            'discord_configured': self.is_discord_configured(),
            'guardian_series_url': self.guardian_series_url,
            'send_error_notifications': self.send_error_notifications,
            'data_directory': str(self.get_data_directory_path()),
            'log_level': self.log_level,
            'log_to_file': self.log_to_file,
            'request_timeout': self.request_timeout,
            'retry_attempts': self.retry_attempts
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        summary = self.get_summary()
        lines = ['Guardian Seven Best Shows Monitor Configuration:']
        
        # Group related settings
        lines.append('  Discord:')
        lines.append(f'    configured: {summary["discord_configured"]}')
        
        lines.append('  Guardian:')
        lines.append(f'    series_url: {summary["guardian_series_url"]}')
        
        lines.append('  Application:')
        lines.append(f'    send_error_notifications: {summary["send_error_notifications"]}')
        
        lines.append('  Storage:')
        lines.append(f'    data_directory: {summary["data_directory"]}')
        
        lines.append('  HTTP:')
        lines.append(f'    request_timeout: {summary["request_timeout"]} seconds')
        lines.append(f'    retry_attempts: {summary["retry_attempts"]}')
        
        lines.append('  Logging:')
        lines.append(f'    log_level: {summary["log_level"]}')
        lines.append(f'    log_to_file: {summary["log_to_file"]}')
        
        return '\n'.join(lines)


# Global configuration instance
config = Config()


def main():
    """Test configuration loading."""
    print("🔧 Testing Configuration Loading")
    print("=" * 40)
    
    try:
        # Setup logging
        config.setup_logging()
        
        # Print configuration summary
        print(config)
        
        # Test specific settings
        print(f"\nDiscord configured: {config.is_discord_configured()}")
        print(f"Data directory: {config.get_data_directory_path()}")
        print(f"Guardian series URL: {config.guardian_series_url}")
        print(f"Send error notifications: {config.send_error_notifications}")
        
        if config.is_discord_configured():
            print("✅ Discord webhook is configured")
        else:
            print("⚠️  Discord webhook not configured - notifications will be disabled")
            
        print("✅ Configuration loaded successfully from config.ini and .env")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        raise


if __name__ == "__main__":
    main()
