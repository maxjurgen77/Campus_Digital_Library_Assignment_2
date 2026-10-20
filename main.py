import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from abc import ABC, abstractmethod
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"
BOOKS_FILE = DATA_DIR / "books.json"
PATRONS_FILE = DATA_DIR / "patrons.json"


class LibraryError(Exception):
    """Base exception for library application errors."""


class DuplicateIDError(LibraryError):
    pass


class ItemUnavailableError(LibraryError):
    pass


class ItemNotFoundError(LibraryError):
    pass


class LibraryItem(ABC):
    def __init__(self, title, item_id, year):
        title = title.strip()
        item_id = item_id.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        if not item_id:
            raise ValueError("Item ID cannot be empty.")
        if not isinstance(year, int) or year < 0:
            raise ValueError("Year must be a non-negative integer.")

        self.title = title
        self.item_id = item_id
        self.year = year
        self.is_available = True
        self.borrowed_by = ""

    def get_details(self):
        status = "Available" if self.is_available else f"Borrowed by {self.borrowed_by}"
        return f"[{self.item_id}] {self.title} ({self.year}) - {status}"

    @abstractmethod
    def display_access_info(self):
        pass

    def to_dict(self):
        raise NotImplementedError("Subclasses must implement to_dict().")

    def __str__(self):
        # Polymorphism variant 2: operator/method overloading through __str__.
        return self.get_details()

    def __lt__(self, other):
        # Enables sorting LibraryItem objects by title.
        if not isinstance(other, LibraryItem):
            return NotImplemented
        return self.title.casefold() < other.title.casefold()


class PhysicalBook(LibraryItem):
    def __init__(self, title, item_id, year, shelf_location, page_count, chapters=None):
        super().__init__(title, item_id, year)
        self.shelf_location = shelf_location.strip()
        if not self.shelf_location:
            raise ValueError("Shelf location cannot be empty.")
        if not isinstance(page_count, int) or page_count < 1:
            raise ValueError("Page count must be a positive integer.")
        self.table_of_contents = TableOfContents(page_count, chapters or [])

    def display_access_info(self):
        # Polymorphism variant 1: overriding the superclass method.
        return f"Physical copy. Find it at shelf {self.shelf_location}."

    def get_shelf_info(self):
        return f"Shelf: {self.shelf_location}"

    def to_dict(self):
        return {
            "type": "physical", "title": self.title, "item_id": self.item_id,
            "year": self.year, "is_available": self.is_available,
            "borrowed_by": self.borrowed_by, "shelf_location": self.shelf_location,
            "page_count": self.table_of_contents.page_count,
            "chapters": self.table_of_contents.chapters
        }


class EBook(LibraryItem):
    def __init__(self, title, item_id, year, file_size_mb, download_link):
        super().__init__(title, item_id, year)
        if not isinstance(file_size_mb, (float, int)) or file_size_mb <= 0:
            raise ValueError("File size must be greater than zero.")
        self.file_size_mb = float(file_size_mb)
        self.download_link = download_link.strip()
        if not self.download_link:
            raise ValueError("Download link cannot be empty.")

    def display_access_info(self):
        # Polymorphism variant 1: same method name, different subclass behaviour.
        return f"Digital copy ({self.file_size_mb:g} MB). Link: {self.download_link}"

    def verify_format(self):
        return self.download_link.lower().split("?")[0].endswith((".pdf", ".epub"))

    def to_dict(self):
        return {
            "type": "ebook", "title": self.title, "item_id": self.item_id,
            "year": self.year, "is_available": self.is_available,
            "borrowed_by": self.borrowed_by, "file_size_mb": self.file_size_mb,
            "download_link": self.download_link
        }


class TableOfContents:
    # Composition: a PhysicalBook owns its TableOfContents.
    def __init__(self, page_count, chapters=None):
        self.page_count = page_count
        self.chapters = list(chapters or [])

    def add_chapter(self, chapter_name):
        chapter_name = chapter_name.strip()
        if not chapter_name:
            raise ValueError("Chapter name cannot be empty.")
        self.chapters.append(chapter_name)

    def get_summary(self):
        return f"Pages: {self.page_count}; Chapters: {len(self.chapters)}"


class Patron:
    def __init__(self, patron_id, name):
        self.patron_id = patron_id.strip()
        self.name = name.strip()
        if not self.patron_id or not self.name:
            raise ValueError("Patron ID and name cannot be empty.")
        self.borrowed_item_ids = []

    def to_dict(self):
        return {
            "patron_id": self.patron_id,
            "name": self.name,
            "borrowed_item_ids": self.borrowed_item_ids
        }


