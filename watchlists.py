from pathlib import Path
import os.path as ospath

import tomllib
import tomlkit

import re
from datetime import date

def _create_toml_document_object(name:str, tickers:list, version:str, date:str, metadata:dict):
    """
    Returns a tomlkit.TOMLDocument object with the given parameters.

    Parameters:
    -----------
    - name
    - tickers
    - version
    - date
    - metadata
    """
    doc: tomlkit.TOMLDocument = tomlkit.document()
    doc.add("title", name)
    doc.add("stocks", tickers)
    doc.add("version", version)
    doc.add("date", date)
    for key in metadata.keys():
        doc.add(key, metadata[key])
    
    return doc

def _get_archive_directory():
    """
    !!!INTERNAL METHOD!!!
    This method should only be used by the Watchlists library classes and functions. Outside use
    is not suggested and may result in broken code and unexpected behavior.

    Description:
    ------------
    Returns the path to the complementary archive folder.
    """
    return Path( ospath.dirname( ospath.realpath(__file__) ) ) / "archive"

def _get_watchlist_directory():
    """
    !!!INTERNAL METHOD!!!
    This method should only be used by the Watchlists library classes and functions. Outside use
    is not suggested and may result in broken code and unexpected behavior.

    Description:
    ------------
    Returns the path to the TOML watchlist files.
    """
    return Path( ospath.dirname( ospath.realpath(__file__) ) ) / "lists"

def _is_date(dt: str) -> bool:
    """
    !!!INTERNAL METHOD!!!
    This method should only be used by the Watchlists library classes and functions. Outside use
    is not suggested and may result in broken code and unexpected behavior.

    Description:
    ------------
    Checks whether the given date is in YYYY-MM-DD format. Also checks whether dt is a real date.
    """
    date_pattern = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.IGNORECASE)
    if date_pattern.match(dt):
        year, month, day = dt.split('-')
        try:
            date(int(year), int(month), int(day))
            return True
        except ValueError:
            return False
    else:
        raise AttributeError

def _is_future_date(dt:str) -> bool:
    """
    !!!INTERNAL METHOD!!!
    This method should only be used by the Watchlists library classes and functions. Outside use
    is not suggested and may result in broken code and unexpected behavior.

    Description:
    ------------
    Checks whether the given date is in the future with respect to today. Assumes YYYY-MM-DD format.
    """
    year, month, day = dt.split("-")
    d = date(int(year), int(month), int(day))
    return date.today() < d

def _is_toml(filename:str) -> bool:
    """
    !!!INTERNAL METHOD!!!
    This method should only be used by the Watchlists library classes and functions. Outside use
    is not suggested and may result in broken code and unexpected behavior.

    Description:
    ------------
    Checks whether the given filename is a TOML file.
    """
    # Check for None Type
    if filename is None:
        return False

    # Check for TOML file extension
    if not filename.upper().endswith(".TOML"):
        return False

    return True

def _verify_and_clean_date(watchlist_date: str):
    """
    Verifies and cleans the date.
    """
    if watchlist_date is None:
        raise ValueError("Date cannot be None-type.")
    
    if watchlist_date == "":
        return watchlist_date
    else:
        if _is_date(watchlist_date) and not _is_future_date(watchlist_date):
            return watchlist_date

    raise ValueError("Must provide date in format YYYY-MM-DD.")

def _verify_and_clean_list(watchlist_list:list):
    """
    Verifies and cleans a list of stocks to add to watchlist.
    """
    if watchlist_list is None or not watchlist_list:
        raise ValueError("Provide a list of at least 1 stock ticker in watchlist.")
    
    _tickers: list = []
    for ticker in watchlist_list:
        if type(ticker) != str:
            raise ValueError("A non-string value was detected in the list of stocks. Provide only strings")
        
        _tickers.append(ticker)
    
    _tickers.sort()

    return _tickers

def _verify_and_clean_metadata(meta_data:dict):
    """
    Verifies and cleans the metadata.
    """
    if meta_data is None:
        raise ValueError("Metadata cannot be provided as Nonetype.")

    cleaned_metadata: dict = {}
    for key in meta_data.keys():
        value = meta_data[key]
        if value is None:
            raise ValueError(f"Value of key {key} in meta data cannot be None.")
        if type(meta_data[key]) != str:
            raise ValueError(f"Value of key {key} in meta data must be a string.")
        
        cleaned_metadata[key] = value
    
    return cleaned_metadata

