import jsonschema, importlib.util, re, traceback
from typing import Any, Dict, Optional
from .utils import Utils

class SanitizerHandler:
    def __init__(self, source: str):
        """
        Initialize the SanitizerHandler class.

        Args:
            source (str): The source name for the sanitizer handler.
        """
        self.source = source
        self.utils = Utils()

    def regex_handler(self, working_string: str, regex_string: str) -> Optional[str]:
        """
        Applies a regex string to a working string and returns the matched string.

        Args:
            working_string (str): The string to apply the regex to.
            regex_string (str): The regex string to apply.

        Returns:
            Optional[str]: The matched string, or None if no match was found.
        """
        try:
            matches = re.search(regex_string, working_string)
            if matches:
                print(f"Final string after regex: {matches[0]} for string {working_string}")
                return matches[0]
            return None
        except Exception as e:
            print(f"Error in regex_handler: {str(e)}")
            return None

    def conversion_handler(self, working_string: str, conversion_type: str) -> Optional[str]:
        """
        Converts a given numeric string from one unit to another based on the specified conversion type.

        Args:
            working_string (str): The numeric string to convert.
            conversion_type (str): The type of conversion to perform. Supported types include 'time' (from minutes to seconds) and 'distance' (from miles to kilometers).

        Returns:
            Optional[str]: The converted value as a string, or None if the conversion type is unsupported or the input is invalid.
        """
        try:
            conversion_map = {
                "time": {"from": "minutes", "to": "seconds", "factor": 60},
                "distance": {"from": "mile", "to": "km", "factor": 1.60934},
            }
            if conversion_type not in conversion_map:
                print(f"Unsupported conversion type: {conversion_type}")
                return None

            conversion_config = conversion_map[conversion_type]
            try:
                numeric_value = float(working_string)
            except ValueError:
                print(f"Invalid numeric value in working_string: {working_string}")
                return None

            converted_value = numeric_value * conversion_config["factor"]
            return str(converted_value)
        except Exception as e:
            print(f"Error in conversion_handler: {str(e)}")
            return None

    def handle_santisation(
        self, 
        index: int, 
        value: Any, 
        sanitizer_module: object, 
        yaml_data: Dict,
        processed_values: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """
        Applies the specified sanitizers to the given value and returns the sanitized result.

        Args:
            index (int): The index of the current field being processed in the yaml_data.
            value (Any): The value to be sanitized.
            sanitizer_module (object): The module containing the sanitizer functions.
            yaml_data (Dict): The configuration data from the yaml file.
            processed_values (Optional[Dict], optional): A dictionary containing the processed values of the fields. Defaults to None.
            **kwargs: Additional keyword arguments passed to the sanitizer functions.

        Returns:
            Any: The sanitized value.
        """
        try:
            object = yaml_data["to_extract"][index]
            if "sanitizer" not in object:
                print(f"No sanitizer found for {object['key_name']}")
                return value

            sanitizer = object["sanitizer"]
            for key, config in sanitizer.items():
                try:
                    if key == "regex":
                        value = self.regex_handler(value, config)
                    elif key == 'extract_key':
                        if isinstance(value, dict):
                            value = value.get(config, None)
                    elif key == "function":
                        if not hasattr(sanitizer_module, config):
                            print(f"Function '{config}' not found in module")
                            continue
                            
                        target_function = getattr(sanitizer_module, config)
                        if "dependencies" in sanitizer:
                            required_values = {}
                            missing_deps = []
                            for dep in sanitizer["dependencies"]:
                                if processed_values and dep in processed_values:
                                    required_values[dep] = processed_values[dep]
                                else:
                                    missing_deps.append(dep)
                                    required_values[dep] = None
                                    
                            if missing_deps:
                                print(f"Missing dependencies for {object['key_name']}: {missing_deps}")
                            
                            try:
                                print(f"Passing {value} and {required_values} into sanitizer function {config}")
                                value = target_function(value, object['key_name'], **required_values)
                                print(f"Result of function {config}: {value}")
                            except Exception as e:
                                print(f"Error in sanitizer function '{config}': {str(e)}")
                                fall_back_value = kwargs.get('fallback_value', value)
                                if fall_back_value:
                                    print(f'Fallback value for {object["key_name"]}: {fall_back_value}')
                                    value = target_function(fall_back_value, object['key_name'], **required_values)
                        else:
                            try:
                                print(f"Passing {value} into sanitizer function {config}")
                                value = target_function(value)
                                print(f"Result of function {config}: {value}")
                            except Exception as e:
                                print(f"Error in sanitizer function '{config}': {str(e)}")
                                return None
                    elif key == "conversion":
                        for conversion_type, details in config.items():
                            print(f"Converting {value} from {details['from']} to {details['to']}")
                            if value is None:
                                print(f"Value is None, skipping conversion for {object['key_name']}")
                                continue
                            value = self.conversion_handler(str(value), conversion_type)
                except Exception as e:
                    print(f"Error processing sanitizer key {key}: {str(e)}")
                    continue

            return value
        except Exception as e:
            print(f"Error in handle_santisation: {str(e)}")
            return value

    def process_data(
        self,
        extracted_data: Optional[Dict] = None,
        yaml_data: Optional[Dict] = None,
        validation_schema: Optional[Dict] = None,
        schema: Optional[Dict] = None,
        is_serviceable: bool = True,
    ) -> Optional[Dict]:
        """
        Processes the extracted data and returns a compiled version of it.

        Args:
            extracted_data (Optional[Dict]): The extracted data from the raw data.
            yaml_data (Optional[Dict]): The configuration data from the yaml file.
            validation_schema (Optional[Dict]): The json schema used for validation.
            schema (Optional[Dict]): The base schema of the data.
            is_serviceable (bool, optional): Whether the source is serviceable. Defaults to True.

        Returns:
            Optional[Dict]: A dictionary containing the compiled data, error count, total count, error keys, and error message.
        """
        try:
            if not all([extracted_data, yaml_data, validation_schema, schema]):
                print("Missing required parameters")
                return None

            compiled_data = []
            error_keys = {}
            error_count = 0
            total_count = 0
            error_message = None

            try:
                schema_copy = self.utils.get_type_casted_schema(schema)
            except Exception as e:
                print(f"Error in schema type casting: {str(e)}")
                return None

            try:
                spec = importlib.util.spec_from_file_location("sanitizer", "path_to_sanitizer")
                sanitizer_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(sanitizer_module)
            except Exception as e:
                print(f"Error loading sanitizer module: {str(e)}")
                return None

            try:
                iterate = self.utils.get_iterate(extracted_data, is_serviceable)
                print(f"Started creating compile data using: {iterate}")
            except Exception as e:
                print(f"Error getting iterate: {str(e)}")
                return None

            for i in range(len(iterate)):
                try:
                    data = schema_copy.copy()
                    data["source"] = yaml_data["rival"]
                    data['client'] = yaml_data["client"]
                    
                    if yaml_data.get("index", True):
                        data['vehicle_category_position'] = i + 1

                    for field in yaml_data.get('to_extract', []):
                        try:
                            key = field['key_name']
                            value = extracted_data.get(key, [])
                            fallback_value = extracted_data.get(f'{key}_fallback', None)
                            
                            print(f"Processing key:{key}, value:{str(value)[:100]}")
                            
                            if len(value) not in [1, len(iterate)]:
                                print(f"Invalid value length for key:{key}, value:{value}")
                                data["is_error"] = True
                                error_count += 1
                                error_keys[key] = value
                                continue

                            if len(value) == 0:
                                continue

                            current_value = value[0] if len(value) == 1 else value[i]
                            current_fallback = fallback_value[0] if fallback_value and len(fallback_value) == 1 else fallback_value[i] if fallback_value else None

                            if current_value is None:
                                data[key] = current_value
                                continue

                            result = self.handle_santisation(
                                index=yaml_data['to_extract'].index(field),
                                value=current_value,
                                sanitizer_module=sanitizer_module,
                                yaml_data=yaml_data,
                                processed_values=data,
                                fallback_value=current_fallback,
                            )

                            if result is None:
                                data[key] = result
                                continue

                            try:
                                data[key] = result
                            except ValueError as e:
                                error_keys[key] = value
                                print(f"Type casting error for key {key}: {str(e)}")

                        except Exception as e:
                            print(f"Error processing field {key}: {str(e)}")
                            error_keys[key] = value
                            continue

                    processed_data = self.utils.get_processed_data(data)
                    
                    try:
                        jsonschema.validate(processed_data, validation_schema)
                        processed_data["compiler_id"] = str(hash(f"{self.source}_{i}"))
                        compiled_data.append(processed_data)
                        total_count += 1
                        print(f"Row {i} processed successfully. ID: {processed_data['compiler_id']}")
                    except jsonschema.exceptions.ValidationError as e:
                        print(f"Validation failed: {str(e)}")
                        error_message = str(e)
                        processed_data["is_error"] = True
                        error_count += 1
                        compiled_data.append(processed_data)

                except Exception as e:
                    print(f"Error processing row {i}: {str(e)}")
                    continue

            print(f"Completed creating compile data using: {iterate}")
            return {
                "compiled_data": compiled_data,
                "error_count": error_count,
                "total_count": total_count,
                "error_keys": error_keys,
                "error_message": error_message,
            }

        except Exception as e:
            print(f"Error in process_data: {str(e)}\nTraceback: {traceback.format_exc()}")
            return None