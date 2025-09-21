import tkinter as tk
from tkinter import ttk, messagebox
import math
import random


class QuizApp:
    """
    Quiz Interaktif - Tugas Akhir Event-Driven

    Fitur:
    - Multiple choice dengan Radiobutton
    - Timer countdown per soal (default 30s)
    - Progress bar skor realtime
    - Validasi jawaban sebelum lanjut (wajib pilih sebelum submit)
    - Animasi feedback benar/salah pada canvas (pulse/flash)
    - Keyboard shortcuts: Enter=Submit, Esc=Skip
    - State management untuk progress quiz
    """

    def __init__(self):
        # Window setup
        self.window = tk.Tk()
        self.window.title("Quiz Interaktif - Tugas Akhir")
        self.window.geometry("800x600")
        self.window.minsize(720, 520)

        # Pastikan cleanup yang rapi saat jendela ditutup
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Data quiz (10 soal contoh)
        self.questions = [
            {
                "question": "Apa itu event-driven programming?",
                "options": [
                    "Program yang berjalan berurutan",
                    "Program yang merespons kejadian",
                    "Program tanpa GUI",
                    "Program berbasis web",
                ],
                "correct": 1,
            },
            {
                "question": "Method Tkinter untuk memulai event loop adalah?",
                "options": ["loop()", "run()", "mainloop()", "start()"],
                "correct": 2,
            },
            {
                "question": "Parameter paling umum untuk menangani klik Button adalah?",
                "options": ["bind", "onClick", "command", "listener"],
                "correct": 2,
            },
            {
                "question": "Fungsi after() digunakan untuk?",
                "options": [
                    "Menunda eksekusi tanpa blok GUI",
                    "Menghentikan event loop",
                    "Membuat thread baru",
                    "Menutup aplikasi",
                ],
                "correct": 0,
            },
            {
                "question": "Widget yang cocok untuk input pilihan tunggal?",
                "options": ["Checkbutton", "Radiobutton", "Listbox multi", "Canvas"],
                "correct": 1,
            },
            {
                "question": "Variabel kontrol untuk boolean di Tkinter adalah?",
                "options": ["IntVar", "DoubleVar", "StringVar", "BooleanVar"],
                "correct": 3,
            },
            {
                "question": "Event <B1-Motion> terjadi saat?",
                "options": [
                    "Klik kiri",
                    "Drag dengan tombol kiri ditekan",
                    "Rilis tombol kiri",
                    "Gerak mouse tanpa klik",
                ],
                "correct": 1,
            },
            {
                "question": "Apa kegunaan method trace_add pada Variable?",
                "options": [
                    "Menghapus variabel",
                    "Mengamati perubahan nilai",
                    "Menambah widget",
                    "Menutup window",
                ],
                "correct": 1,
            },
            {
                "question": "Apa yang TIDAK benar tentang Tkinter?",
                "options": [
                    "Menyediakan event handling",
                    "Berbasis web",
                    "Mendukung berbagai widget",
                    "Memiliki event loop",
                ],
                "correct": 1,
            },
            {
                "question": "Keyboard shortcut untuk Submit pada app ini adalah?",
                "options": ["Ctrl+S", "Enter", "Space", "Esc"],
                "correct": 1,
            },
        ]

        random.shuffle(self.questions)

        # State management
        self.current_question = 0
        self.score = 0
        self.time_per_question = 30
        self.time_left = self.time_per_question
        self.timer_job = None
        self.selected_answer = tk.IntVar(value=-1)
        self.answered = False
        self.correct_animation_job = None
        self.flash_state = False

        # UI
        self.buat_interface()
        self.bind_shortcuts()

        # Load first question
        self.load_question()
        self.start_timer()

    # ---------------------- UI BUILD ----------------------
    def buat_interface(self):
        # Header: Title + Score + Progress
        header = tk.Frame(self.window)
        header.pack(fill=tk.X, padx=16, pady=10)

        tk.Label(
            header,
            text="QUIZ INTERAKTIF",
            font=("Arial", 20, "bold"),
            fg="#1a4f8b",
        ).pack(side=tk.LEFT)

        right_header = tk.Frame(header)
        right_header.pack(side=tk.RIGHT)

        # Score label
        self.score_label = tk.Label(
            right_header, text="Skor: 0", font=("Arial", 12, "bold"), fg="#0a7d00"
        )
        self.score_label.pack(anchor="e")

        # Progress bar for score percentage
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            right_header, orient=tk.HORIZONTAL, mode="determinate", length=220, variable=self.progress_var
        )
        self.progress_bar.pack(pady=(4, 0))
        self.progress_text = tk.Label(right_header, text="0%", font=("Arial", 9))
        self.progress_text.pack(anchor="e")

        # Timer + Canvas feedback row
        top_mid = tk.Frame(self.window)
        top_mid.pack(fill=tk.X, padx=16, pady=(0, 10))

        # Timer Label
        self.timer_label = tk.Label(
            top_mid, text="Sisa Waktu: 30s", font=("Consolas", 16, "bold"), fg="#b10f2e"
        )
        self.timer_label.pack(side=tk.LEFT)

        # Feedback Canvas (animation)
        self.canvas = tk.Canvas(top_mid, width=120, height=40, highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT)
        self.feedback_rect = self.canvas.create_rectangle(
            0, 0, 120, 40, fill="#f0f0f0", outline=""
        )
        self.feedback_text = self.canvas.create_text(
            60, 20, text="", font=("Arial", 12, "bold"), fill="#333"
        )

        # Question Frame
        self.question_frame = tk.LabelFrame(self.window, text="Pertanyaan", padx=12, pady=12)
        self.question_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        self.question_label = tk.Label(
            self.question_frame, text="", font=("Arial", 14), wraplength=700, justify="left"
        )
        self.question_label.pack(anchor="w", pady=(0, 8))

        # Options (Radiobuttons)
        self.options_frame = tk.Frame(self.question_frame)
        self.options_frame.pack(fill=tk.X, pady=6)
        self.option_buttons = []
        for idx in range(4):
            rb = tk.Radiobutton(
                self.options_frame,
                text=f"Option {idx+1}",
                variable=self.selected_answer,
                value=idx,
                font=("Arial", 12),
                anchor="w",
                justify="left",
                wraplength=650,
            )
            rb.pack(fill=tk.X, pady=4, anchor="w")
            self.option_buttons.append(rb)

        # Navigation buttons
        nav = tk.Frame(self.window)
        nav.pack(fill=tk.X, padx=16, pady=10)

        self.submit_btn = tk.Button(
            nav,
            text="Submit (Enter)",
            bg="#1e90ff",
            fg="white",
            font=("Arial", 12, "bold"),
            width=16,
            command=self.submit_answer,
        )
        self.submit_btn.pack(side=tk.LEFT)

        self.skip_btn = tk.Button(
            nav,
            text="Skip (Esc)",
            bg="#aaaaaa",
            fg="white",
            font=("Arial", 12, "bold"),
            width=12,
            command=self.skip_question,
        )
        self.skip_btn.pack(side=tk.LEFT, padx=8)

        self.next_btn = tk.Button(
            nav,
            text="Next",
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            width=12,
            state=tk.DISABLED,
            command=self.next_question,
        )
        self.next_btn.pack(side=tk.RIGHT)

        # Footer info
        self.progress_info = tk.Label(
            self.window,
            text="Pertanyaan 1/{}".format(len(self.questions)),
            font=("Arial", 10),
        )
        self.progress_info.pack(pady=(0, 8))

    def bind_shortcuts(self):
        # Keyboard bindings
        self.window.bind("<Return>", self._on_enter)
        self.window.bind("<Escape>", lambda e: self.skip_question())

    def _on_enter(self, event=None):
        """Enter: Submit jika belum menjawab, Next jika sudah menjawab."""
        if self.answered:
            self.next_question()
        else:
            self.submit_answer()

    # ---------------------- QUIZ FLOW ----------------------
    def load_question(self):
        self.stop_feedback_animation()
        q = self.questions[self.current_question]

        # Reset selection and state
        self.selected_answer.set(-1)
        self.answered = False
        self.enable_options(True)
        self.next_btn.config(state=tk.DISABLED)
        # Pastikan submit & skip aktif untuk soal baru
        self.submit_btn.config(state=tk.NORMAL)
        self.skip_btn.config(state=tk.NORMAL)

        # Update texts
        self.question_label.config(text=q["question"]) 
        for i, opt in enumerate(q["options"]):
            self.option_buttons[i].config(text=opt)

        # Reset timer
        self.time_left = self.time_per_question
        self.update_timer_label()

        # Reset feedback canvas
        self.canvas.itemconfig(self.feedback_rect, fill="#f0f0f0")
        self.canvas.itemconfig(self.feedback_text, text="")

        # Progress info
        self.progress_info.config(
            text=f"Pertanyaan {self.current_question + 1}/{len(self.questions)}"
        )

    def start_timer(self):
        # Cancel previous job if any
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
            self.timer_job = None
        self.tick_timer()

    def tick_timer(self):
        # Update display
        self.update_timer_label()

        if self.time_left <= 0:
            # Time's up -> auto submit as incorrect (if not answered)
            if not self.answered:
                self.answered = True
                self.enable_options(False)
                # Matikan submit/skip ketika waktu habis
                self.submit_btn.config(state=tk.DISABLED)
                self.skip_btn.config(state=tk.DISABLED)
                self.show_feedback(correct=False, by_timeout=True)
                self.next_btn.config(state=tk.NORMAL)
                self.next_btn.focus_set()
            return

        # Decrement and reschedule
        self.time_left -= 1
        self.timer_job = self.window.after(1000, self.tick_timer)

    def update_timer_label(self):
        # Color changes when low time
        if self.time_left <= 5:
            color = "#ff2e2e"
        elif self.time_left <= 10:
            color = "#ff8c00"
        else:
            color = "#b10f2e"
        self.timer_label.config(text=f"Sisa Waktu: {self.time_left}s", fg=color)

    def enable_options(self, enable: bool):
        state = tk.NORMAL if enable else tk.DISABLED
        for rb in self.option_buttons:
            rb.config(state=state)

    def submit_answer(self):
        if self.answered:
            return
        choice = self.selected_answer.get()
        if choice == -1:
            messagebox.showwarning("Validasi", "Pilih salah satu jawaban terlebih dahulu!")
            return

        self.answered = True
        self.enable_options(False)
        # Hentikan timer saat sudah menjawab
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
            self.timer_job = None

        # Check correctness
        correct_index = self.questions[self.current_question]["correct"]
        is_correct = choice == correct_index
        if is_correct:
            self.score += 1
        self.update_score_progress()
        self.show_feedback(correct=is_correct)

        # Allow Next
        self.next_btn.config(state=tk.NORMAL)
        # Nonaktifkan submit & skip; fokuskan Next agar alur jelas
        self.submit_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.DISABLED)
        self.next_btn.focus_set()

    def skip_question(self):
        if self.answered:
            return
        self.answered = True
        self.enable_options(False)
        # Hentikan timer saat skip
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
            self.timer_job = None
        self.show_feedback(correct=False, skipped=True)
        self.next_btn.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.DISABLED)
        self.next_btn.focus_set()

    def next_question(self):
        # Stop timer for current question
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
            self.timer_job = None

        # Next or finish
        if self.current_question + 1 < len(self.questions):
            self.current_question += 1
            self.load_question()
            self.start_timer()
        else:
            self.show_result()

    # ---------------------- FEEDBACK + ANIMATION ----------------------
    def show_feedback(self, correct: bool, skipped: bool = False, by_timeout: bool = False):
        if correct:
            self.canvas.itemconfig(self.feedback_rect, fill="#ccffcc")
            self.canvas.itemconfig(self.feedback_text, text="Benar ✓", fill="#0a7d00")
            self.start_correct_pulse()
        else:
            msg = "Salah ✗"
            if skipped:
                msg = "Lewati ⏭"
            if by_timeout:
                msg = "Waktu Habis ⏲"
            self.canvas.itemconfig(self.feedback_rect, fill="#ffe1e1")
            self.canvas.itemconfig(self.feedback_text, text=msg, fill="#b10f2e")
            self.start_wrong_flash()

    def start_correct_pulse(self):
        # Soft pulsing background green
        self.stop_feedback_animation()
        self.pulse_phase = 0
        def step():
            self.pulse_phase = (self.pulse_phase + 1) % 40
            # sine wave 0..1
            intensity = (1 + math.sin(self.pulse_phase / 40 * 2 * math.pi)) / 2
            green = int(200 + 55 * intensity)  # 200..255
            # Format warna RGB yang benar (#RRGGBB)
            color = "#%02x%02x%02x" % (200, green, 200)
            self.canvas.itemconfig(self.feedback_rect, fill=color)
            self.correct_animation_job = self.window.after(50, step)
        step()

    def start_wrong_flash(self):
        # Red/white flashing
        self.stop_feedback_animation()
        self.flash_state = False
        def step():
            self.flash_state = not self.flash_state
            color = "#ffd6d6" if self.flash_state else "#ffecec"
            self.canvas.itemconfig(self.feedback_rect, fill=color)
            self.correct_animation_job = self.window.after(120, step)
        step()

    def stop_feedback_animation(self):
        if self.correct_animation_job:
            self.window.after_cancel(self.correct_animation_job)
            self.correct_animation_job = None

    # ---------------------- SCORE PROGRESS ----------------------
    def update_score_progress(self):
        total = len(self.questions)
        pct = (self.score / total) * 100
        self.progress_var.set(pct)
        self.progress_text.config(text=f"{pct:.0f}%")
        self.score_label.config(text=f"Skor: {self.score}")

    # ---------------------- RESULT ----------------------
    def show_result(self):
        # Stop timer/animations
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
            self.timer_job = None
        self.stop_feedback_animation()

        total = len(self.questions)
        pct = (self.score / total) * 100
        message = (
            f"Hasil Akhir\n\n"
            f"Skor: {self.score}/{total} ({pct:.0f}%)\n\n"
            f"Terima kasih telah mengikuti Quiz!"
        )
        messagebox.showinfo("Selesai", message)
        # Tutup aplikasi dengan rapi
        self.window.destroy()

    def _on_close(self):
        """Cleanup saat jendela ditutup lewat tombol close (X)."""
        # Batalkan semua after jobs agar tidak memanggil widget yang sudah dihancurkan
        try:
            if self.timer_job:
                self.window.after_cancel(self.timer_job)
                self.timer_job = None
            if self.correct_animation_job:
                self.window.after_cancel(self.correct_animation_job)
                self.correct_animation_job = None
        finally:
            self.window.destroy()

    # ---------------------- RUN ----------------------
    def jalankan(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = QuizApp()
    app.jalankan()
