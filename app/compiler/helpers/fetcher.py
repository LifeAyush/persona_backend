import json
import yaml
import os
from typing import Optional

class Fetcher():
    """
    A class to fetch and parse configuration and schema files.
    
    Attributes:
        source (str): The source name used to locate configuration files.
    """
    
    def __init__(self, source: str):
        """
        Initialize the Fetcher with a source name.
        
        Args:
            source (str): The source name.
            
        Raises:
            ValueError: If source is empty or not a string.
        """
        try:
            if not isinstance(source, str):
                raise ValueError("Source must be a string")
            if not source.strip():
                raise ValueError("Source cannot be empty")
                
            self.source = source
            self.config_base_path = 'app/compiler/configs'
            self.schema_base_path = 'app/compiler/schemas'
            
        except Exception as e:
            raise ValueError(f"Error initializing Fetcher: {str(e)}")

    def _validate_file_path(self, file_path: str) -> None:
        """
        Validates if a file path exists and is accessible.
        
        Args:
            file_path (str): Path to the file to validate.
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file isn't accessible
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"No read permission for file: {file_path}")

    def _read_json_file(self, file_path: str) -> dict:
        """
        Reads and parses a JSON file.
        
        Args:
            file_path (str): Path to the JSON file.
            
        Returns:
            dict: Parsed JSON content.
            
        Raises:
            json.JSONDecodeError: If JSON is invalid
            UnicodeDecodeError: If file encoding is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"Error reading file {file_path}: Invalid encoding - {str(e)}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in file {file_path}: {str(e)}", e.doc, e.pos
            )

    def fetch_config(self) -> Optional[dict]:
        """
        Fetches the configuration for the given source as a YAML object.

        Returns:
            dict: The configuration as a YAML object.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
            yaml.YAMLError: If YAML conversion fails.
            Exception: For other unexpected errors.
        """
        try:
            config_path = os.path.join(self.config_base_path, f'{self.source}.json')
            
            # Validate file path
            self._validate_file_path(config_path)
            
            # Read and parse JSON
            json_config = self._read_json_file(config_path)
            
            # Convert to YAML
            try:
                yaml_config_dump = yaml.dump(json_config, default_flow_style=False)
                yaml_config = yaml.safe_load(yaml_config_dump)
                
                # Validate the loaded config has content
                if not yaml_config:
                    raise ValueError("Configuration file is empty")
                
                return yaml_config
                
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error converting JSON to YAML: {str(e)}")
                
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError) as e:
            raise
        except Exception as e:
            raise Exception(f"Unexpected error fetching config: {str(e)}")

    def fetch_schema(self) -> Optional[dict]:
        """
        Fetches the JSON schema from the specified file.

        Returns:
            dict: The JSON schema object.

        Raises:
            FileNotFoundError: If the schema file is not found.
            json.JSONDecodeError: If the schema file contains invalid JSON.
            Exception: For other unexpected errors.
        """
        try:
            schema_path = os.path.join(self.schema_base_path, 'schema.json')
            
            # Validate file path
            self._validate_file_path(schema_path)
            
            # Read and parse JSON
            schema = self._read_json_file(schema_path)
            
            # Validate schema has content
            if not schema:
                raise ValueError("Schema file is empty")
                
            return schema
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise
        except Exception as e:
            raise Exception(f"Unexpected error fetching schema: {str(e)}")
        
    def fetch_json_validation_schema(self) -> Optional[dict]:
        """
        Fetches the JSON validation schema from the specified file.

        Returns:
            dict: The JSON validation schema object.

        Raises:
            FileNotFoundError: If the schema file is not found.
            json.JSONDecodeError: If the schema file contains invalid JSON.
            Exception: For other unexpected errors.
        """
        try:
            validation_schema_path = os.path.join(self.schema_base_path, 'json_validation_schema.json')
            
            # Validate file path
            self._validate_file_path(validation_schema_path)
            
            # Read and parse JSON
            validation_schema = self._read_json_file(validation_schema_path)
            
            # Validate schema has content
            if not validation_schema:
                raise ValueError("Validation schema file is empty")
                
            return validation_schema
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise
        except Exception as e:
            raise Exception(f"Unexpected error fetching validation schema: {str(e)}")
