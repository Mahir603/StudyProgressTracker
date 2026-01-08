import sqlite3
from datetime import date

DB_NAME = "study_progress.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            minutes INTEGER,
            study_date TEXT,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
    """)

    conn.commit()
    conn.close()


def add_subject(name):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def add_study_session(subject_id, minutes):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO study_sessions (subject_id, minutes, study_date)
        VALUES (?, ?, ?)
    """, (subject_id, minutes, date.today().isoformat()))

    conn.commit()
    conn.close()


def show_subjects():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM subjects")
    subjects = cursor.fetchall()

    print("\n--- Vakken ---")
    for s in subjects:
        print(f"{s[0]}. {s[1]}")

    conn.close()
    return subjects


def show_progress():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subjects.name, SUM(study_sessions.minutes)
        FROM study_sessions
        JOIN subjects ON subjects.id = study_sessions.subject_id
        GROUP BY subjects.name
    """)

    print("\n--- Studievoortgang ---")
    for row in cursor.fetchall():
        hours = row[1] / 60
        print(f"{row[0]}: {hours:.2f} uur")

    conn.close()


def main():
    create_tables()

    while True:
        print("\n=== StudyProgressTracker ===")
        print("1. Vak toevoegen")
        print("2. Studie-uren toevoegen")
        print("3. Overzicht voortgang")
        print("4. Afsluiten")

        choice = input("Kies een optie: ")

        if choice == "1":
            name = input("Naam van het vak: ")
            add_subject(name)
            print("Vak toegevoegd.")

        elif choice == "2":
            subjects = show_subjects()
            if not subjects:
                print("Geen vakken gevonden.")
                continue

            subject_id = int(input("Kies vaknummer: "))
            minutes = int(input("Aantal minuten gestudeerd: "))
            add_study_session(subject_id, minutes)
            print("Studie-uren opgeslagen.")

        elif choice == "3":
            show_progress()

        elif choice == "4":
            print("Tot ziens 👋")
            break

        else:
            print("Ongeldige keuze.")


if __name__ == "__main__":
    main()





# test
