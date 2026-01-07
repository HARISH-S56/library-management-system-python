import sqlite3
from tkinter import ttk
conn=sqlite3.connect("library.db")
cursor=conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
               book_id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT,
               author TEXT,
               status TEXT) """)
cursor.execute(""" 
CREATE TABLE IF NOT EXISTS issued_books (
               issued_id INTEGER PRIMARY KEY AUTOINCREMENT,
               book_id INTEGER,
               student_name TEXT,
               issued_date TEXT,
               return_date TEXT) """)

conn.commit()
conn.close()

def add_book(title,author):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute(
        "INSERT INTO books (title,author,status) VALUES (?,?,?)",
        (title,author,"Available")
    )
    conn.commit()
    conn.close()

def view_books():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute(
        "SELECT * FROM books"
    )
    rows=cursor.fetchall()
    cursor.close()
    return rows
from datetime import date
def issue_book(book_id, student_name):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute(
        "SELECT status FROM books WHERE book_id=?",(book_id,)
    )
    status=cursor.fetchone()
    if status and status[0] == "Available":
        cursor.execute(
            "INSERT INTO issued_books(book_id,student_name,issued_date,return_date) VALUES (?,?,?,?)",
            (book_id,student_name,date.today(),None)
        )
        cursor.execute(
            "UPDATE books SET status='Issued' WHERE book_id=?",
            (book_id,)
        )
        conn.commit()
        conn.close()

def return_book(book_id):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute(
        "SELECT issued_date FROM issued_books WHERE book_id=? AND return_date is NULL",(book_id,)
    )       
    row=cursor.fetchone()
    if not row:
        conn.close()
        return None
    issued_date=date.fromisoformat(row[0])
    today=date.today()
    days=(today-issued_date).days
    fine=max(0,(days-7)*5)
    cursor.execute(
        "UPDATE issued_books SET return_date=? WHERE book_id=? AND return_date IS Null",(today,book_id)
        )
    cursor.execute(
        "UPDATE books SET status='Availabile' WHERE book_id=?",(book_id,)
        )
    conn.commit()
    conn.close()
    return fine

#GUI
import tkinter as tk
from tkinter import messagebox
def add_book_gui():
    add_book(title_entry.get(),author_entry.get())
    messagebox.showinfo("Success","Book added")

def view_books_gui():
    window=tk.Toplevel()
    window.title=("View Books")
    window.geometry("600x300")
    tree=ttk.Treeview(window,columns=("ID","Title","Author","Status"),show="headings")
    tree.heading("ID",text="Book ID")
    tree.heading("Title",text="Title")
    tree.heading("Author",text="Author")
    tree.heading("Status",text="Status")
    tree.column("ID",width=60)
    tree.column("Title",width=200)
    tree.column("Author",width=150)
    tree.column("Status",width=100)
    tree.pack(fill=tk.BOTH, expand=True)
    books=view_books()
    for book in books:
        tree.insert("", tk.END, values=book)
def issue_book_gui():
    def issue():
        book_id=book_id_entry.get()
        student=student_entry.get()
        if book_id=="" or student=="":
            messagebox.showerror("Error","All fields are required")
            return
        issue_book(int(book_id),student)
        messagebox.showinfo("Success","Book Issued Successfully")
        issue_window.destroy()
    issue_window=tk.Toplevel()
    issue_window.title("Issue Book")
    issue_window.geometry("300x200")
    tk.Label(issue_window,text="Book ID").pack(pady=5)
    book_id_entry=tk.Entry(issue_window)
    book_id_entry.pack()
    tk.Label(issue_window,text="Student").pack(pady=5)
    student_entry=tk.Entry(issue_window)
    student_entry.pack()
    tk.Button(issue_window,text="Issue Book",command=issue).pack(pady=10)

def return_book_gui():
    def return_book_action():
        booK_id=book_id_entry.get()
        if booK_id=="":
            messagebox.showerror("Error","Book ID is required")
            return
        fine=return_book(int(booK_id))
        if fine is not None:
            messagebox.showinfo("Returned",f"Book returned successfully. \nFine: ${fine}")
        else:
            messagebox.showerror("Error","Invalid Book ID or Book not issued")
        return_window.destroy()
    return_window=tk.Toplevel()
    return_window.title("Return Book")
    return_window.geometry("300x150")
    tk.Label(return_window,text="Book ID").pack(pady=5)
    book_id_entry=tk.Entry(return_window)
    book_id_entry.pack()
    tk.Button(return_window,text="Return Book",command=return_book_action).pack(pady=10)



root=tk.Tk()
root.title("Library Management System")
root.geometry("400x300")
tk.Label(root,text="Book Title").pack()
title_entry=tk.Entry(root)
title_entry.pack()

tk.Label(root,text="Author").pack()
author_entry=tk.Entry(root)
author_entry.pack()

tk.Button(root,text="Add Book",command=add_book_gui).pack(pady=10)

tk.Button(root,text="View Books",command=view_books_gui).pack(pady=5)
tk.Button(root,text="Issue Book",command=issue_book_gui).pack(pady=5)
tk.Button(root,text="Return Book",command=return_book_gui).pack(pady=5)
root.mainloop()
