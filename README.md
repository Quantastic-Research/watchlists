# Watchlists
A Python library for managing stock watchlists as TOML files.

TOML (short for "Tom's Obvious Minimal Language") were developed by Tom Preston-Werner. It is an
alternative to other configuration file formats like .ini or .yaml. TOML was developed to be 
easy to read and write due to to obvious, minimalistic semantics.

TOML files provide an easy-to-understand medium for managing stock market watchlists, especially for
quantitative data analysis where multiple strategies and programs might require various lists of 
tickers.

The Watchlists generated using this library have four (4) default key-value pairings:
- title = The name of the TOML file.
- stocks = A list of strings representing stock tickers.
- version = A user-defined version number.
- date = The date that the watchlist was last updated.

## Using the Library
The suggested file structure to use this library is:

```
root/
|-- watchlists/
|   |-- __init__.py
|   |-- watchlists.py
|   |-- README.md
|   |-- archive/_placeholder.txt
|   `-- lists/
|       `-- DOW30.toml
`-- run.py
```

Where the code you write is located in the `run.py` file.

### Creating a Watchlist
You must create a watchlist using the create_watchlist() function.

```
from watchlists import Watchlist, create_watchlist

name = "SP500.toml"
version = "1"
tickers = ["META", "TSLA"]
update_date = "2024-01-02"
meta = {"index":"S&P500", "sector":"Technology"}

wl: Watchlist = create_watchlist(name, tickers, version, watchlist_date=update_date, metadata=meta)
```

### The Watchlist Object
You can use the watchlist object to interact with the watchlist variables. Features include:
- Read the name of the TOML file associated with the Watchlist
    - `wl.get_filename()`
- Modifying and reading the update date (dates should be strings, formatted as "YYYY-MM-DD")
    - `wl.update_date("2020-01-02")`
    - `wl.get_date()` (returns a string in format "YYYY-MM-DD")
- Adding, deleting, and reading the stock watchlist.
    - `wl.add_ticker("AAPL")`
    - `wl.delete_ticker("AAPL")`
    - `wl.get_list()` (returns a Python list)
- Adding, deleting, updatng, and reading meta data
    - `wl.add_meta_data(key, value)`
    - `wl.delete_meta_data(key)`
    - `wl.update_meta_data(key, value)`
    - `wl.get_meta_data(key)` (returns a string)
- Modifying and reading the version number
    - `wl.read_version()`
    - `wl.update_version()`
- Request a dictionary representing the TOML watchlist file
    - `wl.load()`

### Merging Watchlists
It might be helpful to merge two separate watchlists into a single, new watchlist TOML file. For that,
use the `merge_watchlists()` function.

```py
from watchlists import Watchlist, create_watchlist, merge_watchlists

name = "SP500.toml"
version = "1"
tickers = ["META", "TSLA"]
update_date = "2024-01-02"
meta = {"index":"S&P500", "sector":"Technology"}

wl: Watchlist = create_watchlist(name, tickers, version, watchlist_date=update_date, metadata=meta)
dow30 = Watchlist("DOW30.toml")

merged_watchlist: Watchlist = merge_watchlists(
    wl, # First watchlist
    dow30, # Second watchlist
    merged_name="New_Watchlist.toml", # New watchlist name
    version="1", # New watchlist version
    watchlist_date="", # New watchlist date (defaults to today's date on empty string)
    extract_meta_from=1 # Extract meta data from First Watchlist
    )
```
#### merge_watchlists Parameters
- watchlist1: Watchlist
    - Required, represents the first Watchlist in the merge
- watchlist2: Watchlist
    - Required, represent the second Watchlist in the merge
- merged_name: str
    - Defaults to (Watchlist #1 Name)_(Watchlist #2 Name).TOML when merged_name = ""
    - When specified, detects .toml extension and adds if necessary
- version: str
    - Defaults to "1"
- watchlist_date: str
    - Defaults to today's date in YYYY-MM-DD format when watchlist_date = ""
    - When specified, must be a string in YYYY-MM-DD format representing a date _before or including_ today's date.
- extract_meta_from: int
    - Defaults to extracting no metadata from either Watchlist
    - Accepts values from 0 and 2, inclusive
        - 0 = No metadata is copied into the new watchlist
        - 1 = Metadata from Watchlist #1 is copied into new watchlist
        - 2 = Metadata from Watchlist #2 is copied into new watchlist

## Contact and Issues
Feel free to create [issue requests](https://github.com/Quantastic-Research/watchlists/issues) in this repo. [GitHub Profile](https://github.com/dpsciarrino).

Blog: [Quantastic Research](https://quantasticresearch.com/)
