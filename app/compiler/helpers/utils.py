import random
from typing import List
import logging

class Utils:
    """
    This is a Custom Integration in Compiler.
    This is a specific helper for Ride.

    Methods:
        >>> __init__              : Initialize the class
        >>> get_iterate           : Get the iterate value from the extracted data.
        >>> handle_trip_time      : Handle the trip time from the extracted data.
        >>> get_processed_data    : Process the extracted data.
        >>> get_type_casted_schema: Type cast schema according to specified types.
    """

    def __init__(self):
        """Initialize the Utils class."""
        self.logger = logging.getLogger(__name__)

    def _validate_extracted_data(self, extracted_data: dict) -> None:
        """
        Validate the extracted data dictionary.

        Args:
            extracted_data (dict): Data to validate

        Raises:
            TypeError: If extracted_data is not a dictionary
            ValueError: If extracted_data is empty
        """
        if not isinstance(extracted_data, dict):
            raise TypeError(f"Expected dictionary for extracted_data, got {type(extracted_data)}")
        if not extracted_data:
            raise ValueError("Extracted data dictionary is empty")

    def get_iterate(self, extracted_data: dict, is_serviceable: bool) -> List[str]:
        """
        Get the iterate value from the extracted data.
        Check if vehicle_name is present in the extracted data, if yes then return the vehicle_name else return vehicle_category.

        Args:
            extracted_data (dict): Extracted data
            is_serviceable (bool): Whether the service is available

        Returns:
            List[str]: Iterate value

        Raises:
            TypeError: If inputs are of wrong type
            KeyError: If required keys are missing
            Exception: For other unexpected errors
        """
        try:
            # Validate inputs
            self._validate_extracted_data(extracted_data)
            if not isinstance(is_serviceable, bool):
                raise TypeError(f"Expected boolean for is_serviceable, got {type(is_serviceable)}")

            if is_serviceable:
                try:
                    if "vehicle_name" in extracted_data:
                        iterate = extracted_data["vehicle_name"]
                    elif "vehicle_category" in extracted_data:
                        iterate = extracted_data["vehicle_category"]
                    else:
                        raise KeyError("Neither vehicle_name nor vehicle_category found in extracted data")
                    
                    # Validate iterate value
                    if not isinstance(iterate, list):
                        raise TypeError(f"Expected list for iterate value, got {type(iterate)}")
                    if not all(isinstance(item, str) for item in iterate):
                        raise TypeError("All iterate items must be strings")
                    
                    return iterate
                except KeyError as e:
                    self.logger.error(f"Key error in get_iterate: {str(e)}")
                    raise
            else:
                self.logger.warning("Service not available, returning default value")
                return ['N/A']

        except Exception as e:
            self.logger.error(f"Error in get_iterate: {str(e)}")
            raise

    def handle_trip_time(self, data: dict) -> dict:
        """
        Handle the trip time from the extracted data.

        Args:
            data (dict): Extracted data

        Returns:
            dict: Extracted data with trip time handled

        Raises:
            TypeError: If input is not a dictionary
            ValueError: If input data is empty
            Exception: For other unexpected errors
        """
        try:
            self._validate_extracted_data(data)
            
            try:
                eta = data.get("vehicle_eta")
                trip_time = data.get("estimated_trip_time")
                
                if eta is not None and trip_time is not None:
                    try:
                        # Validate numeric types
                        if not isinstance(eta, (int, float)) or not isinstance(trip_time, (int, float)):
                            raise TypeError("vehicle_eta and estimated_trip_time must be numeric")
                        
                        data["estimated_total_trip_time"] = eta + trip_time
                    except (TypeError, ValueError) as e:
                        self.logger.error(f"Error calculating total trip time: {str(e)}")
                        data["estimated_total_trip_time"] = None
                else:
                    data["estimated_total_trip_time"] = None
                
                return data
                
            except Exception as e:
                self.logger.error(f"Error processing trip time: {str(e)}")
                data["estimated_total_trip_time"] = None
                return data

        except Exception as e:
            self.logger.error(f"Error in handle_trip_time: {str(e)}")
            raise

    def get_processed_data(self, data: dict) -> dict:
        """
        Get the ride data from the extracted data.

        Args:
            data (dict): Extracted data

        Returns:
            dict: Processed ride data

        Raises:
            TypeError: If input is not a dictionary
            ValueError: If input data is empty
            Exception: For other unexpected errors
        """
        try:
            self._validate_extracted_data(data)
            return self.handle_trip_time(data)
        except Exception as e:
            self.logger.error(f"Error in get_processed_data: {str(e)}")
            raise

    def get_type_casted_schema(self, schema: dict) -> dict:
        """
        Type cast schema according to specified types.

        Args:
            schema (dict): Schema to type cast

        Returns:
            dict: Type casted schema

        Raises:
            TypeError: If input is not a dictionary
            ValueError: If schema is empty or invalid
            Exception: For other unexpected errors
        """
        try:
            self._validate_extracted_data(schema)
            
            for key, value in schema.items():
                try:
                    if not isinstance(value, dict):
                        raise TypeError(f"Schema value for key '{key}' must be a dictionary")
                    
                    data_type = value.get("type")
                    if data_type is None:
                        raise ValueError(f"No type specified for key '{key}'")

                    # Handle list of types
                    if isinstance(data_type, list):
                        if not data_type:
                            raise ValueError(f"Empty type list for key '{key}'")
                        data_type = data_type[0]

                    if not isinstance(data_type, str):
                        raise TypeError(f"Type must be string for key '{key}', got {type(data_type)}")

                    try:
                        if data_type == "string":
                            setattr(self, key, "")

                        elif data_type == "integer":
                            minimum = value.get("minimum", 1)
                            maximum = value.get("maximum", 100)
                            if not isinstance(minimum, (int, float)) or not isinstance(maximum, (int, float)):
                                raise TypeError(f"Minimum and maximum must be numeric for key '{key}'")
                            if minimum > maximum:
                                raise ValueError(f"Minimum ({minimum}) is greater than maximum ({maximum}) for key '{key}'")
                            setattr(self, key, random.randint(int(minimum), int(maximum)))

                        elif data_type == "number":
                            minimum = value.get("minimum", 0)
                            maximum = value.get("maximum", 100)
                            if not isinstance(minimum, (int, float)) or not isinstance(maximum, (int, float)):
                                raise TypeError(f"Minimum and maximum must be numeric for key '{key}'")
                            if minimum > maximum:
                                raise ValueError(f"Minimum ({minimum}) is greater than maximum ({maximum}) for key '{key}'")
                            setattr(self, key, random.uniform(float(minimum), float(maximum)))

                        elif data_type == "boolean":
                            setattr(self, key, random.choice([True, False]))

                        elif data_type == "array":
                            setattr(self, key, [])

                        elif data_type == "dict":
                            setattr(self, key, {})

                        else:
                            self.logger.warning(f"Unknown data type '{data_type}' for key '{key}', setting to None")
                            setattr(self, key, None)

                    except (TypeError, ValueError) as e:
                        self.logger.error(f"Error setting value for key '{key}': {str(e)}")
                        setattr(self, key, None)

                except Exception as e:
                    self.logger.error(f"Error processing schema key '{key}': {str(e)}")
                    setattr(self, key, None)

            self.logger.info("Datatype checking and typecasting completed successfully")
            return self.__dict__

        except Exception as e:
            self.logger.error(f"Error in get_type_casted_schema: {str(e)}")
            raise