class LibraryBranch:
    def __init__(self, branch_name="Main Campus Library"):
        self.branch_name = branch_name
        # Lists are the Abstract Data Type (ADT) used for inventory and patrons.
        self.inventory = []
        self.patrons = []

    def add_item(self, item):
        if any(existing.item_id.casefold() == item.item_id.casefold()
               for existing in self.inventory):
            raise DuplicateIDError(f"An item with ID {item.item_id} already exists.")
        self.inventory.append(item)

    def register_patron(self, patron):
        if any(existing.patron_id.casefold() == patron.patron_id.casefold()
               for existing in self.patrons):
            raise DuplicateIDError(f"A patron with ID {patron.patron_id} already exists.")
        self.patrons.append(patron)

    def search_item(self, title):
        title = title.strip().casefold()
        if not title:
            raise ValueError("Enter a title or part of a title to search.")
        return [item for item in self.inventory if title in item.title.casefold()]

    def find_item(self, item_id):
        for item in self.inventory:
            if item.item_id.casefold() == item_id.strip().casefold():
                return item
        raise ItemNotFoundError(f"No item with ID {item_id} was found.")

    def find_patron(self, patron_id):
        for patron in self.patrons:
            if patron.patron_id.casefold() == patron_id.strip().casefold():
                return patron
        raise LibraryError(f"No patron with ID {patron_id} was found.")

    def count_available(self):
        return sum(1 for item in self.inventory if item.is_available)

    def process_item(self, item):
        # Polymorphism variant 3: duck typing. The caller uses the shared
        # display_access_info() interface without needing to branch on type.
        return f"{item.get_details()}\nAccess: {item.display_access_info()}"

    def borrow_item(self, item_id, patron_id):
        item = self.find_item(item_id)
        patron = self.find_patron(patron_id)
        if not item.is_available:
            raise ItemUnavailableError(f"'{item.title}' is already borrowed.")
        item.is_available = False
        item.borrowed_by = patron.patron_id
        patron.borrowed_item_ids.append(item.item_id)

    def return_item(self, item_id, patron_id):
        item = self.find_item(item_id)
        patron = self.find_patron(patron_id)
        if item.is_available or item.borrowed_by.casefold() != patron.patron_id.casefold():
            raise LibraryError("This item is not recorded as borrowed by that patron.")
        item.is_available = True
        item.borrowed_by = ""
        if item.item_id in patron.borrowed_item_ids:
            patron.borrowed_item_ids.remove(item.item_id)

    def save_to_files(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with BOOKS_FILE.open("w", encoding="utf-8") as file:
            json.dump([item.to_dict() for item in self.inventory], file, indent=4)
        with PATRONS_FILE.open("w", encoding="utf-8") as file:
            json.dump([patron.to_dict() for patron in self.patrons], file, indent=4)

    def load_from_files(self):
        # If the files do not exist yet, the application starts with empty lists.
        if BOOKS_FILE.exists():
            with BOOKS_FILE.open("r", encoding="utf-8") as file:
                book_data = json.load(file)
            loaded_items = []
            for data in book_data:
                if data.get("type") == "physical":
                    item = PhysicalBook(
                        data["title"], data["item_id"], int(data["year"]),
                        data["shelf_location"], int(data["page_count"]),
                        data.get("chapters", [])
                    )
                elif data.get("type") == "ebook":
                    item = EBook(
                        data["title"], data["item_id"], int(data["year"]),
                        float(data["file_size_mb"]), data["download_link"]
                    )
                else:
                    raise ValueError(f"Unknown item type for ID {data.get('item_id')}.")
                item.is_available = bool(data.get("is_available", True))
                item.borrowed_by = data.get("borrowed_by", "")
                loaded_items.append(item)
            self.inventory = loaded_items

        if PATRONS_FILE.exists():
            with PATRONS_FILE.open("r", encoding="utf-8") as file:
                patron_data = json.load(file)
            self.patrons = [
                Patron(data["patron_id"], data["name"]) for data in patron_data
            ]
            for patron, data in zip(self.patrons, patron_data):
                patron.borrowed_item_ids = data.get("borrowed_item_ids", [])


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Digital Library System")
        self.root.geometry("1050x680")
        self.library = LibraryBranch()
        try:
            self.library.load_from_files()
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as error:
            messagebox.showwarning(
                "File loading problem",
                f"Saved data could not be loaded. The system will start with empty data.\n\n{error}"
            )
            self.library = LibraryBranch()

        self._build_menu()
        self._build_interface()
        self.refresh_table()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def _build_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save data", command=self.save_data)
        file_menu.add_command(label="Load data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        patron_menu = tk.Menu(menu_bar, tearoff=0)
        patron_menu.add_command(label="Register patron", command=self.register_patron_dialog)
        menu_bar.add_cascade(label="Patrons", menu=patron_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
            "About", "Campus Digital Library System\nObject-Oriented Programming — Assignment Two"
        ))
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def _build_interface(self):
        heading = ttk.Label(self.root, text="Campus Digital Library System",
                            font=("Arial", 18, "bold"))
        heading.pack(pady=(12, 2))
        self.summary = ttk.Label(self.root, text="")
        self.summary.pack(pady=(0, 10))

        form = ttk.LabelFrame(self.root, text="Add a library item")
        form.pack(fill="x", padx=12, pady=6)

        self.kind_var = tk.StringVar(value="Physical Book")
        self.title_var = tk.StringVar()
        self.id_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.shelf_var = tk.StringVar()
        self.pages_var = tk.StringVar(value="100")
        self.size_var = tk.StringVar(value="5")
        self.link_var = tk.StringVar()

        fields = [
            ("Item type", self.kind_var, 0, 0),
            ("Title", self.title_var, 0, 2),
            ("Item ID", self.id_var, 0, 4),
            ("Year", self.year_var, 0, 6),
        ]
        for label, variable, row, col in fields:
            ttk.Label(form, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="w")
            if label == "Item type":
                widget = ttk.Combobox(form, textvariable=variable,
                                      values=("Physical Book", "E-Book"), state="readonly", width=16)
            else:
                widget = ttk.Entry(form, textvariable=variable, width=19)
            widget.grid(row=row, column=col + 1, padx=5, pady=5, sticky="ew")

        ttk.Label(form, text="Shelf location").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(form, textvariable=self.shelf_var, width=18).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form, text="Page count").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(form, textvariable=self.pages_var, width=18).grid(row=1, column=3, padx=5, pady=5)
        ttk.Label(form, text="File size (MB)").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        ttk.Entry(form, textvariable=self.size_var, width=18).grid(row=1, column=5, padx=5, pady=5)
        ttk.Label(form, text="Download link").grid(row=1, column=6, padx=5, pady=5, sticky="w")
        ttk.Entry(form, textvariable=self.link_var, width=25).grid(row=1, column=7, padx=5, pady=5)
        ttk.Button(form, text="Add item", command=self.add_item).grid(
            row=0, column=8, rowspan=2, padx=8, pady=5, sticky="ns"
        )

        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=12, pady=6)
        ttk.Label(search_frame, text="Search by title:").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=6)
        ttk.Button(search_frame, text="Search", command=self.search_items).pack(side="left", padx=3)
        ttk.Button(search_frame, text="Show all", command=self.refresh_table).pack(side="left", padx=3)
        ttk.Button(search_frame, text="Sort by title", command=self.sort_items).pack(side="left", padx=3)

        columns = ("id", "title", "type", "year", "status", "access")
        self.table = ttk.Treeview(self.root, columns=columns, show="headings", height=13)
        for col, label, width in [
            ("id", "Item ID", 90), ("title", "Title", 240), ("type", "Type", 115),
            ("year", "Year", 70), ("status", "Status", 150), ("access", "Access information", 330)
        ]:
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True, padx=12, pady=6)

        actions = ttk.LabelFrame(self.root, text="Library actions")
        actions.pack(fill="x", padx=12, pady=(4, 12))
        ttk.Button(actions, text="Register patron", command=self.register_patron_dialog).pack(
            side="left", padx=5, pady=8
        )
        ttk.Button(actions, text="Borrow selected item", command=self.borrow_dialog).pack(
            side="left", padx=5, pady=8
        )
        ttk.Button(actions, text="Return selected item", command=self.return_dialog).pack(
            side="left", padx=5, pady=8
        )
        ttk.Button(actions, text="View item details", command=self.view_details).pack(
            side="left", padx=5, pady=8
        )
        ttk.Button(actions, text="Save data", command=self.save_data).pack(
            side="right", padx=5, pady=8
        )

    def _selected_item_id(self):
        selection = self.table.selection()
        if not selection:
            raise LibraryError("Select an item from the table first.")
        return self.table.item(selection[0], "values")[0]

    def _selected_item(self):
        return self.library.find_item(self._selected_item_id())

    def add_item(self):
        try:
            title = self.title_var.get()
            item_id = self.id_var.get()
            year = int(self.year_var.get())
            if self.kind_var.get() == "Physical Book":
                item = PhysicalBook(title, item_id, year, self.shelf_var.get(),
                                    int(self.pages_var.get()))
            else:
                item = EBook(title, item_id, year, float(self.size_var.get()),
                             self.link_var.get())
            self.library.add_item(item)
            self.save_data(silent=True)
            self.refresh_table()
            for var in (self.title_var, self.id_var, self.year_var,
                        self.shelf_var, self.link_var):
                var.set("")
            messagebox.showinfo("Success", "Library item added and saved.")
        except (ValueError, LibraryError, OSError) as error:
            messagebox.showerror("Could not add item", str(error))

    def register_patron_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Register patron")
        dialog.resizable(False, False)
        patron_id_var, name_var = tk.StringVar(), tk.StringVar()
        ttk.Label(dialog, text="Patron ID").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ttk.Entry(dialog, textvariable=patron_id_var, width=28).grid(row=0, column=1, padx=10, pady=8)
        ttk.Label(dialog, text="Full name").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        ttk.Entry(dialog, textvariable=name_var, width=28).grid(row=1, column=1, padx=10, pady=8)

        def submit():
            try:
                self.library.register_patron(Patron(patron_id_var.get(), name_var.get()))
                self.save_data(silent=True)
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("Success", "Patron registered and saved.")
            except (ValueError, LibraryError, OSError) as error:
                messagebox.showerror("Could not register patron", str(error), parent=dialog)

        ttk.Button(dialog, text="Register", command=submit).grid(
            row=2, column=0, columnspan=2, pady=10
        )

    def _patron_id_dialog(self, action):
        item_id = self._selected_item_id()
        dialog = tk.Toplevel(self.root)
        dialog.title(action + " item")
        patron_id_var = tk.StringVar()
        ttk.Label(dialog, text="Enter registered patron ID:").pack(padx=12, pady=(12, 4))
        ttk.Entry(dialog, textvariable=patron_id_var, width=28).pack(padx=12, pady=4)

        def submit():
            try:
                if action == "Borrow":
                    self.library.borrow_item(item_id, patron_id_var.get())
                else:
                    self.library.return_item(item_id, patron_id_var.get())
                self.save_data(silent=True)
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("Success", f"Item {action.lower()} operation completed.")
            except (ValueError, LibraryError, OSError) as error:
                messagebox.showerror("Operation failed", str(error), parent=dialog)

        ttk.Button(dialog, text=action, command=submit).pack(pady=10)

    def borrow_dialog(self):
        try:
            self._patron_id_dialog("Borrow")
        except LibraryError as error:
            messagebox.showerror("Select item", str(error))

    def return_dialog(self):
        try:
            self._patron_id_dialog("Return")
        except LibraryError as error:
            messagebox.showerror("Select item", str(error))

    def search_items(self):
        try:
            results = self.library.search_item(self.search_var.get())
            self.refresh_table(results)
            if not results:
                messagebox.showinfo("Search", "No matching titles were found.")
        except ValueError as error:
            messagebox.showerror("Search", str(error))

    def sort_items(self):
        self.refresh_table(sorted(self.library.inventory))

    def refresh_table(self, items=None):
        for row in self.table.get_children():
            self.table.delete(row)
        for item in (self.library.inventory if items is None else items):
            kind = "Physical Book" if isinstance(item, PhysicalBook) else "E-Book"
            status = "Available" if item.is_available else f"Borrowed by {item.borrowed_by}"
            self.table.insert("", "end", values=(
                item.item_id, item.title, kind, item.year, status, item.display_access_info()
            ))
        self.summary.config(
            text=f"Branch: {self.library.branch_name} | Total items: {len(self.library.inventory)}"
                 f" | Available: {self.library.count_available()} | Registered patrons: {len(self.library.patrons)}"
        )

    def view_details(self):
        try:
            item = self._selected_item()
            details = self.library.process_item(item)
            if isinstance(item, PhysicalBook):
                details += "\n" + item.table_of_contents.get_summary()
            elif isinstance(item, EBook):
                details += f"\nSupported file format: {'Yes' if item.verify_format() else 'Not verified'}"
            messagebox.showinfo("Item details", details)
        except LibraryError as error:
            messagebox.showerror("Item details", str(error))

    def save_data(self, silent=False):
        try:
            self.library.save_to_files()
            if not silent:
                messagebox.showinfo("Saved", f"Data saved to:\n{DATA_DIR}")
        except OSError as error:
            messagebox.showerror("File error", f"Data could not be saved.\n\n{error}")

    def load_data(self):
        try:
            self.library.load_from_files()
            self.refresh_table()
            messagebox.showinfo("Loaded", "Saved books and patrons have been loaded.")
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as error:
            messagebox.showerror("File error", f"Data could not be loaded.\n\n{error}")

    def close_app(self):
        try:
            self.library.save_to_files()
        except OSError as error:
            if not messagebox.askyesno(
                "Save failed", f"Could not save data:\n{error}\n\nExit without saving?"
            ):
                return
        self.root.destroy()


def main():
    root = tk.Tk()
    LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
