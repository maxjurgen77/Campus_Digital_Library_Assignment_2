# Campus Digital Library System — Assignment Two

## Requirements
- Python 3.10 or newer
- Tkinter (usually included with Python on Windows)
- Visual Studio Code

## Run the program
1. Extract this ZIP file to a folder.
2. Open the folder in Visual Studio Code.
3. Open `main.py`.
4. Select **Terminal → New Terminal**.
5. Run:

   ```bash
   python main.py
   ```

   If `python` is not recognized on Windows, try:

   ```bash
   py main.py
   ```

## How to use
1. Add a Physical Book or E-Book using the form at the top.
2. Register a patron with a unique ID.
3. Select an item and use Borrow or Return. Enter the registered patron ID.
4. Search titles, show all items, sort by title, or view item details.
5. Use File → Save data / Load data. Data is saved in the `data` folder as `books.json` and `patrons.json`.
6. The application attempts to save data when it closes.

## Assignment Two requirement mapping
- **Updated problem statement:** The original Campus Digital Library System is extended with persistent storage, exception handling and a GUI.
- **Polymorphism variant 1 — overriding:** `PhysicalBook.display_access_info()` and `EBook.display_access_info()` implement the abstract method differently.
- **Polymorphism variant 2 — operator overloading:** `LibraryItem.__str__()` customises the string representation; `LibraryItem.__lt__()` allows items to be sorted by title.
- **Polymorphism variant 3 — duck typing:** `LibraryBranch.process_item()` calls `get_details()` and `display_access_info()` through the common interface rather than branching on the item's concrete class.
- **Exception handling:** custom library exceptions and `try/except` blocks handle duplicate IDs, invalid data, missing records, unavailable items and file problems.
- **File writing:** `save_to_files()` writes books and patrons to JSON.
- **File reading:** `load_from_files()` reads JSON and recreates objects.
- **ADT:** Python lists store inventory, patrons, borrowed item IDs and chapters.
- **GUI:** Tkinter provides a menu bar, forms, buttons, dialogs and a table.
- **Original concepts:** inheritance (`PhysicalBook` and `EBook` inherit `LibraryItem`), composition (`PhysicalBook` owns `TableOfContents`), aggregation (`LibraryBranch` holds lists of items and patrons), searching and object type checking are retained.

## Testing checklist
- [ ] Add a valid physical book.
- [ ] Add a valid e-book.
- [ ] Attempt to add an item with an existing ID; confirm an error message.
- [ ] Register a patron.
- [ ] Attempt to register a duplicate patron ID; confirm an error message.
- [ ] Borrow an available item.
- [ ] Try to borrow that item again; confirm it is rejected.
- [ ] Return the item using the same patron ID.
- [ ] Search for a title.
- [ ] Sort items by title.
- [ ] Save data, close the application, reopen it, and confirm the data remains.
- [ ] View details for both a physical book and an e-book.

## Data and limitations
The application stores data locally in JSON files. It is a coursework demonstration, not a multi-user production library database. Keep the `data` folder with the program so saved records remain available.
