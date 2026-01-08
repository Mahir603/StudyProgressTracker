import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import date

DB_NAME = "study_progress.db"


# ---------------- Database helpers ----------------

def connect_db():
    return sqlite3.connect(DB_NAME)


def get_subjects():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()
    conn.close()
    return subjects


# ---------------- UI functies ----------------

def add_subject():
    name = subject_entry.get().strip()

    if not name:
        messagebox.showwarning("Fout", "Vul een vaknaam in")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    subject_entry.delete(0, tk.END)
    refresh_subjects()
    messagebox.showinfo("Gelukt", "Vak toegevoegd")


def refresh_subjects():
    subjects = get_subjects()
    subject_names = [s[1] for s in subjects]
    subject_combo["values"] = subject_names


def add_session():
    subject_name = subject_combo.get()
    minutes = minutes_entry.get()

    if not subject_name or not minutes:
        messagebox.showwarning("Fout", "Vul alle velden in")
        return

    try:
        minutes = int(minutes)
        if minutes <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Fout", "Vul een geldig aantal minuten in")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject_name,))
    subject_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO study_sessions (subject_id, minutes, study_date)
        VALUES (?, ?, ?)
    """, (subject_id, minutes, date.today().isoformat()))

    conn.commit()
    conn.close()

    minutes_entry.delete(0, tk.END)
    messagebox.showinfo("Gelukt", "Studiesessie toegevoegd")


def show_progress():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subjects.name, SUM(study_sessions.minutes)
        FROM study_sessions
        JOIN subjects ON subjects.id = study_sessions.subject_id
        GROUP BY subjects.name
    """)

    output.delete("1.0", tk.END)
    output.insert(tk.END, "--- Totaal per vak ---\n")

    for name, total_minutes in cursor.fetchall():
        hours = total_minutes / 60
        output.insert(tk.END, f"{name}: {hours:.2f} uur\n")

    conn.close()


def show_today():
    today = date.today().isoformat()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(minutes)
        FROM study_sessions
        WHERE study_date = ?
    """, (today,))

    result = cursor.fetchone()[0]
    total_minutes = result if result else 0

    output.delete("1.0", tk.END)
    output.insert(
        tk.END,
        f"Vandaag gestudeerd: {total_minutes} minuten\n"
    )

    conn.close()


# ---------------- UI setup ----------------

root = tk.Tk()
root.title("StudyProgressTracker")
root.resizable(False, False)

# Vak toevoegen
tk.Label(root, text="Vak toevoegen").grid(row=0, column=0, sticky="w", padx=5, pady=5)
subject_entry = tk.Entry(root, width=25)
subject_entry.grid(row=0, column=1, padx=5)
tk.Button(root, text="Toevoegen", command=add_subject).grid(row=0, column=2, padx=5)

# Studie invoer
tk.Label(root, text="Vak").grid(row=1, column=0, sticky="w", padx=5)
subject_combo = ttk.Combobox(root, state="readonly", width=22)
subject_combo.grid(row=1, column=1, padx=5)

tk.Label(root, text="Minuten").grid(row=2, column=0, sticky="w", padx=5)
minutes_entry = tk.Entry(root, width=25)
minutes_entry.grid(row=2, column=1, padx=5)

tk.Button(root, text="Studietijd opslaan", command=add_session)\
    .grid(row=3, column=1, pady=5)

# Overzicht knoppen
tk.Button(root, text="Totaal per vak", command=show_progress)\
    .grid(row=4, column=1, sticky="w", pady=5)

tk.Button(root, text="Vandaag", command=show_today)\
    .grid(row=4, column=2, sticky="w", pady=5)

# Output
output = tk.Text(root, height=8, width=45)
output.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Init
refresh_subjects()

root.mainloop()
