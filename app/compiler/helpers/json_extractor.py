from jsonpath_ng.ext import parse

class JsonDataExtractor():
    """
    This class is used to compile the raw data according to config.yaml file.
    
    Functions:
        extract_data            : This function will extract the data.
        extract_schema_overrides: This function will extract the schema overrides if present.
        
    Example:
        >>> json_data_extractor = JsonDataExtractor()
        >>> json_data_extractor.extract_data(raw_data, yaml_data)
    """

    def __init__(
        self
    ):
        pass

    def extract_data(self, raw_data: object, yaml_data: object, is_serviceable: bool) -> dict:
        """
        Extracts data from the given raw data and YAML configuration.

        Args:
            raw_data (object): The raw data to extract data from.
            yaml_data (object): The YAML configuration containing the extraction rules.

        Returns:
            dict: A dictionary containing the extracted data. The keys of the dictionary are the names of the extracted fields, and the values are the corresponding data extracted from the raw data.

        Raises:
            KeyError: If required fields are missing in yaml_data
            Exception: For other unexpected errors during extraction
        """
        try:
            extracted_data_dict = {}
            
            if not isinstance(yaml_data, dict) or not isinstance(raw_data, dict):
                raise TypeError("raw_data and yaml_data must be dictionaries")
                
            if is_serviceable:
                try:
                    for i, fields in enumerate(yaml_data.get("to_extract", [])):
                        try:
                            key_name = fields.get("key_name")
                            key_value = fields.get("key_field_path")
                            fall_back_value = fields.get("fall_back_path", None)
                            get_keys = fields.get("get_keys", False)

                            # Validate `key_name` and `key_field_path`
                            if not key_name or not key_value:
                                raise ValueError(f"Missing [key_name] or [key_field_path] in {fields}")
                            
                            # Skip if `key_name` already exists in the dictionary
                            if key_name in extracted_data_dict:
                                # print(f"Key {key_name} already exists in extracted_data_dict, skipping", "info")
                                continue
                            
                            # Parse JSONPath
                            try:
                                jsonpath = parse(key_value)
                            except Exception as e:
                                print(f"Invalid JSONPath '{key_value}': {e}", "error")
                                raise ValueError(f"Invalid JSONPath '{key_value}': {e}")
                            
                            # Extract matching values
                            matches = list(jsonpath.find(raw_data))
                            
                            if get_keys:
                                temp_data = []
                                try:
                                    temp_data = [match.value if match.value is not None else None for match in matches]
                                    temp_data = [list(match.keys()) if match is not None else None for match in temp_data]
                                    temp_data = [item for sublist in temp_data for item in sublist]
                                except AttributeError as e:
                                    print(f"Error getting keys from match: {e}", "error")
                                    temp_data = []
                            else:
                                temp_data = [match.value if match.value is not None else None for match in matches]
                            
                            if fall_back_value:
                                try:
                                    jsonpath = parse(fall_back_value)
                                    fallback_matches = list(jsonpath.find(raw_data))
                                    
                                    if get_keys:
                                        fallback_data = []
                                        try:
                                            fallback_data = [match.value if match.value is not None else None for match in fallback_matches]
                                            fallback_data = [list(match.keys()) if match is not None else None for match in fallback_data]
                                            fallback_data = [item for sublist in fallback_data for item in sublist]
                                        except AttributeError as e:
                                            print(f"Error getting keys from fallback match: {e}", "error")
                                    else:
                                        fallback_data = [match.value if match.value is not None else None for match in fallback_matches]
                                    
                                    if fallback_data:
                                        extracted_data_dict[f'{key_name}_fallback'] = fallback_data   
                                    
                                    if not temp_data:
                                        temp_data = fallback_data
                                        
                                except Exception as e:
                                    print(f"Error processing fallback value '{fall_back_value}': {e}", "error")
                            
                            extracted_data_dict[key_name] = temp_data
                            # print(f"Data extracted for {key_name}: {temp_data}", "info")
                            
                        except Exception as e:
                            print(f"Error processing field {fields}: {e}", "error")
                            continue
                            
                except Exception as e:
                    print(f"Error processing serviceable data: {e}", "error")
                    return None, str(e)

            else:
                print('Message Not Serviceable modifying Category to N/A', 'warning')
                try:
                    for i, fields in enumerate(yaml_data["to_extract"]):
                        try:
                            key_name = fields.get("key_name", None)
                            key_value = fields.get("key_field_path", None)
                            
                            if key_name is None or key_value is None:
                                raise ValueError(f"Missing [key_name] or [key_field_path] in {fields}")
                            
                            jsonpath = parse(key_value)
                            data = [match.value for match in jsonpath.find(raw_data)]

                            if len(data) > 0:
                                extracted_data_dict[key_name] = [data[0]]
                            else:
                                extracted_data_dict[key_name] = ["N/A"]
                            
                            if key_name == "vehicle_category":
                                extracted_data_dict[key_name] = ["N/A"]
                                
                        except Exception as e:
                            print(f"Error processing non-serviceable field {fields}: {e}", "error")
                            continue
                            
                except Exception as e:
                    print(f"Error processing non-serviceable data: {e}", "error")
                    return None, str(e)

            return extracted_data_dict, {"success": True}
            
        except Exception as e:
            print(f"Unexpected error in extract_data: {e}", "error")
            return None, str(e)

    def extract_serviceable(self, raw_data: object, yaml_data: object) -> dict:
        """
        Extracts the serviceable status from the given raw data and YAML configuration using jsonpath.

        Args:
            raw_data (object): The raw data from which to extract the serviceable status.
            yaml_data (object): The YAML configuration containing the extraction rules.

        Returns:
            dict: A dictionary containing the serviceable status.
        """
        try:
            serviceable_value = None
            serviceable_exist = False
            
            if not isinstance(yaml_data, dict) or "to_extract" not in yaml_data:
                raise ValueError("Invalid yaml_data format")
                
            for i, fields in enumerate(yaml_data["to_extract"]):
                try:
                    serviceable = fields.get("key_name", None)
                    if serviceable is not None and serviceable == "serviceable":
                        serviceable_value = fields.get("key_field_path", None)
                        serviceable_exist = True
                        break
                except Exception as e:
                    print(f"Error processing field for serviceable status: {e}", "error")
                    continue
            
            if serviceable_exist is False:
                print("Missing [key_name] serviceable continuing to orginal compilation", "warning")
                return True

            if serviceable_value is None and serviceable_exist is True:
                print("Missing [key_field_path] value in serviceable", "warning")
                return None
            
            try:
                jsonpath = parse(serviceable_value)
                data = [match.value for match in jsonpath.find(raw_data)]
                if data == [] or data is None:
                    return False
                return data[0]
                
            except Exception as e:
                print(f"Error parsing or extracting serviceable value: {e}", "error")
                return None
                
        except Exception as e:
            print(f"Unexpected error in extract_serviceable: {e}", "error")
            return None

    def extract_schema_overrides(self, raw_data: object, yaml_data: object) -> dict:
        """
        Extracts the schema overrides from the given raw data and YAML configuration.

        Args:
            raw_data (object): The raw data from which to extract the schema overrides.
            yaml_data (object): The YAML configuration containing the extraction rules.

        Returns:
            dict: A dictionary containing the keys of the schema overrides.
        """
        try:
            keys = {}
            
            if not isinstance(yaml_data, dict) or "to_extract" not in yaml_data:
                raise ValueError("Invalid yaml_data format")
                
            for i, fields in enumerate(yaml_data["to_extract"]):
                try:
                    key_name = fields.get("key_name")
                    if not key_name:
                        raise ValueError(f"Missing key_name in field {fields}")
                        
                    schema_overrides = fields.get("schema_overrides", None)
                    value_type = fields.get("type", 'string')
                    
                    if schema_overrides is None:
                        schema_overrides = fields.get("schema_override", None)
                        
                    if schema_overrides:
                        # print(f"Extracting schema override for {key_name}, type: {value_type}", "warning")
                        keys[key_name] = {
                            "key": schema_overrides,
                            "type": value_type
                        }
                        
                except Exception as e:
                    print(f"Error processing schema override for field {fields}: {e}", "error")
                    continue
                    
            return keys
            
        except Exception as e:
            print(f"Unexpected error in extract_schema_overrides: {e}", "error")
            return {}