def _verify_and_clean_watchlist_name(watchlist_name:str):
    """
    Verifies and cleans the filename for a TOML watchlist.
    """
    if watchlist_name is None or not watchlist_name:
        raise ValueError("Provide watchlist name.")
    
    if _is_toml(watchlist_name):
        return watchlist_name
    
    return watchlist_name + ".toml"

def _verify_and_clean_version(version):
    """
    Verifies and cleans the version for a TOML watchlist.
    """
    if version is None:
        raise ValueError("Version cannot be Nonetype.")
    
    if type(version) != str:
        if type(version) == int or type(version) == float:
            return str(version)
        else:
            raise ValueError("Version must be a string.")
    
    return str(version)

    


def _watchlist_exists(filename:str) -> bool:
    if _is_toml(filename):
        # Define filepath
        watchlist_filepath: Path = _get_watchlist_directory() / filename

        # Check if file exists
        if not watchlist_filepath.is_file():
            raise FileNotFoundError 
        
        return True
    
    raise AttributeError



class Watchlist:
    def __init__(self, filename:str):
        """
        Watchlist allows you to interact with an individual TOML file holding a stock watchlist.

        The TOML file must live in the 'lists' directory and must have been created using the 
        create_watchlist() function.

        Parameters:
        -----------
        - filename: The name of the TOML file to associated with an instance of Watchlist.
            - File must exist in the 'lists' folder before instantiating a Watchlist.
            - Examples: "DOW30.toml", "DOW30", "DOW30.TOML"
        """

        # Verify that the Watchlist TOML file exists
        try:
            _watchlist_exists(filename)
        except FileNotFoundError:
            print("EXCEPTION: Watchlist file not found in watchlist directory.")
        except AttributeError:
            print("EXCEPTION: Provided filename is not a TOML file. Make sure you include the extension (.toml) when specifying filename.")

        # Define Watchlist TOML file path
        self._filepath = _get_watchlist_directory() / filename

        # Define and sync dict associated with the given TOML file.
        self._toml_dict: dict = {}
        self._update_toml_dict()

        # Defines a list of default keys in every Watchlist TOML file.
        self._default_keys = ['title', 'stocks', 'version', 'date']
    
    def _update_toml_dict(self):
        """
        !!!INTERNAL METHOD!!!
        This method should only be used by the Watchlists library classes and functions. Outside use
        is not suggested and may result in broken code and unexpected behavior.

        Description:
        ------------
        Updates the internal TOML dictionary object by reading the associated TOML file.
        """
        try:
            with open(str(self._filepath), 'rb') as watchlist_file:
                self._toml_dict = tomllib.load(watchlist_file)
        except Exception as e:
            print("EXCEPTION: Something went wrong opening TOML file when updating internal Watchlist model.")
        finally:
            watchlist_file.close()
    
    def add_meta_data(self, key: str, value:str):
        """
        Adds meta data to the watchlist TOML file. The key-value must be strings.

        If the key is already in the watchlist, returns None (Use update_meta_data instead).
        If the key is not in the watchlist, updates the watchlist TOML file and returns a dictionary
            representing the watchlist file.
        """
        if key in self._toml_dict.keys():
            print("EXCEPTION: Key already found in watchlist.")
            return None
        else:
            self._update_toml_file(key, value)
            return self.load()
    
    def add_ticker(self, ticker: str):
        """
        Adds a ticker symbol to the existing stock list.

        Note: This function capitalizes (upper()) the ticker string and resorts the watchlist.
        """
        if ticker is None: raise ValueError("Ticker cannot be None-type.")

        stock_list: list = self.get_list()
        if ticker.upper() not in stock_list:
            stock_list.append(ticker)
        
        stock_list.sort()

        self.update_list(stock_list)

        return self.get_list()
    
    def delete_meta_data(self, meta_key:str) -> dict:
        """
        Deletes a given meta data tag from watchlist file.

        Returns the key and value as a dictionary of the deleted meta key.

        If meta_key is an empty string, then return None.
        If meta_key is not found in the watchlist file, return None.
        """
        # Empty meta key
        if meta_key == "":
            return None
        
        # If meta_key is a default key, throw exception
        if meta_key in self._default_keys:
            raise ValueError("Cannot delete a default key [title, stocks, version, date]")
        
        # If meta_key found in TOML keys
        if meta_key in self._toml_dict.keys():
            # Extract the value
            v = self._toml_dict[meta_key]
            # Delete the key-value pair in local dictionary object
            del self._toml_dict[meta_key]
            # Update TOML file for deletion
            self._update_toml_file("")

            # Return the deleted key-value pair as a dictionary
            return {meta_key: v}
        
        return None

    def delete_ticker(self, ticker: str):
        """
        Deletes the given ticker from the watchlist file.
        
        Returns the newly updated stock list.
        """
        if ticker is None: raise ValueError("Ticker cannot be None type.")

        stock_list: list = self.get_list()
        if ticker in stock_list:
            stock_list.remove(ticker)
        
        self.update_list(stock_list)

        return stock_list

    def get_date(self):
        """
        Retrieves the date associated with the Watchlist file.
        """
        try:
            return self._toml_dict['date']
        except KeyError:
            print("EXCEPTION: Watchlist file has no associated date.")
        return ""
    
    def get_filename(self, extension=True):
        """
        Retrieves the name of the TOML file associated with this Watchlist.

        Parameters:
        -----------
        - extension: True to include the ".toml" extension (default). Set False to exclude it.
        """
        if extension:
            return self._filepath.stem + self._filepath.suffix
        return self._filepath.stem
    
    def get_list(self):
        """
        Returns the watchlist of stocks as a Python list.
        """
        try:
            return self._toml_dict['stocks']
        except KeyError:
            print("EXCEPTION: The associated watchlist file's list of stocks is missing.")
        return []
    
    def get_meta_data(self, meta_key: str):
        """
        Returns any additional meta data from the Watchlist file.

        Note: This function is designed for very basic key-value pairs. Your mileage
        may vary with more advanced TOML structures.

        Parameters:
        -----------
        - meta_key: Defines the key for the value to be returned. Cannot be any of the 
            default keys ['date', 'title', 'stocks', 'version'].
        """
        if meta_key == "":
            return None
        
        try:
            if meta_key not in ['title', 'stocks', 'version', 'date']:
                return self._toml_dict[meta_key]
            raise ValueError("Do not use get_meta_data() to obtain values in default watchlist keys (titel, stocks, version, date).")
        except KeyError:
            print("EXCEPTION: No such key in Watchlist file.")
            return None
    
    def get_version(self):
        """
        Returns the version of the Watchlist file.
        """
        try:
            return self._toml_dict['version']
        except KeyError:
            print("EXCEPTION: No version specified for associated Watchlist.")
        
        return ""
    
    def load(self):
        """
        Retrieves dictionary representation of associated Watchlist TOML file.
        """
        return self._toml_dict

    def update_date(self, new_date: str = ""):
        """
        Updates the date of the Watchlist.

        Parameters:
        -----------
        - new_date: If given an empty string, the file updates with today's date (default).
            Otherwise, the string passed through new_date must be in the form YYYY-MM-DD.

        Returns new_date on successful update.
        """
        date_to_insert = str(date.today())

        # Check whether new_date adheres to proper formatting
        if new_date != "":
            try:
                _is_date(new_date)
            except AttributeError:
                print("EXCEPTION: Invalid date format. Must be YYYY-MM-DD.")
                return None
            except ValueError:
                print("EXCEPTION: Invalid date.")
                return None
            
            try:
                if not _is_future_date(new_date):
                    date_to_insert = new_date
                else:
                    raise ValueError
            except ValueError:
                print("EXCEPTION: Updated date cannot exceed today's date.")
                return None
                    
        # Update watchlist document
        self._update_toml_file('date', date_to_insert)

        return date_to_insert
    
    def update_list(self, new_list: list):
        """
        Updates the watchlist with a list of new stock tickers.

        If update fails, None is returned. If update succeeds, the new_list is returned.
        """
        if not new_list: raise ValueError("Cannot update watchlist with empty list.")

        try:
            self._update_toml_file('stocks', new_list)
            return new_list
        except Exception:
            return None
    
    def update_meta_data(self, meta_key:str, meta_value:str):
        """
        If the meta_key is found, updates the associated value and returns the updated value.

        If the meta_key is found in default_keys, throws a ValueError.
        If the meta_key is not found, returns None.
        If the meta_key is an empty string, returns None.
        """
        # Empty key returns None
        if meta_key == "": return None
        
        # Meta key is found
        if meta_key in self._toml_dict.keys():
            # Meta key is not a default key
            if meta_key not in self._default_keys:
                self._update_toml_file(meta_key, meta_value)
                return meta_value
            else:
                raise ValueError("Do not update default keys using update_meta_data().")
        
        # Meta key not found
        return None

    def update_version(self, new_version:str = ""):
        """
        Updates the version and returns the new version of the watchlist.

        If version is not provided, function attempts to increment the existing version number.
        When an increment is attempted, a whole number is assumed (1, 2, ...).

        For decimal versions (1.1, 1.2, ...) please use the new_version parameter.
        """
        version_to_insert: str = new_version

        # Default is to increment the version number
        if new_version == "":
            version: str = self.get_version()
            try: 
                version_to_insert = str(int(version) + 1)
            except ValueError:
                print("EXCEPTION: Failed trying to increment integer version number. Specify a new version number as a string instead.\nIf you want the ability to increment, specify an integer number as a string.")
                
                return ""
            
        self._update_toml_file('version', version_to_insert)

        return version_to_insert

    def _update_toml_file(self, key: str, value:str = ""):
        """
        !!!INTERNAL METHOD!!!
        This method should only be used by the Watchlists library classes and functions. Outside use
        is not suggested and may result in broken code and unexpected behavior.

        Description:
        ------------
        Takes in a key-value pair and overwrites the associated value in the TOML file.

        If key is an empty string, a deletion is assumed to have occurred.
        The internal _toml_dict is assumed to already have been updated.
        The TOML file is then updated according to the _toml_dict object.
        No update is required in this scenario.

        Parameters:
        -----------
        - watchlist: The Watchlist object
        - key: The key to look up in the TOML watchlist file.
        - value: The value to assign for the given key in the TOML watchlist file.
        """
        # Create a TOMLDocument object
        doc = tomlkit.document()

        # Check for deletion case
        if key == "":
            # Deletion has taken place, copy ALL keys for overwrite.
            for k in self._toml_dict.keys():
                doc.add(k, self._toml_dict[k])
        else:
            # Copy over existing, unchanged key-value pairs
            for k in self._toml_dict.keys():
                if k != key:
                    doc.add(k, self._toml_dict[k])
            
            # Copy over the modified key-value
            doc.add(key, value)
        
        # Update TOML with changes
        watchlist_filepath = _get_watchlist_directory() / self.get_filename()

        try:
            with open(str(watchlist_filepath), 'w') as f:
                f.write(tomlkit.dumps(doc))
        except Exception as e:
            print("EXCEPTION: Raised exception while updating TOML file. Check pathing and file location.")
            return -1
        finally:
            f.close()
        
        if key != "":
            # Update the internal dictionary model
            self._update_toml_dict()
        
        return 0


