import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue
import csv

class BookNode:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None

class BookBST:
    def __init__(self):
        self.root = None

    def insert(self, book):
        if not self.root:
            self.root = BookNode(book)
        else:
            self._insert(self.root, book)

    def _insert(self, node, book):
        if book.title < node.book.title:
            if node.left:
                self._insert(node.left, book)
            else:
                node.left = BookNode(book)
        else:
            if node.right:
                self._insert(node.right, book)  
            else:
                node.right = BookNode(book)

    def search(self, title):
        return self._search(self.root, title.lower())

    def _search(self, node, title):
        if not node:
            return []
        if title in node.book.title.lower():
            return [node.book] + self._search(node.left, title) + self._search(node.right, title)
        elif title < node.book.title.lower():
            return self._search(node.left, title)
        else:
            return self._search(node.right, title)

    def in_order(self):
        books = []
        self._in_order(self.root, books)
        return books

    def _in_order(self, node, books):
        if node:
            self._in_order(node.left, books)
            books.append(node.book)
            self._in_order(node.right, books)

    def _remove_book(self, node, book_id):
        """Helper method to remove a book from the BST."""
        if not node:
            return None

        # Compare book_id as strings (since book_id is stored as a string)
        if book_id < node.book.book_id:
            node.left = self._remove_book(node.left, book_id)
        elif book_id > node.book.book_id:
            node.right = self._remove_book(node.right, book_id)
        else:
            # Node to be deleted found
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            # Node with two children: Get the inorder successor (smallest in the right subtree)
            min_larger_node = self._get_min(node.right)
            node.book = min_larger_node.book
            node.right = self._remove_book(node.right, min_larger_node.book.book_id)
        return node

    def _get_min(self, node):
        """Helper method to find the minimum node in a BST."""
        while node.left:
            node = node.left
        return node

class Book:
    def __init__(self, title, author, book_id):
        self.title = title
        self.author = author
        self.book_id = book_id
        self.available = True
        self.borrowed_by = None
        self.due_date = None
        self.waiting_list = []  # Use a list instead of Queue
        self.borrow_count = 0

class Member:
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
        self.books_borrowed = []

