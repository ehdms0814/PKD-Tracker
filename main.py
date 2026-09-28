import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data_manager import DataManager
from analyzer_visualizer import Analyzer, Visualizer

class PKDTrackerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("PKD Self-Tracking Diary")
        self.root.geometry("1100x700")

        self.data_manager = DataManager()
        self.analyzer = Analyzer(self.data_manager)
        self.visualizer = Visualizer(self.analyzer)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Arial", 13))
        style.configure("TButton", font=("Arial", 13, "bold"), padding=6)
        style.configure("TCombobox", font=("Arial", 13))
        style.configure("TEntry", font=("Arial", 13))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.diary_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.diary_tab, text=" 📅 Diary ")
        self.notebook.add(self.stats_tab, text=" 📊 Statistics ")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.create_diary_widgets()
        self.create_stats_widgets()

    def create_diary_widgets(self):

        left_frame = ttk.Frame(self.diary_tab, padding="20")
        left_frame.pack(side="left", fill="y", padx=(10, 20))

        right_frame = ttk.Frame(self.diary_tab, padding="20")
        right_frame.pack(side="left", fill="y")

        ttk.Label(left_frame, text="Select Date:", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        self.cal = Calendar(
            left_frame, 
            selectmode='day', 
            date_pattern='yyyy-mm-dd',
            font="Arial 16", 
            showweeknumbers=False,

            todaybackground='green',         
            todayforeground='white',          
            weekendbackground='white',       
            weekendforeground='black',        
            othermonthbackground='#f3f3f3',  
            othermonthforeground='gray50',    
            othermonthwebackground='#f3f3f3', 
            othermonthweforeground='gray50',  

            selectbackground='#0078D7'       
        )
        self.cal.pack(pady=10, fill="both", expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        self._date_select_job = None

        ttk.Button(left_frame, text="🔄 Reload Date", command=self.load_date_data).pack(pady=10, fill="x")

        ttk.Label(right_frame, text="Daily Record", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.sleep_start_var = tk.StringVar()
        self.sleep_end_var = tk.StringVar()
        self.sleep_hours_var = tk.StringVar()
        self.med_time_var = tk.StringVar()
        self.med_count_var = tk.StringVar()
        self.ex_type_var = tk.StringVar()
        self.ex_duration_var = tk.StringVar()
        self.symp_occur_var = tk.StringVar(value="No")
        self.symp_count_var = tk.StringVar()
        self.symp_score_var = tk.StringVar()
        self.trans_type_var = tk.StringVar()

        self.sleep_start_var.trace_add("write", self.update_sleep_hours_live)
        self.sleep_end_var.trace_add("write", self.update_sleep_hours_live)

        ttk.Label(right_frame, text="Sleep Start (HH:MM or HHMM):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.sleep_start_var, width=20).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Sleep End (HH:MM or HHMM):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.sleep_end_var).grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Total Sleep Hours:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.sleep_hours_var, state="readonly").grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Separator(right_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(right_frame, text="Medication Time(s):").grid(row=5, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.med_time_var).grid(row=5, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Medication Count:").grid(row=6, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.med_count_var).grid(row=6, column=1, sticky="ew", pady=5)

        ttk.Separator(right_frame, orient='horizontal').grid(row=7, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(right_frame, text="Exercise Type:").grid(row=8, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.ex_type_var).grid(row=8, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Exercise Duration (mins):").grid(row=9, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.ex_duration_var).grid(row=9, column=1, sticky="ew", pady=5)

        ttk.Separator(right_frame, orient='horizontal').grid(row=10, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(right_frame, text="Symptom Occurred:").grid(row=11, column=0, sticky="w", pady=5)

        symp_frame = ttk.Frame(right_frame)
        symp_frame.grid(row=11, column=1, sticky="w")
        ttk.Radiobutton(symp_frame, text="Yes", variable=self.symp_occur_var, value="Yes").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(symp_frame, text="No", variable=self.symp_occur_var, value="No").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(symp_frame, text="Aura Only", variable=self.symp_occur_var, value="Aura Only").pack(side="left")

        ttk.Label(right_frame, text="Symptom Count:").grid(row=12, column=0, sticky="w", pady=5)
        ttk.Entry(right_frame, textvariable=self.symp_count_var).grid(row=12, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Stability Score (1-4):").grid(row=13, column=0, sticky="w", pady=5)
        score_frame = ttk.Frame(right_frame)
        score_frame.grid(row=13, column=1, sticky="w")
        for val in ["1", "2", "3", "4"]:
            ttk.Radiobutton(score_frame, text=val, variable=self.symp_score_var, value=val).pack(side="left", padx=(0, 15))

        ttk.Label(right_frame, text="Transition Type:").grid(row=14, column=0, sticky="nw", pady=5)
        trans_frame = ttk.Frame(right_frame)
        trans_frame.grid(row=14, column=1, sticky="w")
        types = ["None", "rest_to_walk", "sit_to_stand", "turning", "acceleration", "continuous_movement", "unknown"]
        for i, t_val in enumerate(types):
            r = i // 3 
            c = i % 3  
            ttk.Radiobutton(trans_frame, text=t_val, variable=self.trans_type_var, value=t_val).grid(row=r, column=c, sticky="w", padx=(0, 10), pady=2)

        ttk.Label(right_frame, text="Notes:").grid(row=15, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(right_frame, height=3, width=25, font=("Arial", 12))
        self.notes_text.grid(row=15, column=1, sticky="ew", pady=5)

        ttk.Button(right_frame, text="💾 Save Record", command=self.save_data).grid(row=16, column=0, columnspan=2, pady=(20, 5), sticky="ew")

        self.status_lbl = ttk.Label(right_frame, text="", font=("Arial", 12, "bold"))
        self.status_lbl.grid(row=17, column=0, columnspan=2, pady=5)

        self.load_date_data()

    def create_stats_widgets(self):

        self.stats_top_frame = ttk.Frame(self.stats_tab, padding="10")
        self.stats_top_frame.pack(side="top", fill="x")

        self.stats_lbl = ttk.Label(self.stats_top_frame, text="통계 요약이 여기에 표시됩니다.", font=("Arial", 14, "bold"))
        self.stats_lbl.pack(side="left", padx=10)

        ttk.Button(self.stats_top_frame, text="🔄 Refresh Charts", command=self.refresh_stats).pack(side="right", padx=10)
        ttk.Button(self.stats_top_frame, text="💾 Save to PDF", command=self.save_charts_to_pdf).pack(side="right", padx=10)

        self.canvas_frame = ttk.Frame(self.stats_tab, padding="10")
        self.canvas_frame.pack(side="top", fill="both", expand=True)

        self.canvas1 = None
        self.canvas2 = None

    def on_tab_changed(self, event):

        if self.notebook.index(self.notebook.select()) == 1:
            self.refresh_stats()

    def refresh_stats(self):

        stats = self.analyzer.get_basic_stats()
        corrs = self.analyzer.get_correlations()

        if "Error" in stats:
            self.stats_lbl.config(text="데이터가 충분하지 않습니다.")
        else:
            text = f"총 기록 일수: {stats['Total_Recorded_Days']}일 | 평균 수면: {stats['Average_Sleep_Hours']}시간 | 평균 안정성: {stats['Average_Stability_Score']}점\n"
            text += f"[Symptom Count 상관계수] 수면: {corrs.get('Symptom_vs_Sleep_Hours', 0)} | 복약: {corrs.get('Symptom_vs_Medication_Count', 0)} | 운동: {corrs.get('Symptom_vs_Exercise_Hours', 0)}\n"
            text += f"[Stability Score 상관계수] 수면: {corrs.get('Stability_vs_Sleep_Hours', 0)} | 복약: {corrs.get('Stability_vs_Medication_Count', 0)} | 운동: {corrs.get('Stability_vs_Exercise_Hours', 0)}"

            self.stats_lbl.config(text=text, justify="left")

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        fig1 = self.visualizer.create_symptoms_figure()
        if fig1:
            self.canvas1 = FigureCanvasTkAgg(fig1, master=self.canvas_frame)
            self.canvas1.draw()
            self.canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=5)

        fig2 = self.visualizer.create_transition_figure()
        if fig2:
            self.canvas2 = FigureCanvasTkAgg(fig2, master=self.canvas_frame)
            self.canvas2.draw()
            self.canvas2.get_tk_widget().pack(side="right", fill="both", expand=True, padx=5)

    def on_date_select(self, event):

        if self._date_select_job is not None:
            self.root.after_cancel(self._date_select_job)
        self._date_select_job = self.root.after(50, self.load_date_data)

    def load_date_data(self):

        selected_date = self.cal.get_date()
        entry = self.data_manager.get_entry_by_date(selected_date)

        self.clear_form()

        if entry:
            self.sleep_start_var.set(entry.get("Sleep_Start", ""))
            self.sleep_end_var.set(entry.get("Sleep_End", ""))
            self.sleep_hours_var.set(entry.get("Sleep_Hours", ""))
            self.med_time_var.set(entry.get("Medication_Time", ""))
            self.med_count_var.set(entry.get("Medication_Count", ""))
            self.ex_type_var.set(entry.get("Exercise_Type", ""))
            self.ex_duration_var.set(entry.get("Exercise_Duration", ""))
            self.symp_occur_var.set(entry.get("Symptom_Occurred", "No"))
            self.symp_count_var.set(entry.get("Symptom_Count", ""))
            self.symp_score_var.set(entry.get("Symptom_Score", ""))
            self.trans_type_var.set(entry.get("Transition_Type", "None"))
            self.notes_text.insert("1.0", entry.get("Notes", ""))

    def clear_form(self):

        self.sleep_start_var.set("")
        self.sleep_end_var.set("")
        self.sleep_hours_var.set("")
        self.med_time_var.set("")
        self.med_count_var.set("")
        self.ex_type_var.set("")
        self.ex_duration_var.set("")
        self.symp_occur_var.set("No")
        self.symp_count_var.set("")
        self.symp_score_var.set("")
        self.trans_type_var.set("None")
        self.notes_text.delete("1.0", tk.END)

    def calculate_sleep_hours(self, start_str, end_str):

        if not start_str or not end_str:
            return ""

        if len(start_str) == 4 and ":" not in start_str:
            start_str = f"{start_str[:2]}:{start_str[2:]}"
        if len(end_str) == 4 and ":" not in end_str:
            end_str = f"{end_str[:2]}:{end_str[2:]}"

        try:
            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")

            if end_time < start_time:
                end_time += timedelta(days=1)

            delta = end_time - start_time
            hours = round(delta.total_seconds() / 3600, 1)
            return str(hours)
        except ValueError:
            return ""

    def update_sleep_hours_live(self, *args):

        start_str = self.sleep_start_var.get().strip()
        end_str = self.sleep_end_var.get().strip()
        calculated_hours = self.calculate_sleep_hours(start_str, end_str)
        self.sleep_hours_var.set(calculated_hours)

    def save_data(self):

        selected_date = self.cal.get_date()

        sleep_start = self.sleep_start_var.get().strip()
        sleep_end = self.sleep_end_var.get().strip()

        if len(sleep_start) == 4 and ":" not in sleep_start:
            sleep_start = f"{sleep_start[:2]}:{sleep_start[2:]}"
            self.sleep_start_var.set(sleep_start)
        if len(sleep_end) == 4 and ":" not in sleep_end:
            sleep_end = f"{sleep_end[:2]}:{sleep_end[2:]}"
            self.sleep_end_var.set(sleep_end)

        calculated_hours = self.sleep_hours_var.get()

        entry_data = {
            "Date": selected_date,
            "Sleep_Start": sleep_start,
            "Sleep_End": sleep_end,
            "Sleep_Hours": calculated_hours,
            "Medication_Time": self.med_time_var.get(),
            "Medication_Count": self.med_count_var.get(),
            "Exercise_Type": self.ex_type_var.get(),
            "Exercise_Duration": self.ex_duration_var.get(),
            "Symptom_Occurred": self.symp_occur_var.get(),
            "Symptom_Count": self.symp_count_var.get(),
            "Symptom_Score": self.symp_score_var.get(),
            "Transition_Type": self.trans_type_var.get(),
            "Notes": self.notes_text.get("1.0", tk.END).strip() 
        }

        self.data_manager.save_entry(entry_data)

        self.status_lbl.config(text=f"✅ {selected_date} 기록이 저장되었습니다!", foreground="green")
        self.root.after(3000, lambda: self.status_lbl.config(text=""))

        self.load_date_data()

    def save_charts_to_pdf(self):

        from tkinter import filedialog
        from matplotlib.backends.backend_pdf import PdfPages

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf")],
            title="Save Charts as PDF"
        )

        if not filepath:
            return

        try:
            fig1 = self.visualizer.create_symptoms_figure()
            fig2 = self.visualizer.create_transition_figure()

            with PdfPages(filepath) as pdf:
                if fig1:
                    pdf.savefig(fig1)
                if fig2:
                    pdf.savefig(fig2)

            messagebox.showinfo("Success", f"그래프가 PDF로 성공적으로 저장되었습니다!\n\n저장 위치:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"PDF 저장 중 오류가 발생했습니다.\n\n상세 내용: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PKDTrackerApp(root)
    root.mainloop()