def create_watchlist(name: str, watchlist: list, version: str = "1", watchlist_date: str = "", metadata:dict = {}) -> Watchlist:
    """
    Creates a TOML Watchlist file located in the 'lists' directory.
    This function creates a new TOML file and overwrites one if named the same.

    Parameters:
    -----------
    - name: the name of the watchlist to be added. TOML extension will be added if not detected
    - watchlist: a Python list of tickers to be added, all strings representing tickers. upper() is applied.
    - version: defaults to "1"
    - watchlist_date: defaults to today's date, must be in YYYY-MM-DD format
    - metadata: a dictionary of key-value pairs to be added to the watchlist document
        Example:
        - "index": "S&P500"
        
    Returns: Watchlist object
    """
    # Verify and clean name
    try:
        _watchlist_name: str = _verify_and_clean_watchlist_name(name)
    except ValueError as e:
        print("EXCEPTION: ", e.args)
        return None
    
    # Verify and clean list
    try:
        _watchlist_list = _verify_and_clean_list(watchlist)
    except ValueError as e:
        print("EXCEPTION: ", e.args)
        return None
    
    # Verify and clean version
    try:
        _watchlist_version = _verify_and_clean_version(version)
    except ValueError as e:
        print("EXCEPTION: ", e.args)
        return None
    
    # Verify and clean date
    if watchlist_date == "":
        _watchlist_date = str(date.today())
    else:
        try:
            _watchlist_date = _verify_and_clean_date(watchlist_date)
        except ValueError as e:
            print("EXCEPTION: ", e.args)
            return None
    
    # Verify and clean meta
    try:
        _watchlist_meta = _verify_and_clean_metadata(metadata)
    except ValueError as e:
        print("EXCEPTION: ", e.args)
        return None
    
    # Create TOML Document Object
    doc = _create_toml_document_object(_watchlist_name, _watchlist_list, _watchlist_version, _watchlist_date, _watchlist_meta)

    # Create watchlist file in watchlists directory
    try:
        _watchlist_path: Path = _get_watchlist_directory() / _watchlist_name
        with open(str(_watchlist_path), 'w') as f:
            f.write(tomlkit.dumps(doc))
    except Exception as e:
        print("Exception: Raised exception while creating TOML file. Check pathing and file location.")
        return None
    
    # Return Watchlist object
    return Watchlist(filename = _watchlist_name)