class Library:
    def __init__(self):
        self.books = BookBST()
        self.members = {}
        self.next_book_id = 1
        self.next_member_id = 1

    def add_book(self, title, author):
        book_id = str(self.next_book_id)
        self.next_book_id += 1
        book = Book(title, author, book_id)
        self.books.insert(book)
        return book_id

    def add_member(self, name):
        member_id = str(self.next_member_id)
        self.next_member_id += 1
        self.members[member_id] = Member(name, member_id)
        return member_id

    def borrow_book(self, book_title, member_id, days=14):
        if member_id not in self.members:
            return False, "Member Not Found"

        member = self.members[member_id]
        books = self.books.search(book_title)

        for book in books:
            if book.available:
                book.available = False
                book.borrowed_by = member_id
                book.due_date = datetime.datetime.now().date() + datetime.timedelta(days=days)
                member.books_borrowed.append(book.book_id)  # Track borrowed books in the member object
                book.borrow_count += 1  # Increment borrow count
                return True, f"Book '{book.title}' borrowed successfully!"

        # Add to waiting list
        books[0].waiting_list.append(member_id)
        return False, f"Book is currently unavailable. Added to the waiting list."

    def return_book(self, book_id, member_id):
        print(f"Attempting to return Book ID: {book_id} by Member ID: {member_id}")  # Debug print
        for book in self.books.in_order():
            print(f"Book ID: {book.book_id}, Borrowed By: {book.borrowed_by}")  # Debug print
            if book.book_id == book_id and book.borrowed_by == member_id:
                book.available = True
                book.borrowed_by = None
                book.due_date = None
                self.members[member_id].books_borrowed.remove(book_id)  # Remove the book from the member's borrowed list

                if book.waiting_list:
                    # Get the next member from the waiting list
                    next_member_id = book.waiting_list.pop(0)
                    self.borrow_book(book.title, next_member_id)

                return True, 'Book returned successfully.'
        return False, 'Book not found or invalid member ID.'

    def list_books(self):
        return self.books.in_order()

    def get_most_borrowed_books(self, top_n=5):
        """Get the top N most borrowed books."""
        all_books = self.books.in_order()
        sorted_books = sorted(all_books, key=lambda book: book.borrow_count, reverse=True)
        return sorted_books[:top_n]

    def save_books_to_csv(self, filename="books.csv"):
        """Save all books to a CSV file."""
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(["book_id", "title", "author", "available", "borrowed_by", "due_date", "borrow_count"])
            # Write book data
            for book in self.books.in_order():
                writer.writerow([
                    book.book_id,
                    book.title,
                    book.author,
                    book.available,
                    book.borrowed_by,
                    book.due_date.strftime('%Y-%m-%d') if book.due_date else "",
                    book.borrow_count
                ])

    def load_books_from_csv(self, filename="books.csv"):
        """Load books from a CSV file."""
        try:
            with open(filename, mode="r") as file:
                reader = csv.DictReader(file)
                max_book_id = 0  # Track the highest book ID
                for row in reader:
                    book = Book(
                        title=row["title"],
                        author=row["author"],
                        book_id=row["book_id"]
                    )
                    book.available = row["available"] == "True"
                    book.borrowed_by = row["borrowed_by"] if row["borrowed_by"] else None
                    book.due_date = datetime.datetime.strptime(row["due_date"], "%Y-%m-%d").date() if row["due_date"] else None
                    book.borrow_count = int(row["borrow_count"])
                    self.books.insert(book)

                    # Update max_book_id
                    max_book_id = max(max_book_id, int(book.book_id))

                # Set next_book_id to the highest book ID + 1
                self.next_book_id = max_book_id + 1
        except FileNotFoundError:
            pass  # If the file doesn't exist, start with an empty library

    def save_members_to_csv(self, filename="members.csv"):
        """Save all members to a CSV file."""
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(["member_id", "name", "books_borrowed"])
            # Write member data
            for member_id, member in self.members.items():
                writer.writerow([
                    member_id,
                    member.name,
                    ",".join(member.books_borrowed)  # Save borrowed books as a comma-separated string
                ])

    def load_members_from_csv(self, filename="members.csv"):
        """Load members from a CSV file."""
        try:
            with open(filename, mode="r") as file:
                reader = csv.DictReader(file)
                max_member_id = 0  # Track the highest member ID
                for row in reader:
                    member = Member(
                        name=row["name"],
                        member_id=row["member_id"]
                    )
                    # Load borrowed books as a list
                    member.books_borrowed = row["books_borrowed"].split(",") if row["books_borrowed"] else []
                    self.members[member.member_id] = member

                    # Update max_member_id
                    max_member_id = max(max_member_id, int(member.member_id))

                # Set next_member_id to the highest member ID + 1
                self.next_member_id = max_member_id + 1
        except FileNotFoundError:
            pass  # If the file doesn't exist, start with an empty member list

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x500")

        self.library = Library()

        # Load data from CSV files
        self.library.load_books_from_csv()
        self.library.load_members_from_csv()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Reorder the tabs: Lending first, Members second, Books last
        self.create_lending_tab()  # Lending Page is now the first tab
        self.create_members_tab()  # Members Page remains the second tab
        self.create_books_tab()    # Books Page is now the last tab

        # Refresh the UI to display the loaded data
        self.load_books()
        self.load_members()
        self.load_available_books()

    def create_books_tab(self):
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books")

        # Add a search bar
        search_frame = ttk.Frame(books_frame)
        search_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(search_frame, text="Search Book:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_book_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_book_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search_frame, text="Search", command=self.search_books).grid(row=0, column=2, padx=5, pady=5)

        add_frame = ttk.Frame(books_frame)
        add_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(add_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Author:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.author_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.author_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="Add Book", command=self.add_book).grid(row=2, column=0, columnspan=2, pady=10)

        list_frame = ttk.Frame(books_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ('id', 'title', 'author', 'status')
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        self.books_tree.heading('id', text="ID")
        self.books_tree.heading('title', text='Title')
        self.books_tree.heading('author', text='Author')
        self.books_tree.heading('status', text='Status')

        self.books_tree.column('id', width=50)
        self.books_tree.column('title', width=200)
        self.books_tree.column('author', width=150)
        self.books_tree.column('status', width=100)

        self.books_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.books_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.books_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(books_frame, text="Show All Books", command=self.load_books).pack(pady=10)

        self.load_books()

    def create_members_tab(self):
        member_frame = ttk.Frame(self.notebook)
        self.notebook.add(member_frame, text="Members")

        # Add a search bar
        search_frame = ttk.Frame(member_frame)
        search_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(search_frame, text="Search Member:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_member_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_member_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search_frame, text="Search", command=self.search_members).grid(row=0, column=2, padx=5, pady=5)

        add_member_frame = ttk.Frame(member_frame)
        add_member_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(add_member_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.member_name_var = tk.StringVar()
        ttk.Entry(add_member_frame, textvariable=self.member_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(add_member_frame, text="Add Member", command=self.add_member).grid(row=1, column=0, columnspan=2, pady=10)

        list_frame = ttk.Frame(member_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ('id', 'name', 'books_borrowed')
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        self.members_tree.heading('id', text="ID")
        self.members_tree.heading('name', text="Name")
        self.members_tree.heading('books_borrowed', text="Books Borrowed")

        self.members_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.members_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.members_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(member_frame, text="Show All Members", command=self.load_members).pack(pady=10)

        # Add Delete Button
        ttk.Button(member_frame, text="Delete Member", command=self.delete_member).pack(pady=10)

        self.load_members()

    def create_lending_tab(self):
        lending_frame = ttk.Frame(self.notebook)
        self.notebook.add(lending_frame, text="Lending")

        # Borrow Book Section
        borrow_frame = ttk.Frame(lending_frame)
        borrow_frame.pack(padx=10, pady=10, fill="x")

        # Book Title field
        ttk.Label(borrow_frame, text="Book Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.borrow_book_title_var = tk.StringVar()
        self.borrow_book_id_var = tk.StringVar()
        self.borrow_book_title_var.trace("w", self.update_book_id)  # Trigger update when text changes
        ttk.Entry(borrow_frame, textvariable=self.borrow_book_title_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Member ID field
        ttk.Label(borrow_frame, text="Member ID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.borrow_member_id_var = tk.StringVar()
        ttk.Entry(borrow_frame, textvariable=self.borrow_member_id_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        # Borrow Book button
        ttk.Button(borrow_frame, text="Borrow Book", command=self.borrow_book).grid(row=2, column=0, columnspan=2, pady=10)

        # Return Book Section
        return_frame = ttk.Frame(lending_frame)
        return_frame.pack(padx=10, pady=10, fill="x")

        # Book Title field for returning books
        ttk.Label(return_frame, text="Book Title:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.return_book_title_var = tk.StringVar()
        self.return_book_title_var.trace("w", self.update_return_book_id)  # Trigger update when text changes
        ttk.Entry(return_frame, textvariable=self.return_book_title_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Book ID Display (Read-only)
        ttk.Label(return_frame, text="Book ID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.return_book_id_var = tk.StringVar()
        book_id_entry = ttk.Entry(return_frame, textvariable=self.return_book_id_var, width=30, state="readonly")
        book_id_entry.grid(row=1, column=1, padx=5, pady=5)

        # Member ID field for returning books
        ttk.Label(return_frame, text="Member ID:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.return_member_id_var = tk.StringVar()
        ttk.Entry(return_frame, textvariable=self.return_member_id_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        # Return Book button
        ttk.Button(return_frame, text="Return Book", command=self.return_book).grid(row=3, column=0, columnspan=2, pady=10)

        # Available Books Section
        available_books_frame = ttk.Frame(lending_frame)
        available_books_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add the search bar to the right side
        search_frame = ttk.Frame(available_books_frame)
        search_frame.pack(side="right", padx=10, pady=10, fill="y")

        ttk.Label(search_frame, text="Search Book:").pack(anchor="w", padx=5, pady=5)
        self.search_lending_book_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_lending_book_var, width=30).pack(anchor="w", padx=5, pady=5)
        ttk.Button(search_frame, text="Search", command=self.search_lending_books).pack(anchor="w", padx=5, pady=5)

        # Available Books Treeview
        columns = ('id', 'title', 'author')
        self.available_books_tree = ttk.Treeview(available_books_frame, columns=columns, show='headings')

        self.available_books_tree.heading('id', text="ID")
        self.available_books_tree.heading('title', text="Title")
        self.available_books_tree.heading('author', text="Author")

        self.available_books_tree.column('id', width=50)
        self.available_books_tree.column('title', width=200)
        self.available_books_tree.column('author', width=150)

        self.available_books_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(available_books_frame, orient="vertical", command=self.available_books_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.available_books_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(lending_frame, text="Show All Available Books", command=self.load_available_books).pack(pady=10)

        self.load_available_books()

    def load_books(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        for book in self.library.list_books():
            status = "Available" if book.available else "Borrowed"
            self.books_tree.insert('', 'end', values=(book.book_id, book.title, book.author, status))

    def load_members(self):
        """Load all members into the Treeview with borrowed books and return dates displayed."""
        # Clear the Treeview
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)

        # Insert members into the Treeview
        for member_id, member in self.library.members.items():
            if member.books_borrowed:
                books_borrowed = ", ".join(
                    f"{book_id}: {next(book.title for book in self.library.list_books() if book.book_id == book_id)} "
                    f"(Due: {next(book.due_date.strftime('%Y-%m-%d') for book in self.library.list_books() if book.book_id == book_id)})"
                    for book_id in member.books_borrowed
                )
            else:
                books_borrowed = "None"
            self.members_tree.insert('', 'end', values=(member_id, member.name, books_borrowed))

    def load_available_books(self):
        """Load all available books into the Treeview."""
        # Clear the Treeview
        for item in self.available_books_tree.get_children():
            self.available_books_tree.delete(item)

        # Insert available books into the Treeview
        for book in self.library.list_books():
            if book.available:
                self.available_books_tree.insert('', 'end', values=(book.book_id, book.title, book.author))

    def add_book(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()

        if not title or not author:
            messagebox.showwarning("Input Error", "Title and Author are required!")
            return

        book_id = self.library.add_book(title, author)
        messagebox.showinfo("Success", f"Book added with ID: {book_id}")
        self.library.save_books_to_csv()  # Save books to CSV
        self.load_books()  # Refresh the Books Tab

        # Clear the text boxes
        self.title_var.set("")
        self.author_var.set("")

    def add_member(self):
        name = self.member_name_var.get().strip()

        if not name:
            messagebox.showwarning("Input Error", "Member name is required!")
            return

        member_id = self.library.add_member(name)
        messagebox.showinfo("Success", f"Member added with ID: {member_id}")
        self.library.save_members_to_csv()  # Save members to CSV
        self.load_members()  # Refresh the Members Tab

        # Clear the text box
        self.member_name_var.set("")

    def borrow_book(self):
        book_title = self.borrow_book_title_var.get().strip()
        member_id = self.borrow_member_id_var.get().strip()

        if not book_title or not member_id:
            messagebox.showwarning("Input Error", "Book title and Member ID are required!")
            return

        success, message = self.library.borrow_book(book_title, member_id)
        if success:
            # Retrieve the borrowed book and member details
            books = self.library.books.search(book_title)
            member = self.library.members.get(member_id)
            if not member:
                messagebox.showerror("Error", "Member not found!")
                return

            for book in books:
                if book.borrowed_by == member_id:
                    due_date = book.due_date.strftime('%Y-%m-%d')  # Format the due date
                    # Create a receipt-like message
                    receipt = (
                        f"--- Borrow Receipt ---\n"
                        f"Member Name: {member.name}\n"
                        f"Member ID: {member_id}\n"
                        f"Book Title: {book.title}\n"
                        f"Return Date: {due_date}\n"
                        f"-----------------------"
                    )
                    messagebox.showinfo("Borrow Successful", receipt)
                    break
        else:
            # Handle the case where the book is unavailable
            books = self.library.books.search(book_title)
            if books:
                book = books[0]
                queue_position = len(book.waiting_list)  # Calculate the queue position
                member = self.library.members.get(member_id)
                if not member:
                    messagebox.showerror("Error", "Member not found!")
                    return

                # Create a receipt-like message for the waiting list
                receipt = (
                    f"--- Waiting List Receipt ---\n"
                    f"Member Name: {member.name}\n"
                    f"Member ID: {member_id}\n"
                    f"Book Title: {book.title}\n"
                    f"Queue Position: {queue_position}\n"
                    f"-----------------------------\n"
                    f"Do you want to cancel your request?"
                )

                # Create a custom dialog for canceling the request
                if messagebox.askyesno("Book Unavailable", receipt):
                    # If the user chooses to cancel, remove them from the waiting list
                    book.waiting_list.remove(member_id)
                    messagebox.showinfo("Request Canceled", "Your request to borrow the book has been canceled.")
                else:
                    messagebox.showinfo("Request Confirmed", "You have been added to the waiting list.")

        self.library.save_books_to_csv()  # Save books to CSV
        self.library.save_members_to_csv()  # Save members to CSV
        self.load_books()  # Refresh the Books Tab
        self.load_members()  # Refresh the Members Tab
        self.load_available_books()  # Refresh the Available Books section

        # Clear the text boxes
        self.borrow_book_title_var.set("")
        self.borrow_member_id_var.set("")

    def return_book(self):
        book_id = self.return_book_id_var.get().strip()
        member_id = self.return_member_id_var.get().strip()

        if not book_id or not member_id:
            messagebox.showwarning("Input Error", "Book ID and Member ID are required!")
            return

        success, message = self.library.return_book(book_id, member_id)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

        self.library.save_books_to_csv()  # Save books to CSV
        self.library.save_members_to_csv()  # Save members to CSV
        self.load_books()  # Refresh the Books Tab
        self.load_members()  # Refresh the Members Tab
        self.load_available_books()  # Refresh the Available Books section

        # Clear the text boxes
        self.return_book_id_var.set("")
        self.return_book_title_var.set("")
        self.return_member_id_var.set("")

    def show_most_borrowed_books(self):
        """Display the top 3 most borrowed books."""
        most_borrowed_books = self.library.get_most_borrowed_books(top_n=3)  # Limit to top 3 books

        if not most_borrowed_books:
            messagebox.showinfo("Most Borrowed Books", "No books have been borrowed yet.")
            return

        message = "Top 3 Most Borrowed Books:\n"
        for book in most_borrowed_books:
            message += f"- {book.title} by {book.author} (Borrowed {book.borrow_count} times)\n"

        messagebox.showinfo("Most Borrowed Books", message)

    def load_status(self):
        """Load the status of all books into the Treeview."""
        # Clear the Treeview
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)

        # Insert books into the Treeview
        for book in self.library.list_books():
            status = "Available" if book.available else "Borrowed"
            self.status_tree.insert('', 'end', values=(book.book_id, book.title, book.author, status))

    def update_book_id(self, *args):
        """Update the Book ID field based on the entered book title."""
        book_title = self.borrow_book_title_var.get().strip()
        if not book_title:
            self.borrow_book_id_var.set("")  # Clear the Book ID field if no title is entered
            return

        # Search for the book by title
        books = self.library.books.search(book_title)
        if books:
            self.borrow_book_id_var.set(books[0].book_id)  # Display the first matching book's ID
        else:
            self.borrow_book_id_var.set("Not Found")  # Display "Not Found" if no match

    def update_book_title(self, *args):
        """Update the Book Title field based on the entered book ID."""
        book_id = self.return_book_id_var.get().strip()
        if not book_id:
            self.return_book_title_var.set("")  # Clear the Book Title field if no ID is entered
            return

        # Search for the book by ID
        for book in self.library.list_books():
            if book.book_id == book_id:
                self.return_book_title_var.set(book.title)  # Display the matching book's title
                return

        self.return_book_title_var.set("Not Found")  # Display "Not Found" if no match

    def update_return_book_id(self, *args):
        """Update the Book ID field based on the entered book title in the Return Section."""
        book_title = self.return_book_title_var.get().strip()
        if not book_title:
            self.return_book_id_var.set("")  # Clear the Book ID field if no title is entered
            return

        # Search for the book by title
        books = self.library.books.search(book_title)
        if books:
            self.return_book_id_var.set(books[0].book_id)  # Display the first matching book's ID
        else:
            self.return_book_id_var.set("Not Found")  # Display "Not Found" if no match

    def search_members(self):
        """Search for members by name or ID and display the results."""
        query = self.search_member_var.get().strip().lower()
        if not query:
            self.load_members()  # If the search bar is empty, reload all members
            return

        # Clear the Treeview
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)

        # Search for members by name or ID
        for member_id, member in self.library.members.items():
            if query in member_id.lower() or query in member.name.lower():
                if member.books_borrowed:
                    books_borrowed = ", ".join(
                        f"{book_id}: {next(book.title for book in self.library.list_books() if book.book_id == book_id)}"
                        f"(Due: {next(book.due_date.strftime('%Y-%m-%d') for book in self.library.list_books() if book.book_id == book_id)})"
                        for book_id in member.books_borrowed
                    )
                else:
                    books_borrowed = "None"
                self.members_tree.insert('', 'end', values=(member_id, member.name, books_borrowed))

        # Clear the search bar
        self.search_member_var.set("")

    def search_books(self):
        """Search for books by title or author and display the results."""
        query = self.search_book_var.get().strip().lower()
        if not query:
            self.load_books()  # If the search bar is empty, reload all books
            return

        # Clear the Treeview
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)

        # Search for books by title or author
        for book in self.library.list_books():
            if query in book.title.lower() or query in book.author.lower():
                status = "Available" if book.available else "Borrowed"
                self.books_tree.insert('', 'end', values=(book.book_id, book.title, book.author, status))

        # Clear the search bar
        self.search_book_var.set("")

    def delete_member(self):
        selected_item = self.members_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No member selected!")
            return

        member_id = self.members_tree.item(selected_item, "values")[0]
        if member_id in self.library.members:
            del self.library.members[member_id]
            self.library.save_members_to_csv()  # Save updated members to CSV
            self.load_members()  # Refresh the Members Tab
            messagebox.showinfo("Success", f"Member with ID {member_id} deleted successfully!")
        else:
            messagebox.showerror("Error", "Member not found!")

    def _remove_book(self, node, book_id):
        """Helper method to remove a book from the BST."""
        if not node:
            return None

        # Compare book_id as strings (since book_id is stored as a string)
        if book_id < node.book.book_id:
            node.left = self._remove_book(node.left, book_id)
        elif book_id > node.book.book_id:
            node.right = self._remove_book(node.right, book_id)
        else:
            # Node to be deleted found
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            # Node with two children: Get the inorder successor (smallest in the right subtree)
            min_larger_node = self._get_min(node.right)
            node.book = min_larger_node.book
            node.right = self._remove_book(node.right, min_larger_node.book.book_id)
        return node

    def _get_min(self, node):
        """Helper method to find the minimum node in a BST."""
        while node.left:
            node = node.left
        return node

    def print_books(self):
        books = self.library.books.in_order()
        for book in books:
            print(f"Book ID: {book.book_id}, Title: {book.title}")

    def search_lending_books(self):
        """Search for books by title or author in the Lending Page and display the results."""
        query = self.search_lending_book_var.get().strip().lower()
        if not query:
            self.load_available_books()  # If the search bar is empty, reload all available books
            return

        # Clear the Treeview
        for item in self.available_books_tree.get_children():
            self.available_books_tree.delete(item)

        # Search for books by title or author
        for book in self.library.list_books():
            if book.available and (query in book.title.lower() or query in book.author.lower()):
                self.available_books_tree.insert('', 'end', values=(book.book_id, book.title, book.author))

        # Clear the search bar
        self.search_lending_book_var.set("")

root = tk.Tk()
app = LibraryApp(root)
root.mainloop()


















