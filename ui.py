import tkinter as tk
from ga import genetic_algorithm, decode
from utils import setup

def start_ui():
    root = tk.Tk()
    root.title("AI Smart Study Planner")
    root.geometry("400x400")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Subjects (comma separated):", font=("Arial", 10)).pack()
    subjects_entry = tk.Entry(frame, width=30)
    subjects_entry.pack(pady=5)

    tk.Label(frame, text="Total Study Hours:", font=("Arial", 10)).pack()
    hours_entry = tk.Entry(frame, width=10)
    hours_entry.pack(pady=5)

    result_box = tk.Text(root, height=12, width=45)
    result_box.pack(pady=10)

    def generate():
        try:
            subjects = subjects_entry.get().split(",")
            subjects = [s.strip() for s in subjects if s.strip() != ""]

            hours = int(hours_entry.get())

            if len(subjects) == 0:
                result_box.insert(tk.END, "Enter valid subjects\n")
                return

            setup(subjects, hours)

            best = genetic_algorithm()
            schedule = decode(best)

            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, "📅 Best Schedule:\n\n")

            for t, s in schedule:
                result_box.insert(tk.END, f"{t}  →  {s}\n")

        except Exception as e:
            result_box.insert(tk.END, f"Error: {str(e)}\n")

    tk.Button(root, text="Generate Schedule", command=generate, bg="green", fg="white").pack(pady=5)

    root.mainloop()