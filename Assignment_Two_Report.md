# Object-Oriented Programming — Assignment Two
## Campus Digital Library System

### 1. Updated Problem Statement

The University of Namibia requires a Campus Digital Library System to manage physical books, electronic books and registered library patrons. The system must allow a librarian to add and search for books, register patrons, lend available items, record returns, and view item details. It must preserve book and patron information in files so that records remain available after the program is closed.

The application is developed in Python and uses a graphical user interface. It extends the original Assignment One design by adding three demonstrated variants of polymorphism, exception handling, file reading and writing, and an Abstract Data Type. The original object-oriented relationships are retained: `LibraryItem` is the superclass of `PhysicalBook` and `EBook`; a `PhysicalBook` owns a `TableOfContents`; and `LibraryBranch` aggregates collections of items and patrons.

### 2. Class Design

- **LibraryItem:** Abstract superclass containing the item ID, title, year, availability and borrowing status.
- **PhysicalBook:** Subclass with shelf location, page count and table of contents.
- **EBook:** Subclass with file size and download link.
- **TableOfContents:** Stores page count and chapter names; it is composed within a physical book.
- **Patron:** Stores patron information and the IDs of borrowed items.
- **LibraryBranch:** Manages item and patron lists, searching, borrowing, returning, and file operations.
- **LibraryApp:** Builds the Tkinter graphical interface and connects the buttons and menus to system operations.

### 3. Polymorphism — Three Variants

1. **Method overriding:** `PhysicalBook` and `EBook` each override `display_access_info()`. A physical book reports its shelf location, while an e-book reports its digital download link.
2. **Operator overloading:** `LibraryItem.__str__()` defines the text representation of an item. `LibraryItem.__lt__()` defines title-based comparison, allowing the objects to be sorted.
3. **Duck typing:** `LibraryBranch.process_item()` calls `get_details()` and `display_access_info()` using the common interface. The method relies on the object's supported behaviour rather than requiring a separate implementation for every concrete item type.

### 4. Exception Handling

The program defines `LibraryError`, `DuplicateIDError`, `ItemUnavailableError` and `ItemNotFoundError`. These exceptions report invalid library operations. Input conversion and validation errors are caught and displayed through GUI message boxes. File operations handle operating-system errors and invalid JSON data. The program prevents duplicate item and patron IDs, rejects attempts to borrow unavailable items, and checks that a returned item belongs to the specified patron.

### 5. File Handling

The system writes item records to `data/books.json` and patron records to `data/patrons.json`. The `save_to_files()` method uses JSON serialization to save data. The `load_from_files()` method reads the JSON records and reconstructs the relevant Python objects. If no files exist on the first run, the system starts with empty collections. The GUI provides Save and Load commands, and the application attempts to save when it closes.

### 6. Abstract Data Type

Python lists are used as the collection ADT. `LibraryBranch.inventory` stores library items, `LibraryBranch.patrons` stores patrons, `Patron.borrowed_item_ids` stores borrowed item IDs, and `TableOfContents.chapters` stores chapter names. The application uses list operations to add, remove, search and iterate through these records.

### 7. Graphical User Interface

The program uses Tkinter. The main window includes:
- a menu bar with File, Patrons and Help menus;
- a form to add a physical book or e-book;
- search, show-all and sort buttons;
- a table displaying item IDs, titles, types, years, status and access information;
- buttons to register patrons, borrow or return selected items, view details and save data;
- dialog boxes for user input, confirmation and error messages.

### 8. Testing Plan

The application should be tested by adding each item type, searching and sorting items, registering patrons, borrowing and returning items, checking duplicate IDs, attempting to borrow an unavailable item, viewing details, and saving and reloading data. The testing checklist is included in `README.md`.

### 9. How to Run

Open the project folder in Visual Studio Code and run `python main.py` in the integrated terminal. On Windows, `py main.py` may be used if the `python` command is unavailable. Python 3.10 or newer is recommended.

### 10. Conclusion

The updated Campus Digital Library System extends Assignment One with three identifiable polymorphism variants, exception handling, JSON file storage, list-based ADTs and a graphical interface. It retains the original inheritance, composition, aggregation, searching and object-type checking requirements.
