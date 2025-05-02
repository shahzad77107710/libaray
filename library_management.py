import streamlit as st
import datetime

# -----------------------------
# Book and Library Classes
# -----------------------------
class Book:
    def __init__(self, book_id, title, available=True, on_rent="No", rented_by="-------", rent_date="-------"):
        self.book_id = book_id
        self.title = title
        self.available = available
        self.on_rent = on_rent
        self.rented_by = rented_by
        self.rent_date = rent_date

    def get_rental_days(self):
        if self.rent_date == "-------":
            return 0
        rent_time = datetime.datetime.strptime(self.rent_date, '%Y-%m-%d %H:%M:%S')
        return (datetime.datetime.now() - rent_time).days

class Library:
    def __init__(self):
        self.books = [
            Book(1, "Python Basics"),
            Book(2, "AI & ML", False, "Yes", "Abdul Rehman", "2025-04-10 14:30:00"),
            Book(3, "Data Science", False, "Yes", "Abdul Samad", "2025-04-15 10:15:00"),
            Book(4, "Web Development"),
            Book(5, "Cyber Security")
        ]
        self.admin_username = "admin"
        self.admin_password = "1234"

    def find_book(self, book_id):
        return next((b for b in self.books if b.book_id == book_id), None)

    def rent_book(self, book_id, customer_name):
        book = self.find_book(book_id)
        if book and book.available:
            book.available = False
            book.on_rent = "Yes"
            book.rented_by = customer_name
            book.rent_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return True, book
        return False, None

    def return_book(self, book_id, return_days):
        book = self.find_book(book_id)
        if not book or book.available:
            return None, None, None

        days_late = max(0, return_days - 5)
        fine = 0 if days_late <= 0 else (days_late * 10 if days_late <= 10 else 1000)

        previous_renter = book.rented_by
        book.available = True
        book.on_rent = "No"
        book.rented_by = "-------"
        book.rent_date = "-------"

        return fine, previous_renter, book

    def add_book(self, title):
        if not title.strip():
            return None
        new_id = max(book.book_id for book in self.books) + 1 if self.books else 1
        new_book = Book(new_id, title)
        self.books.append(new_book)
        return new_id

    def delete_book(self, book_id):
        book = self.find_book(book_id)
        if book and book.available:
            self.books.remove(book)
            return True
        return False

    def authenticate_admin(self, username, password):
        return username == self.admin_username and password == self.admin_password


# -----------------------------
# Initialize Session State
# -----------------------------
if 'library' not in st.session_state:
    st.session_state.library = Library()

library = st.session_state.library

# -----------------------------
# UI Layout
# -----------------------------
st.set_page_config(page_title="📚 Library Management System", layout="wide")
st.markdown("<h1 style='text-align: center; color: navy;'>📚 Library Management System</h1>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("📋 Main Menu", ["📖 View Books", "📕 Rent Book", "📗 Return Book", "➕ Add Book (Admin)", "🗑️ Delete Book (Admin)"])

# -----------------------------
# View All Books
# -----------------------------
if menu == "📖 View Books":
    st.subheader("📚 All Books in Library")
    book_data = [{
        "ID": book.book_id,
        "Title": book.title,
        "Status": "✅ Available" if book.available else "❌ Not Available",
        "On Rent": book.on_rent,
        "Rent Date": book.rent_date,
        "Rented By": book.rented_by
    } for book in library.books]
    st.dataframe(book_data, use_container_width=True)

# -----------------------------
# Rent a Book
# -----------------------------
elif menu == "📕 Rent Book":
    st.subheader("📌 Rent a Book")
    available_books = [book for book in library.books if book.available]
    if available_books:
        book_titles = {f"{book.book_id} - {book.title}": book.book_id for book in available_books}
        col1, col2 = st.columns(2)
        with col1:
            selection = st.selectbox("📗 Choose a Book", list(book_titles.keys()))
        with col2:
            customer_name = st.text_input("👤 Enter Your Name")

        if st.button("📝 Rent Now"):
            if customer_name.strip():
                success, book = library.rent_book(book_titles[selection], customer_name)
                if success:
                    rent_date = datetime.datetime.now()
                    return_date = rent_date + datetime.timedelta(days=5)
                    st.success("✅ Book rented successfully!")
                    st.info(f"📅 Return By: {return_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.info("💸 Rental Fee: Rs. 50")
                else:
                    st.error("❌ Failed to rent the book.")
            else:
                st.warning("⚠️ Please enter your name.")
    else:
        st.info("ℹ️ No books currently available for rent.")

# -----------------------------
# Return a Book
# -----------------------------
elif menu == "📗 Return Book":
    st.subheader("📤 Return a Book")
    rented_books = [book for book in library.books if not book.available]
    if rented_books:
        book_titles = {f"{book.book_id} - {book.title} (by {book.rented_by})": book.book_id for book in rented_books}
        selection = st.selectbox("Select the Book to Return", list(book_titles.keys()))
        book_id = book_titles[selection]
        book = library.find_book(book_id)
        actual_days = book.get_rental_days()
        return_days = st.number_input("📆 Enter Total Days Book Was Rented", min_value=actual_days, value=actual_days)
        if st.button("🔄 Return Book"):
            fine, renter, returned_book = library.return_book(book_id, return_days)
            if fine is not None:
                st.success("✅ Book returned successfully.")
                st.markdown(f"""
                **Book Title:** {returned_book.title}  
                **Rented By:** {renter}  
                **Rental Duration:** {return_days} days  
                **Fine:** Rs. {fine}
                """)
            else:
                st.error("❌ Error in returning the book.")
    else:
        st.info("ℹ️ No books are currently rented out.")

# -----------------------------
# Add a Book (Admin)
# -----------------------------
elif menu == "➕ Add Book (Admin)":
    st.subheader("🛠️ Admin: Add New Book")
    username = st.text_input("👤 Admin Username")
    password = st.text_input("🔒 Admin Password", type="password")
    title = st.text_input("📘 Book Title")
    if st.button("➕ Add Book"):
        if library.authenticate_admin(username, password):
            new_id = library.add_book(title)
            if new_id:
                st.success(f"✅ Book '{title}' added successfully with ID {new_id}.")
            else:
                st.warning("⚠️ Book title cannot be empty.")
        else:
            st.error("❌ Invalid admin credentials.")

# -----------------------------
# Delete a Book (Admin)
# -----------------------------
elif menu == "🗑️ Delete Book (Admin)":
    st.subheader("🛠️ Admin: Delete Book")
    username = st.text_input("👤 Admin Username")
    password = st.text_input("🔒 Admin Password", type="password")
    deletable_books = {f"{book.book_id} - {book.title}": book.book_id for book in library.books if book.available}
    if deletable_books:
        selection = st.selectbox("📘 Choose Book to Delete", list(deletable_books.keys()))
        if st.button("🗑️ Delete Book"):
            if library.authenticate_admin(username, password):
                deleted = library.delete_book(deletable_books[selection])
                if deleted:
                    st.success("✅ Book deleted successfully.")
                else:
                    st.error("❌ Could not delete the book.")
            else:
                st.error("❌ Invalid admin credentials.")
    else:
        st.info("ℹ️ No deletable books found.")