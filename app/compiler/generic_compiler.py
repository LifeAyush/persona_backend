import yaml
import logging
from typing import Optional, Any, Tuple, Union
from dataclasses import dataclass
from .helpers import JsonDataExtractor, Fetcher, SanitizerHandler

@dataclass
class CompilerResponse:
    """Data class to hold compiler response"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_type: Optional[str] = None

class GenericCompiler:
    """
    A generic compiler class that handles data extraction, validation, and compilation.
    
    Attributes:
        source (str): Source identifier for the data
        raw_data (dict): Raw data to be compiled
        fetcher (Fetcher): Instance of Fetcher class
        json_data_extractor (JsonDataExtractor): Instance of JsonDataExtractor class
        sanitizer_handler (SanitizerHandler): Instance of SanitizerHandler class
    """

    def __init__(self, source: str, raw_data: dict):
        """
        Initialize the GenericCompiler.

        Args:
            source (str): Source identifier
            raw_data (dict): Raw data to process

        Raises:
            ValueError: If inputs are invalid
            TypeError: If inputs are of wrong type
        """
        try:
            # Validate inputs
            if not isinstance(source, str):
                raise TypeError(f"Source must be a string, got {type(source)}")
            if not source.strip():
                raise ValueError("Source cannot be empty")
            
            if not isinstance(raw_data, dict):
                raise TypeError(f"Raw data must be a dictionary, got {type(raw_data)}")
            if not raw_data:
                raise ValueError("Raw data cannot be empty")

            # Initialize attributes
            self.source: str = source
            self.raw_data: dict = raw_data
            self.logger = logging.getLogger(__name__)
            
            # Initialize components
            try:
                self.fetcher: Fetcher = Fetcher(self.source)
                self.json_data_extractor: JsonDataExtractor = JsonDataExtractor()
                self.sanitizer_handler: SanitizerHandler = SanitizerHandler(self.source)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize components: {str(e)}")
            
            # Initialize state variables
            self.config: Optional[dict] = None
            self.schema: Optional[dict] = None
            self.validation_schema: Optional[dict] = None
            self.extracted_data: Optional[dict] = None

        except Exception as e:
            self.logger.error(f"Error initializing GenericCompiler: {str(e)}")
            raise

    def _fetch_configurations(self) -> CompilerResponse:
        """
        Fetch all required configurations.

        Returns:
            CompilerResponse: Result of fetching configurations
        """
        try:
            self.config = self.fetcher.fetch_config()
            if not self.config:
                return CompilerResponse(
                    success=False,
                    error="Failed to fetch configuration",
                    error_type="ConfigurationError"
                )

            self.schema = self.fetcher.fetch_schema()
            if not self.schema:
                return CompilerResponse(
                    success=False,
                    error="Failed to fetch schema",
                    error_type="SchemaError"
                )

            self.validation_schema = self.fetcher.fetch_json_validation_schema()
            if not self.validation_schema:
                return CompilerResponse(
                    success=False,
                    error="Failed to fetch validation schema",
                    error_type="ValidationSchemaError"
                )

            return CompilerResponse(success=True)

        except Exception as e:
            self.logger.error(f"Error fetching configurations: {str(e)}")
            return CompilerResponse(
                success=False,
                error=str(e),
                error_type=type(e).__name__
            )

    def _handle_schema_overrides(self, serviceable: bool) -> CompilerResponse:
        """
        Handle schema overrides if service is available.

        Args:
            serviceable (bool): Whether service is available

        Returns:
            CompilerResponse: Result of handling schema overrides
        """
        try:
            if not serviceable:
                return CompilerResponse(success=True)

            schema_overrides = self.json_data_extractor.extract_schema_overrides(
                raw_data=self.raw_data,
                yaml_data=self.config
            )

            for key, type_info in schema_overrides.items():
                try:
                    if not isinstance(type_info, dict) or 'type' not in type_info:
                        raise ValueError(f"Invalid type information for key {key}")

                    self.schema[key] = "string"
                    self.validation_schema["properties"][key] = {
                        "type": [type_info["type"], "null"]
                    }
                    self.logger.info(f"Schema override applied for {key} with type {type_info['type']}")
                except Exception as e:
                    self.logger.error(f"Error processing schema override for key {key}: {str(e)}")
                    continue

            return CompilerResponse(success=True)

        except Exception as e:
            self.logger.error(f"Error handling schema overrides: {str(e)}")
            return CompilerResponse(
                success=False,
                error=str(e),
                error_type=type(e).__name__
            )

    def compile_data(self) -> Optional[Union[Tuple[dict, ...], None]]:
        """
        Compile the raw data using the configured extractors and handlers.

        Returns:
            Optional[Union[Tuple[dict, ...], None]]: Compiled data if successful, None otherwise

        Raises:
            Exception: For unexpected errors during compilation
        """
        try:
            # Fetch configurations
            config_response = self._fetch_configurations()
            if not config_response.success:
                self.logger.error(f"Configuration error: {config_response.error}")
                return None

            # Extract serviceable status
            try:
                serviceable = self.json_data_extractor.extract_serviceable(
                    raw_data=self.raw_data,
                    yaml_data=self.config
                )
            except Exception as e:
                self.logger.error(f"Error extracting serviceable status: {str(e)}")
                return None

            if serviceable is False:
                self.logger.warning(f"Serviceable status is False for source: {self.source}")
                return None

            # Extract data
            try:
                self.extracted_data, message = self.json_data_extractor.extract_data(
                    raw_data=self.raw_data,
                    yaml_data=self.config,
                    is_serviceable=serviceable,
                )
            except Exception as e:
                self.logger.error(f"Error during data extraction: {str(e)}")
                return None

            if not self.extracted_data:
                self.logger.error(f"Data extraction failed: {message}")
                return None

            # Handle schema overrides
            override_response = self._handle_schema_overrides(serviceable)
            if not override_response.success:
                self.logger.error(f"Schema override error: {override_response.error}")
                return None

            # Process data through sanitizer
            try:
                parser_response = self.sanitizer_handler.process_data(
                    extracted_data=self.extracted_data,
                    yaml_data=self.config,
                    schema=self.schema,
                    validation_schema=self.validation_schema,
                    is_serviceable=serviceable,
                )
            except Exception as e:
                self.logger.error(f"Error during data processing: {str(e)}")
                return None

            if not parser_response.get("error"):
                return parser_response.get("compiled_data")
            else:
                self.logger.error(f"Compilation error: {parser_response.error_message}")
                return None

        except Exception as e:
            self.logger.error(f"Unexpected error during compilation: {str(e)}")
            raise