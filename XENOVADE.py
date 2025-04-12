import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText  # Correct import
import cv2
import os
import sounddevice as sd
import numpy as np
import datetime
import random
from PIL import Image, ImageTk
import csv
from googlesearch import search
import webbrowser

# Initialize main application
class UniversitySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("University Smart System")
        self.create_main_menu()
        self.create_directories()
        
    def create_directories(self):
        os.makedirs("known_faces", exist_ok=True)
        os.makedirs("complaints", exist_ok=True)
        os.makedirs("attendance", exist_ok=True)
        
    def create_main_menu(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=20)
        
        buttons = [
            ("Emergency Detection", self.emergency_detection),
            ("Face Attendance", self.face_attendance),
            ("Complaint Portal", self.complaint_portal),
            ("Health Check", self.health_check),
            ("Academic Assistant", self.academic_assistant)
        ]
        
        for text, command in buttons:
            btn = tk.Button(frame, text=text, width=25, command=command)
            btn.pack(pady=5)

    # Emergency Detection System
    def emergency_detection(self):
        def callback(indata, frames, time, status):
            volume = np.linalg.norm(indata) * 10
            if volume > 20:  # Threshold for emergency sound
                messagebox.showwarning("EMERGENCY", "Loud noise detected! Alerting authorities!")
                
        try:
            with sd.InputStream(callback=callback):
                messagebox.showinfo("Info", "Emergency detection activated")
                sd.sleep(10000)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Face Recognition System
    def face_attendance(self):
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                cv2.imwrite("temp_face.jpg", frame)
                self.register_attendance()
                break
                
            cv2.imshow('Face Attendance', frame)
            if cv2.waitKey(1) == 27:
                break
                
        cap.release()
        cv2.destroyAllWindows()

    def register_attendance(self):
        name = simpledialog.askstring("Input", "Enter your name:")
        if name:
            date = datetime.date.today().strftime("%Y-%m-%d")
            with open(f"attendance/{date}.csv", "a") as f:
                writer = csv.writer(f)
                writer.writerow([name, datetime.datetime.now().strftime("%H:%M:%S")])
            messagebox.showinfo("Success", "Attendance recorded!")

    # Complaint Portal
    def complaint_portal(self):
        window = tk.Toplevel()
        window.title("Complaint Portal")
        
        tk.Label(window, text="Enter your complaint:").pack(pady=10)
        self.complaint_text = tk.Text(window, height=10, width=50)
        self.complaint_text.pack()
        
        tk.Button(window, text="Submit", command=self.save_complaint).pack(pady=10)

    def save_complaint(self):
        complaint = self.complaint_text.get("1.0", tk.END)
        filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".txt"
        with open(f"complaints/{filename}", "w") as f:
            f.write(complaint)
        messagebox.showinfo("Success", "Complaint submitted successfully!")

    # Health Check System with Web Search
    def health_check(self):
        self.health_window = tk.Toplevel(self.root)
        self.health_window.title("Health Check & Solutions")
        
        # Input Frame
        input_frame = tk.Frame(self.health_window)
        input_frame.pack(pady=10, padx=20, fill=tk.X)

        questions = [
            "How are you feeling today?",
            "Describe your sleep quality:",
            "What have you eaten today?",
            "Describe your stress levels:",
            "Social interactions status:"
        ]
        
        self.health_entries = []
        for i, q in enumerate(questions):
            tk.Label(input_frame, text=q).grid(row=i, column=0, sticky='w', pady=5)
            entry = tk.Text(input_frame, height=3, width=50)
            entry.grid(row=i, column=1, pady=5)
            self.health_entries.append(entry)

        # Results Frame
        results_frame = tk.Frame(self.health_window)
        results_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Use ScrolledText directly from the import
        self.result_text = ScrolledText(results_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Search Button
        tk.Button(self.health_window, text="Search Solutions", 
                command=self.search_health_issues).pack(pady=10)

    def search_health_issues(self):
        query_parts = []
        for entry in self.health_entries:
            text = entry.get("1.0", tk.END).strip()
            if text:
                query_parts.append(text)
        
        if not query_parts:
            messagebox.showwarning("Warning", "Please enter some health information first")
            return

        try:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "🔍 Searching for solutions...\n")
            self.health_window.update()

            # Get search results
            search_results = []
            for url in search(
                query=" ".join(query_parts),
                num=5,
                stop=5,
                pause=2.0
            ):
                search_results.append(url)

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "🌐 Top Health Resources:\n\n")
            for i, url in enumerate(search_results, 1):
                self.result_text.insert(tk.END, f"{i}. {url}\n")
            
            self.result_text.insert(tk.END, "\n⚠️ Note: Always consult a medical professional for accurate diagnosis.")

        except Exception as e:
            self.result_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")
            self.result_text.insert(tk.END, "Please check your internet connection or try again later.")

    # Academic Assistant
    def academic_assistant(self):
        question = simpledialog.askstring("Academic Assistant", "Ask your academic question:")
        if question:
            try:
                # Get search results
                search_results = list(search(question, num_results=3))
                if search_results:
                    answers = "\n\n".join([f"Result {i+1}: {result}" for i, result in enumerate(search_results)])
                    messagebox.showinfo("Answer", f"Top results:\n{answers}")
                else:
                    messagebox.showinfo("Answer", "No results found online.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to search: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversitySystem(root)
    root.mainloop()