def merge_watchlists(watchlist1:Watchlist, watchlist2:Watchlist, merged_name:str = "", version:str = "1", watchlist_date:str = "", extract_meta_from:int = 0):
    """
    Merges two watchlists together to create a new watchlist.

    Parameters:
    -----------
    - watchlist1: Watchlist object #1
    - watchlist2: Watchlist object #2
    - merged_name: Defaults to <Watchlist1Name>_<Watchlist2Name>.toml. If provided, tags .toml at the end.
    - version: Defaults to 1.
    - extract_meta_from: An integer value stating where to extract meta data from.
        - 0 = No meta data
        - 1 = Watchlist #1
        - 2 = Watchlist #2
    
    Returns a Watchlist object representing the new file.
    """
    if watchlist1 is None or watchlist2 is None:
        raise ValueError("Watchlist cannot be None. Must be of type Watchlist.")
    
    # Combine watchlist stock lists, remove duplicates
    list1:list = watchlist1.get_list()
    list2:list = watchlist2.get_list()
    _watchlist_list: list = list1 + list(set(list2) - set(list1))
    _watchlist_list.sort()

    # Determine new watchlist name
    _watchlist_name: str = merged_name
    if merged_name is None:
        raise ValueError("Merged Name cannot be None type.")
    
    if merged_name == "":
        name1: str = watchlist1.get_filename().replace(".toml", "")
        name2: str = watchlist2.get_filename().replace(".toml", "")
        _watchlist_name = name1 + "_" + name2 + ".toml"
    else:
        if not _watchlist_name.upper().endswith(".TOML"):
            _watchlist_name = _watchlist_name + ".toml"
    
    # Verify and clean version
    try:
        _watchlist_version = _verify_and_clean_version(version)
    except ValueError as e:
        print("Exception: ", e.args)
        return None
    
    # Verify and clean date
    if watchlist_date == "":
        _watchlist_date = str(date.today())
    else:
        try:
            _watchlist_date = _verify_and_clean_date(watchlist_date)
        except ValueError as e:
            print("Exception: ", e.args)
            return None
    
    # Determine meta data extraction source
    if extract_meta_from is None:
        raise ValueError("extract_meta_from parameter cannot be None. Expecting an integer value from 0 to 2, inclusive.")

    if extract_meta_from < 0 or extract_meta_from > 2:
        raise ValueError(f"extract_meta_from must be an integer from 0 to 2, inclusive. Got: {extract_meta_from}")
    
    _watchlist_meta_data = {}
    if extract_meta_from == 1:
        watchlist_dict = watchlist1.load()
        for key in watchlist_dict.keys():
            if key not in ['date', 'title', 'version', 'stocks']:
                _watchlist_meta_data[key] = watchlist_dict[key]

    elif extract_meta_from == 2:
        watchlist_dict = watchlist2.load()
        for key in watchlist_dict.keys():
            if key not in ['date', 'title', 'version', 'stocks']:
                _watchlist_meta_data[key] = watchlist_dict[key]

    # Create TOML document object    
    doc = _create_toml_document_object(_watchlist_name, _watchlist_list, _watchlist_version, _watchlist_date, _watchlist_meta_data)
    
    # Create watchlist file in watchlists directory
    try:
        _watchlist_path: Path = _get_watchlist_directory() / _watchlist_name
        with open(str(_watchlist_path), 'w') as f:
            f.write(tomlkit.dumps(doc))
    except Exception as e:
        print("Exception: Raised exception while creating TOML file. Check pathing and file location.")
        return None
    finally:
        f.close()

    # Return Watchlist object
    return Watchlist(filename = _watchlist_name)