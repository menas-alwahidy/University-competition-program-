import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import pandas as pd
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

matplotlib.use('TkAgg')

# --- 1. شاشة تسجيل الدخول ---
class LoginScreen(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.title("University Portal - Secure Login")
        
        self.geometry("900x600")
        self.on_success = on_success
        self.configure(fg_color="#FFFFFF")

        
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.main_frame.pack(side="left", expand=True, fill="both", padx=40, pady=40)

        self.logo_label = ctk.CTkLabel(self.main_frame, text="🎓", font=("Arial", 80))
        self.logo_label.pack(pady=(20, 10))

        self.title_label = ctk.CTkLabel(self.main_frame, text="Scoring System LOGIN",
                                        font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
                                        text_color="#1E40AF")
        self.title_label.pack(pady=10)

        self.email_entry = ctk.CTkEntry(self.main_frame, placeholder_text="University Email (@university.edu)",
                                        width=320, height=50, corner_radius=10)
        self.email_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password",
                                        show="*", width=320, height=50, corner_radius=10)
        self.pass_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(self.main_frame, text="SIGN IN", command=self.validate_login,
                                       width=320, height=55, corner_radius=12,
                                       fg_color="#2563EB", font=ctk.CTkFont(size=16, weight="bold"))
        self.login_btn.pack(pady=30)

        
        self.bot_frame = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=20, width=320)
        self.bot_frame.pack(side="right", fill="y", padx=(0, 40), pady=40)
        self.bot_frame.pack_propagate(False) 

        ctk.CTkLabel(self.bot_frame, text=" College Support", 
                     font=("Segoe UI", 18, "bold"), text_color="#1E40AF").pack(pady=20)

        self.chat_box = ctk.CTkTextbox(self.bot_frame, fg_color="white", border_width=1, corner_radius=15)
        self.chat_box.pack(expand=True, fill="both", padx=15, pady=10)
        self.chat_box.insert("end", "🤖: Hello! Need help ?\n\n")
        self.chat_box.configure(state="disabled")

        input_area = ctk.CTkFrame(self.bot_frame, fg_color="transparent")
        input_area.pack(fill="x", padx=15, pady=15)

        self.chat_input = ctk.CTkEntry(input_area, placeholder_text="share your thoughts...", height=40)
        self.chat_input.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.send_btn = ctk.CTkButton(input_area, text="➤", width=40, height=40, 
                                      command=self.handle_chatbot, fg_color="#1E40AF")
        self.send_btn.pack(side="right")

    # --- دوال الربط والمنطق ---
    def handle_chatbot(self):
        user_msg = self.chat_input.get()
        if user_msg.strip():
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", f"You: {user_msg}\n")
            # رد تلقائي يوضح الإرسال للكلية
            self.chat_box.insert("end", "Bot: Your message has been forwarded to the college administration. 📩\n\n")
            self.chat_box.configure(state="disabled")
            self.chat_box.see("end")
            self.chat_input.delete(0, 'end')

    def validate_login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not email:
            messagebox.showerror("Error", "Email field cannot be empty!")
            return
        if not password:
            messagebox.showerror("Error", "Password field cannot be empty!")
            return
        if not email.lower().endswith("@university.edu"):
            messagebox.showerror("Access Denied", "Invalid Domain! Use @university.edu only.")
            return
        if len(password) < 4:
            messagebox.showerror("Security", "Password is too short!")
            return

        self.withdraw()
        self.on_success()

# --- 2. المنطق الحسابي ---
class TournamentLogic:
    @staticmethod
    def get_participation_count(results, name):
        return sum(1 for res in results if res['name'] == name)

    @staticmethod
    def calculate_standings(results):
        stats = {}
        participation_count = {}
        for entry in results:
            name = entry['name']
            participation_count[name] = participation_count.get(name, 0) + 1

        for entry in results:
            name = entry['name']
            if participation_count[name] >= 5:
                stats.setdefault(name, {'total_pts': 0, 'events': 0})
                stats[name]['total_pts'] += entry['points']
                stats[name]['events'] += 1
        return sorted(stats.items(), key=lambda x: x[1]['total_pts'], reverse=True)

# --- 3. الواجهة الرسومية الرئيسية ---
class TechMasterTournament(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NEURAL INTERFACE PRO")
        self.geometry("1400x900")
        

        self.teams = {}
        self.individuals = []
        self.results = []
        self.timer_running = False
        self.remaining_time = 30
        self.auto_refresh_enabled = True 

        self.event_config = {
            "Web Dev(Individual)": {"type": "Individual", "q": "Tag for largest heading?", "a": "h1", "points": 10, "diff": "Easy"},
            "Cyber Security(Individual)": {"type": "Individual", "q": "Decode 'UHl0aG9u'?", "a": "python", "points": 25, "diff": "Hard"},
            "Data Science(Individual)": {"type": "Individual", "q": "Clean '12-A-3' (Numbers only)?", "a": "123", "points": 20, "diff": "Medium"},
            "AI Challenge(Individual)": {"type": "Individual", "q": "Result of 2**3?", "a": "8", "points": 30, "diff": "Elite"},
            "Logic Test(Individual)": {"type": "Individual", "q": "Which number comes next in the sequence: 2, 4, 6, 8, ?", "a": "10", "points": 5, "diff": "Easy"},
            "UI/UX Battle(Team)": {"type": "Team", "q": "Hex code for Pure White?", "a": "#ffffff", "points": 15, "diff": "Medium"},
            "Robotics Team(Team)": {"type": "Team", "q": "Main controller name?", "a": "arduino", "points": 25, "diff": "Hard"},
            "Network Setup(Team)": {"type": "Team", "q": "Protocol for web browsing?", "a": "http", "points": 15, "diff": "Easy"},
            "Database Design(Team)": {"type": "Team", "q": "Language for DB queries?", "a": "sql", "points": 20, "diff": "Medium"},
            "Cloud Computing(Team)": {"type": "Team", "q": "AWS stands for?", "a": "amazon", "points": 25, "diff": "Hard"},
            "Tech Expo (Innovation Gallery)": {"type": "Show", "points": 0}
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.view_port = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=30)
        self.view_port.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)

        self.setup_telemetry()
        self.pages = {}
        self.init_pages()
        self.show_page("Dashboard")

        self.animate_export_step(0)
        self.trigger_tech_intro_step(0)
        self.start_global_refresh_loop() 

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#F1F5F9", border_width=1, border_color="#E2E8F0")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="SYSTEM CORE", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E40AF").pack(pady=60)

        menu = [("Dashboard", ""), ("Teams", ""), ("Players", ""), ("Scoring", ""), ("Leaderboard", ""), ("Analytics", "")]
        for text, icon in menu:
            btn = ctk.CTkButton(self.sidebar, text=f"{icon} {text.upper()}", anchor="w",
                               fg_color="transparent", hover_color="#DBEAFE",
                               text_color="#1E293B", font=ctk.CTkFont(size=14, weight="bold"),
                               height=60, corner_radius=10, command=lambda t=text: self.show_page(t))
            btn.pack(fill="x", padx=25, pady=4)

        self.export_btn = ctk.CTkButton(self.sidebar, text=" EXPORT DATA", fg_color="#059669", hover_color="#047857",
                                       height=65, font=ctk.CTkFont(size=16, weight="bold"), corner_radius=15, command=self.export_excel)
        self.export_btn.pack(side="bottom", pady=50, padx=30, fill="x")

    def setup_telemetry(self):
        self.tel_panel = ctk.CTkFrame(self, width=280, fg_color="#FFFFFF")
        self.tel_panel.grid(row=0, column=2, sticky="nsew")
        ctk.CTkLabel(self.tel_panel, text="LIVE ANALYTICS", font=("Arial", 15, "bold"), text_color="#64748B").pack(pady=40)
        self.st_t = self.create_node("ACTIVE TEAMS", "0", "#3B82F6")
        self.st_p = self.create_node("SYSTEM NODES", "0", "#10B981")
        self.st_r = self.create_node("DATA RECORDS", "0", "#F59E0B")

    def create_node(self, title, val, color):
        node = ctk.CTkFrame(self.tel_panel, fg_color="#FBFDFF", corner_radius=20, border_width=1, border_color="#E2E8F0")
        node.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(node, text=title, font=("Arial", 10, "bold"), text_color="#94A3B8").pack(pady=(15,0))
        lbl = ctk.CTkLabel(node, text=val, font=("Arial", 30, "bold"), text_color=color)
        lbl.pack(pady=(0,15))
        return lbl

    def start_global_refresh_loop(self):

        if self.auto_refresh_enabled:
            if hasattr(self, 'current_page_name') and self.current_page_name == "Leaderboard":
                self.refresh_final_results(is_auto=True)
        self.after(5000, self.start_global_refresh_loop)

    def start_timer(self):
        self.remaining_time = 30
        self.timer_running = True
        self.update_timer_ui()

    def update_timer_ui(self):
        
        if not self.timer_running: 
            return
            
        if self.remaining_time >= 0:
           
            color = "#2563EB" if self.remaining_time > 10 else "#EF4444"
            
            
            self.timer_canvas.delete("timer_arc")
            extent = (self.remaining_time / 30) * 359
            self.timer_canvas.create_arc(10, 10, 70, 70, start=90, extent=extent, 
                                         outline=color, width=5, style="arc", tags="timer_arc")
            self.timer_lbl.configure(text=str(self.remaining_time), text_color=color)

            
            if self.remaining_time <= 5:
                
                if hasattr(self, 'q_label') and self.q_label.winfo_exists():
                    current_color = self.q_label.cget("text_color")
                   
                    next_color = "#EF4444" if current_color != "#EF4444" else "#10B981"
                    self.q_label.configure(text_color=next_color)
            

            self.remaining_time -= 1
            self.timer_id = self.after(1000, self.update_timer_ui)
        else:
            
            self.verify_visual_challenge(timeout=True)

    def show_feedback(self, success=True):
        feedback_overlay = ctk.CTkFrame(self, fg_color="transparent")
        feedback_overlay.place(relx=0.5, rely=0.5, anchor="center")
        symbol = "✅" if success else "❌"
        color = "#10B981" if success else "#EF4444"
        lbl = ctk.CTkLabel(feedback_overlay, text=symbol, font=("Arial", 250), text_color=color)
        lbl.pack()
        self.after(1200, feedback_overlay.destroy)

    def trigger_tech_intro_step(self, char_idx):
        full_title = "Tournament Roadmap"
        if char_idx <= len(full_title):
            self.dash_title.configure(text=full_title[:char_idx])
            self.after(40, lambda: self.trigger_tech_intro_step(char_idx + 1))
        else:
            self.show_milestones_step(0)

    def show_milestones_step(self, idx):
        if idx < len(self.milestones):
            self.milestones[idx].grid()
            self.after(300, lambda: self.show_milestones_step(idx + 1))
        else:
            self.instruction_frame.pack(fill="x", pady=(50, 0), padx=20)

    def animate_export_step(self, step):
        if not hasattr(self, 'export_btn'): return
        frames = [("#10B981", 0), ("#34D399", 2), ("#6EE7B7", 5), ("#34D399", 2)]
        color, width = frames[step % len(frames)]
        if self.export_btn.winfo_exists():
            self.export_btn.configure(border_color=color, border_width=width)
            self.after(150, lambda: self.animate_export_step(step + 1))

    def animate_challenge_btn(self):
        if not hasattr(self, 'start_btn'): return
        colors = ["#2563EB", "#1E40AF", "#3B82F6"]
        current_color = self.start_btn.cget("fg_color")
        next_color = colors[(colors.index(current_color) + 1) % len(colors)]
        self.start_btn.configure(fg_color=next_color)
        self.after(800, self.animate_challenge_btn)

    def build_dashboard(self):
        p = self.pages["Dashboard"]
        self.main_container = ctk.CTkFrame(p, fg_color="transparent")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        self.dash_title = ctk.CTkLabel(self.main_container, text="", font=("Segoe UI", 52, "bold"), text_color="#0F172A")
        self.dash_title.pack(pady=5)
        self.roadmap_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.roadmap_frame.pack()
        self.milestones = []
        steps = [("NODE SETUP", "💠", "Register team identities."), ("DATA INJECTION", "⚡", "Process live scores."), ("STANDINGS", "📊", "Generate analytics.")]
        for i, (title, icon, desc) in enumerate(steps):
            card = ctk.CTkFrame(self.roadmap_frame, fg_color="white", corner_radius=35, width=280, height=360, border_width=2, border_color="#E2E8F0")
            card.grid(row=0, column=i, padx=20)
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=icon, font=("Arial", 65)).pack(pady=(45, 15))
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 20, "bold"), text_color="#2563EB").pack()
            ctk.CTkLabel(card, text=desc, font=("Segoe UI", 14), text_color="#94A3B8", justify="center").pack(pady=25)
            card.grid_remove()
            self.milestones.append(card)
        self.instruction_frame = ctk.CTkFrame(self.main_container, fg_color="#F1F5F9", corner_radius=20)
        instruction_text = "SYSTEM ENGINE LOADED: 1. Register Nodes. 2. Select Event. 3. Participate in 5+ events to see results."
        ctk.CTkLabel(self.instruction_frame, text=instruction_text, font=("Segoe UI", 14, "italic"), text_color="#475569", justify="center").pack(pady=20, padx=20)

    def build_teams(self):
        p = self.pages["Teams"]
        f = ctk.CTkFrame(p, fg_color="white", corner_radius=30, width=600, height=750)
        f.place(relx=0.5, rely=0.5, anchor="center")
        f.pack_propagate(False)
        ctk.CTkLabel(f, text="Team Registry", font=("Arial", 28, "bold")).pack(pady=(30, 10))
        self.team_name_entry = ctk.CTkEntry(f, width=450, height=45, placeholder_text="Team Identity (Unique)")
        self.team_name_entry.pack(pady=10)
        self.member_entries = []
        for i in range(5):
            entry = ctk.CTkEntry(f, width=450, height=40, placeholder_text=f"Member Node {i+1}")
            entry.pack(pady=5)
            self.member_entries.append(entry)

        def commit_team_action():
            name = self.team_name_entry.get().strip()
            members = [m.get().strip() for m in self.member_entries if m.get().strip()]
            if not name:
                messagebox.showerror("Validation Error", "Team name is required!"); return
            if name in self.teams:
                messagebox.showerror("Error", "Team name already exists!"); return
            if len(members) < 5:
                messagebox.showerror("Validation Error", "All 5 member nodes must be filled!"); return
            if len(set(members)) < 5:
                messagebox.showerror("Error", "Member names must be unique within the team!"); return
            self.teams[name] = members
            messagebox.showinfo("Success", f"Team '{name}' registered!"); self.update_stats()
            self.team_name_entry.delete(0, 'end'); [m.delete(0, 'end') for m in self.member_entries]

        self.commit_btn = ctk.CTkButton(f, text="COMMIT TEAM", command=commit_team_action, width=320, height=55, fg_color="#3B8ED0")
        self.commit_btn.pack(pady=30)

    def build_players(self):
        p = self.pages["Players"]
        f = ctk.CTkFrame(p, fg_color="white", corner_radius=25, width=520, height=450)
        f.place(relx=0.5, rely=0.5, anchor="center")
        f.pack_propagate(False)
        ctk.CTkLabel(f, text="Individual Registry", font=("Arial", 22, "bold")).pack(pady=35)
        e = ctk.CTkEntry(f, width=380, height=50, placeholder_text="Player Identity (Unique)")
        e.pack(pady=25)
        
        def a():
            name = e.get().strip()
            if not name:
                messagebox.showerror("Error", "Player name cannot be empty!"); return
            if name in self.individuals:
                messagebox.showerror("Duplicate", "This player is already registered!"); return
            if any(name in members for members in self.teams.values()):
                messagebox.showerror("Error", "This name is already part of a registered team!"); return
            self.individuals.append(name); e.delete(0, 'end'); self.update_stats(); messagebox.showinfo("OK", "Player Logged")
            
        ctk.CTkButton(f, text="REGISTER NODE", command=a, width=280, height=50).pack(pady=25)

    def build_scoring(self):
        p = self.pages["Scoring"]
        self.score_root = ctk.CTkFrame(p, fg_color="white", corner_radius=30, width=650, height=750, border_width=1, border_color="#E2E8F0")
        self.score_root.place(relx=0.5, rely=0.5, anchor="center")
        self.score_root.pack_propagate(False)
        self.show_scoring_selection()

    
    def filter_events_by_type(self, choice):
        if choice == "Show Event":
            # تصفية الأحداث التي نوعها "Show"
            filtered = [k for k, v in self.event_config.items() if v.get("type") == "Show"]
        else:
            # تصفية الأحداث (Individual أو Team)
            filtered = [k for k, v in self.event_config.items() if v.get("type") == choice]
        
        self.event_drop.configure(values=filtered)
        if filtered:
            self.event_drop.set(filtered[0])
        else:
            self.event_drop.set("No Events Found")



    def show_scoring_selection(self):
        self.timer_running = False
        for w in self.score_root.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.score_root, text="Scoring Engine", font=("Arial", 28, "bold"), text_color="#1E293B").pack(pady=40)
        
        # إضافة خيار "Show Event" إلى الزر المقسم
        self.m_var = ctk.StringVar(value="Individual")
        self.mode_btn = ctk.CTkSegmentedButton(
            self.score_root, 
            values=["Individual", "Team", "Show Event"], # إضافة الخيار هنا
            variable=self.m_var, 
            command=lambda x: self.update_event_list(), 
            width=500, height=45
        )
        self.mode_btn.pack(pady=10)
        
        self.event_detail_lbl = ctk.CTkLabel(self.score_root, text="Select an event to see points & difficulty", font=("Segoe UI", 12), text_color="#64748B")
        self.event_detail_lbl.pack(pady=(10, 0))
        
        self.event_var = ctk.StringVar(value="Select Event")
        self.ev_menu = ctk.CTkOptionMenu(self.score_root, variable=self.event_var, values=[], width=450, height=45, command=self.on_event_change)
        self.ev_menu.pack(pady=15)
        
        self.target_var = ctk.StringVar(value="Select Node")
        self.drop = ctk.CTkOptionMenu(self.score_root, variable=self.target_var, width=450, height=45)
        self.drop.pack(pady=15)
        
        self.update_event_list()
        
        self.start_btn = ctk.CTkButton(self.score_root, text="START LIVE CHALLENGE", command=self.run_visual_challenge, fg_color="#2563EB", height=65, width=450, corner_radius=20, font=("Segoe UI", 16, "bold"))
        self.start_btn.pack(pady=50)
        self.animate_challenge_btn()

    def on_event_change(self, choice):
        if choice in self.event_config:
            pts = self.event_config[choice]["points"]
            diff = self.event_config[choice]["diff"]
            diff_color = "#10B981" if diff == "Easy" else "#F59E0B" if diff == "Medium" else "#EF4444"
            self.event_detail_lbl.configure(text=f"Value: {pts} PTS | Complexity: {diff}", text_color=diff_color)

    def update_event_list(self):
        current_mode = self.m_var.get()
        
        # تصفية الأسماء بناءً على النوع المختار (Individual, Team, or Show)
        # أضفنا التحقق من "Show Event" ليعرض الفعاليات التي نوعها "Show"
        display_names = [name for name, config in self.event_config.items() if config.get("type") == (current_mode if current_mode != "Show Event" else "Show")]
        
        self.ev_menu.configure(values=display_names)
        self.event_var.set("Select Event")
        self.event_detail_lbl.configure(text="Select an event to see points & difficulty", text_color="#64748B")
        
        # تحديد قائمة المشاركين (Nodes) بناءً على النوع
        if current_mode == "Individual":
            v = self.individuals
        elif current_mode == "Team":
            v = list(self.teams.keys())
        elif current_mode == "Show Event": # الإضافة هنا للتعامل مع خيار العرض
            # نجمع الأفراد والفرق معاً ليظهر الجميع في قائمة العرض
            v = self.individuals + list(self.teams.keys())
        else:
            v = []
            
        self.drop.configure(values=v if v else ["NULL"])
        self.target_var.set("Select Node")


    def run_visual_challenge(self):
        ev, node = self.event_var.get(), self.target_var.get()
        selected_type = self.m_var.get() # الحصول على النوع المختار (Individual/Team/Show Event)
        
        # 1. التحقق من الاختيارات
        if ev == "Select Event" or node in ["Select Node", "NULL"] or ev == "No Events Found":
            messagebox.showwarning("Incomplete", "Please select an event and a participant!")
            return

        # 2. المسار الخاص برواق الابتكار (Show Event)
        # إذا كان النوع المختار هو "Show Event" أو كان اسم الفعالية يحتوي على "Tech Expo"
        if selected_type == "Show Event" or "Tech Expo" in ev:
            self.setup_innovation_gallery(node)
            return

        # 3. المسار الخاص بالأحداث التنافسية (كما هي بدون أي تغيير)
        for w in self.score_root.winfo_children():
            w.destroy()
            
        # جلب بيانات السؤال والنقاط من القاموس
        q_data = self.event_config[ev]
        self.active_base_points = q_data.get("points", 0)

        # توجيه كل فعالية للعبة الخاصة بها
        if ev == "Logic Test(Individual)":
            self.setup_puzzle_game(node, ev)
            
        elif ev == "Robotics Team(Team)":
            self.setup_robot_game(node, ev) 
            
        elif ev == "Cyber Security(Individual)":
            self.setup_wire_game(node, ev) 
            
        elif ev == "Cloud Computing(Team)":
            self.setup_cloud_game(node, ev)
            
        else:
            # أي فعالية أخرى لا تملك واجهة رسومية خاصة تفتح نظام الـ Terminal التقليدي
            self.setup_terminal_game(node, ev, q_data)

    

    def setup_terminal_game(self, node, ev, q_data):
        self.active_answer = q_data["a"]
        
        
        ctk.CTkButton(self.score_root, text="⬅ ABORT", command=self.show_scoring_selection, 
                      fg_color="#475569", width=100).pack(anchor="nw", padx=15, pady=10)

        
        timer_frame = ctk.CTkFrame(self.score_root, fg_color="transparent")
        timer_frame.pack(pady=5)
        self.timer_canvas = tk.Canvas(timer_frame, width=70, height=70, bg="white", highlightthickness=0)
        self.timer_canvas.pack()
        self.timer_lbl = ctk.CTkLabel(self.timer_canvas, text="30", font=("Arial", 20, "bold"))
        self.timer_lbl.place(relx=0.5, rely=0.5, anchor="center")

        
        q_box = ctk.CTkFrame(self.score_root, fg_color="#0F172A", corner_radius=15, width=580, height=160)
        q_box.pack(pady=15); q_box.pack_propagate(False)
        self.q_label = ctk.CTkLabel(q_box, text="", font=("Consolas", 20, "bold"), text_color="#10B981", wraplength=500)
        self.q_label.place(relx=0.5, rely=0.5, anchor="center")

        # حقل الإدخال
        self.game_entry = ctk.CTkEntry(self.score_root, placeholder_text="Enter Result...", width=400, height=50)
        self.game_entry.pack(pady=10)
        
        # زر التنفيذ
        self.submit_btn = ctk.CTkButton(self.score_root, text="⚡ EXECUTE", command=self.verify_visual_challenge, 
                                         width=400, height=55, font=("Arial", 16, "bold"))
        self.submit_btn.pack(pady=10)

        # بدء الأنيميشن والوقت
        self.game_entry.configure(state="disabled")
        self.submit_btn.configure(state="disabled")
        self.animate_text(q_data["q"], 0)
        self.start_timer()

    def setup_puzzle_game(self, node, ev):
        """نظام البزل الملون للحدث المنطقي فقط"""
        colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6C5CE7"]
        parts = ["NUM 2", "NUM 4", "NUM 6", "NUM 8"]
        import random
        random.shuffle(parts)

        ctk.CTkLabel(self.score_root, text=" LOGIC PUZZLE", font=("Segoe UI", 26, "bold"), text_color="#1E40AF").pack(pady=10)
        ctk.CTkLabel(self.score_root, text="Which number comes next in the zone!", font=("Segoe UI", 12)).pack()

        self.cv = tk.Canvas(self.score_root, width=550, height=350, bg="#F1F5F9", highlightthickness=2)
        self.cv.pack(pady=15)
        self.cv.create_rectangle(50, 220, 500, 320, fill="#E2E8F0", outline="#94A3B8", dash=(5,5))
        
        self.placed_order = []
        for i, p in enumerate(parts):
            x, y = 80 + (i * 110), 60
            tag = f"pz_{i}"
            self.cv.create_rectangle(x, y, x+90, y+70, fill=colors[i], outline="white", width=2, tags=tag)
            self.cv.create_text(x+45, y+35, text=p, fill="white", font=("Arial", 11, "bold"), tags=tag)
            self.cv.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.start_drag(e, t))
            self.cv.tag_bind(tag, "<B1-Motion>", self.drag)
            self.cv.tag_bind(tag, "<ButtonRelease-1>", lambda e, t=tag: self.stop_puzzle_drag(e, t))

        self.verify_btn = ctk.CTkButton(self.score_root, text="VERIFY LOGIC", command=self.check_puzzle_logic, fg_color="#10B981", height=50, width=250)
        self.verify_btn.pack(pady=10)
        self.start_timer()

    def stop_puzzle_drag(self, event, tag):
        coords = self.cv.coords(tag)
        if coords[1] > 200:
            txt_item = self.cv.find_withtag(tag)[1]
            val = self.cv.itemcget(txt_item, "text")
            if val not in self.placed_order: self.placed_order.append(val)

    def check_puzzle_logic(self):
        if self.placed_order == ["NUM 2", "NUM 4", "NUM 6", "NUM 8"]:
            self.timer_running = False
            self.results.append({'name': self.target_var.get(), 'event': "Logic Test(Individual)", 'points': self.active_base_points + 10})
            self.show_feedback(success=True)
            self.after(1200, self.show_scoring_selection)
        else:
            self.show_feedback(success=False); self.placed_order = []
            messagebox.showwarning("Logic Error", "Order is incorrect! Try again.")

    def start_drag(self, event, tag):
        self._drag_data = {"x": event.x, "y": event.y, "item": tag}

    def drag(self, event):
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        self.cv.move(self._drag_data["item"], delta_x, delta_y)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_drag(self, event, tag):
        # التحقق إذا كانت القطعة داخل منطقة الهدف
        coords = self.cv.coords(tag)
        if coords[1] > 180:
            part_name = self.cv.itemcget(self.cv.find_withtag(tag)[1], "text")
            if part_name not in self.placed_order:
                self.placed_order.append(part_name)
                
                self.cv.itemconfig(tag, outline="#F59E0B")

    def check_puzzle(self):
        
        correct_order = ["NUM 2", "NUM 4", "NUM 6", "NUM 8"]
        if self.placed_order == correct_order:
            self.timer_running = False
            bonus = 10 if self.remaining_time > 15 else 0
            self.results.append({'name': self.target_var.get(), 'event': self.event_var.get(), 'points': self.active_base_points + bonus})
            self.show_feedback(success=True)
            self.after(1200, self.show_scoring_selection)
        else:
            self.show_feedback(success=False)
            self.placed_order = [] 
            messagebox.showwarning("Wrong Order", "The sequence is incorrect! Try again.")

    def animate_text(self, full_text, index):
        if index <= len(full_text):
            display = full_text[:index] + ("█" if index < len(full_text) else "")
            self.q_label.configure(text=display)
            self.after(50, lambda: self.animate_text(full_text, index + 1))
        else:
            self.game_entry.configure(state="normal")
            self.submit_btn.configure(state="normal")
            self.game_entry.focus()

    

    def verify_visual_challenge(self, timeout=False):
        self.timer_running = False
        if hasattr(self, 'timer_id'): self.after_cancel(self.timer_id)
        user_ans = self.game_entry.get().strip().lower() if not timeout else ""
        if not timeout and user_ans == self.active_answer:
            bonus = 5 if self.remaining_time > 20 else 2 if self.remaining_time > 10 else 0
            total_pts = self.active_base_points + bonus
            self.results.append({'name': self.target_var.get(), 'event': self.event_var.get(), 'points': total_pts})
            self.show_feedback(success=True)
            self.after(1200, self.show_scoring_selection)
        else:
            self.show_feedback(success=False)
            self.after(1200, self.show_scoring_selection)
        self.update_stats()

    def build_leaderboard(self):
        p = self.pages["Leaderboard"]
        
        for w in p.winfo_children(): w.destroy()
        
        ctk.CTkLabel(p, text="Live Standing Matrix", font=("Arial", 32, "bold")).pack(pady=20)

        controls_frame = ctk.CTkFrame(p, fg_color="transparent")
        controls_frame.pack(fill="x", padx=100, pady=10)

        self.emergency_btn = ctk.CTkButton(controls_frame, text=" EMERGENCY REFRESH",
                                          command=self.refresh_final_results,
                                          fg_color="#EF4444", hover_color="#B91C1C",
                                          height=45, width=200, font=("Arial", 12, "bold"))
        self.emergency_btn.pack(side="left", padx=10)

        
        self.edit_results_btn = ctk.CTkButton(controls_frame, text=" EDIT RESULTS",
                                         command=self.show_results_editor,
                                         fg_color="#F59E0B", hover_color="#D97706",
                                         height=45, width=200, font=("Arial", 12, "bold"))
        self.edit_results_btn.pack(side="left", padx=10)

        self.go_chart_btn = ctk.CTkButton(controls_frame, text="VIEW ANALYTICS",
                                         command=lambda: self.show_page("Analytics"),
                                         fg_color="#3B82F6", hover_color="#1D4ED8",
                                         height=45, width=200, font=("Arial", 12, "bold"))
        self.go_chart_btn.pack(side="left", padx=10)

        self.refresh_status = ctk.CTkLabel(controls_frame, text="Auto-Refresh: ACTIVE (5s)",
                                          font=("Arial", 11, "italic"), text_color="#10B981")
        self.refresh_status.pack(side="right", padx=20)

        self.lb_sc = ctk.CTkScrollableFrame(p, width=950, height=540, fg_color="white", corner_radius=25)
        self.lb_sc.pack(pady=10)

    def show_results_editor(self):
        """نافذة منبثقة محسنة تضمن ظهور النتائج فوراً"""
       
        if not self.results:
            messagebox.showinfo("Empty Data", "No matches recorded yet. Add some scores first!")
            return

        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Results Management Console")
        edit_win.geometry("750x550")
        edit_win.attributes("-topmost", True)
        edit_win.configure(fg_color="#F8FAFC")

        ctk.CTkLabel(edit_win, text="All Recorded Matches", font=("Arial", 22, "bold"), text_color="#1E293B").pack(pady=20)
        
        # إنشاء الفريم القابل للتمرير
        scroll = ctk.CTkScrollableFrame(edit_win, width=700, height=420, fg_color="white", corner_radius=15)
        scroll.pack(padx=20, pady=10, fill="both", expand=True)

       
        def build_rows():
            for w in scroll.winfo_children(): w.destroy()
            
            for i, res in enumerate(self.results):
                row = ctk.CTkFrame(scroll, fg_color="#F1F5F9", corner_radius=10)
                row.pack(fill="x", pady=4, padx=5)
                
               
                info_text = f"👤 {res['name']}  |  🎯 {res['event']}  |  ⭐ {res['points']} PTS"
                ctk.CTkLabel(row, text=info_text, font=("Consolas", 13), text_color="#334155").pack(side="left", padx=15, pady=10)

             
                def delete_item(idx=i):
                    if messagebox.askyesno("Confirm", "Delete this record?"):
                        self.results.pop(idx)
                        build_rows() 
                        self.update_stats()
                        self.refresh_final_results()

               
                def edit_item(idx=i):
                    dialog = ctk.CTkInputDialog(text=f"Change points for {self.results[idx]['name']}:", title="Edit Score")
                    new_val = dialog.get_input()
                    if new_val and new_val.isdigit():
                        self.results[idx]['points'] = int(new_val)
                        build_rows() # تحديث العرض فوراً
                        self.refresh_final_results()

                # أزرار التحكم
                ctk.CTkButton(row, text="🗑️", width=40, height=35, fg_color="#EF4444", hover_color="#B91C1C", 
                               command=delete_item).pack(side="right", padx=10)
                ctk.CTkButton(row, text=" Edit", width=70, height=35, fg_color="#3B82F6", hover_color="#1D4ED8",
                               command=edit_item).pack(side="right", padx=5)

        
        build_rows()

    def refresh_final_results(self, is_auto=False):
        if not hasattr(self, 'lb_sc'): return

        for w in self.lb_sc.winfo_children(): w.destroy()

        sorted_data = TournamentLogic.calculate_standings(self.results)
        if not sorted_data:
            ctk.CTkLabel(self.lb_sc, text="Waiting for nodes to complete 5 events...",
                        font=("Arial", 16), text_color="#94A3B8").pack(pady=100)
            return

        for i, (name, data) in enumerate(sorted_data):
            row = ctk.CTkFrame(self.lb_sc, fg_color="#F8FAFC", corner_radius=15, height=70)
            row.pack(fill="x", pady=5, padx=20)
            row.pack_propagate(False)

            rank_color = "#F59E0B" if i == 0 else "#94A3B8" if i == 1 else "#CD7F32" if i == 2 else "#1E293B"
            ctk.CTkLabel(row, text=f"#{i+1:02}", font=("Arial", 20, "bold"), text_color=rank_color, width=80).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=name.upper(), font=("Arial", 17, "bold"), anchor="w", text_color="#1E293B").pack(side="left")

            ctk.CTkLabel(row, text=f"({data['events']} Events)", font=("Arial", 12), text_color="#64748B").pack(side="right", padx=10)
            ctk.CTkLabel(row, text=f"{data['total_pts']} PTS", font=("Arial", 22, "bold"), text_color="#2563EB").pack(side="right", padx=20)

        if not is_auto:
            self.emergency_btn.configure(text=" REFRESHED!")
            self.after(1000, lambda: self.emergency_btn.configure(text="🚨 EMERGENCY REFRESH"))

    def build_analytics(self):
        p = self.pages["Analytics"]
        ctk.CTkLabel(p, text="Performance Analytics", font=("Arial", 32, "bold")).pack(pady=20)
        ctrl = ctk.CTkFrame(p, fg_color="white", corner_radius=20)
        ctrl.pack(fill="x", padx=40, pady=10)
        self.who_am_i_var = ctk.StringVar(value="Who are you?")
        self.who_menu = ctk.CTkOptionMenu(ctrl, variable=self.who_am_i_var, width=250)
        self.who_menu.pack(side="left", padx=20, pady=15)
        ctk.CTkButton(ctrl, text=" GENERATE CHART", command=self.render_charts, fg_color="#2563EB", height=50).pack(side="left", padx=20)
        self.chart_container = ctk.CTkFrame(p, fg_color="transparent")
        self.chart_container.pack(expand=True, fill="both", padx=40, pady=20)

    def render_charts(self):
        user_choice = self.who_am_i_var.get()
        if user_choice in ["Who are you?", "NULL"]:
            messagebox.showwarning("Selection Error", "Please select a node!"); return
        count = TournamentLogic.get_participation_count(self.results, user_choice)
        if count < 5:
            messagebox.showwarning("Locked", f"Need 5 events. Current: {count}/5"); return
        for w in self.chart_container.winfo_children(): w.destroy()
        df = pd.DataFrame(self.results)
        perf = df.groupby('name')['points'].sum().sort_values(ascending=False)
        colors = ['#F59E0B' if name == user_choice else '#3B82F6' for name in perf.index]
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        perf.plot(kind='bar', ax=ax, color=colors, edgecolor='black')
        ax.set_title(f"Tournament Standing - Focus: {user_choice}")
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def init_pages(self):
        for name in ["Dashboard", "Teams", "Players", "Scoring", "Leaderboard", "Analytics"]:
            f = ctk.CTkFrame(self.view_port, fg_color="transparent")
            self.pages[name] = f; f.grid(row=0, column=0, sticky="nsew")
        self.build_dashboard(); self.build_teams(); self.build_players(); self.build_scoring(); self.build_leaderboard(); self.build_analytics()

    def show_page(self, name):
        self.current_page_name = name
        self.pages[name].tkraise()
        if name == "Leaderboard": self.refresh_final_results()
        if name == "Analytics": self.update_analytics_who()
        self.update_stats()

    def update_analytics_who(self):
        all_nodes = list(self.teams.keys()) + self.individuals
        self.who_menu.configure(values=all_nodes if all_nodes else ["NULL"])

    def update_stats(self):
        if hasattr(self, 'st_t'):
            self.st_t.configure(text=str(len(self.teams)))
            self.st_p.configure(text=str(len(self.individuals)))
            self.st_r.configure(text=str(len(self.results)))

    def export_excel(self):
        if not self.results:
            messagebox.showwarning("Empty", "No data to export!"); return
        try:
            pd.DataFrame(self.results).to_excel("tournament_report.xlsx")
            messagebox.showinfo("Export Success", "Saved as tournament_report.xlsx")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
    
    def setup_wire_game(self, node, ev):
        """لعبة إصلاح الأسلاك مع التايمر وزر الإلغاء"""
        
        cancel_btn = ctk.CTkButton(self.score_root, text="⬅ ABORT MISSION", 
                                   command=self.show_scoring_selection, 
                                   fg_color="#475569", hover_color="#1E293B", 
                                   width=120, height=32, font=("Arial", 11, "bold"))
        cancel_btn.pack(anchor="nw", padx=20, pady=10)

        # --- منطقة العداد (Timer) ---
        timer_frame = ctk.CTkFrame(self.score_root, fg_color="transparent")
        timer_frame.pack(pady=5)
        self.timer_canvas = tk.Canvas(timer_frame, width=70, height=70, bg="white", highlightthickness=0)
        self.timer_canvas.pack(side="left")
        self.timer_lbl = ctk.CTkLabel(timer_frame, text="30", font=("Arial", 20, "bold"))
        self.timer_lbl.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.score_root, text=" NETWORK SECURITY REPAIR", font=("Segoe UI", 24, "bold"), text_color="#EF4444").pack(pady=5)
        ctk.CTkLabel(self.score_root, text=f"TARGET: {node}", font=("Consolas", 12), text_color="#3B82F6").pack()

        
        self.wire_cv = tk.Canvas(self.score_root, width=580, height=350, bg="#1E293B", highlightthickness=3, highlightbackground="#64748B")
        self.wire_cv.pack(pady=15)

        self.wire_colors = ["#FF3131", "#39FF14", "#FFFB00", "#1F51FF"]
        import random
        l_colors = list(self.wire_colors); random.shuffle(l_colors)
        r_colors = list(self.wire_colors); random.shuffle(r_colors)

        self.connections = 0
        self.selected_start = None

        for i in range(4):
            ly = 60 + (i * 75)
            self.wire_cv.create_oval(30, ly-15, 60, ly+15, fill=l_colors[i], tags=("wire", l_colors[i], "left"))
            ry = 60 + (i * 75)
            self.wire_cv.create_oval(520, ry-15, 550, ry+15, fill=r_colors[i], tags=("wire", r_colors[i], "right"))

        self.wire_cv.tag_bind("wire", "<Button-1>", self.on_wire_click)
        self.signal_status = self.wire_cv.create_text(290, 175, text=" NO SIGNAL", fill="#EF4444", font=("Arial", 18, "bold"))
        
        
        self.start_timer()

    def on_wire_click(self, event):
        item = self.wire_cv.find_closest(event.x, event.y)[0]
        tags = self.wire_cv.gettags(item)
        color, side = tags[1], tags[2]

        if not self.selected_start:
            self.selected_start = {"id": item, "color": color, "side": side}
            self.wire_cv.itemconfig(item, outline="white", width=4)
        else:
            if side != self.selected_start["side"] and color == self.selected_start["color"]:
                c1 = self.wire_cv.coords(self.selected_start["id"])
                c2 = self.wire_cv.coords(item)
                # رسم السلك
                self.wire_cv.create_line(c1[2], c1[1]+15, c2[0], c2[1]+15, fill=color, width=6, smooth=True)
                self.connections += 1
                if self.connections == 4:
                    self.wire_cv.itemconfig(self.signal_status, text="📶 SIGNAL ONLINE", fill="#39FF14")
                    self.timer_running = False
                    self.after(1000, lambda: self.finish_custom_game("Cyber Security(Individual)"))
            else:
                self.wire_cv.itemconfig(self.selected_start["id"], outline="", width=1)
            self.selected_start = None

    
    def setup_puzzle_game(self, node, ev):
        """لعبة البزل الملونة مع التلميح والتايمر وزر الإلغاء"""
        
        cancel_btn = ctk.CTkButton(self.score_root, text="⬅ ABORT MISSION", 
                                   command=self.show_scoring_selection, 
                                   fg_color="#475569", hover_color="#1E293B", 
                                   width=120, height=32, font=("Arial", 11, "bold"))
        cancel_btn.pack(anchor="nw", padx=20, pady=10)

       
        timer_frame = ctk.CTkFrame(self.score_root, fg_color="transparent")
        timer_frame.pack(pady=5)
        self.timer_canvas = tk.Canvas(timer_frame, width=70, height=70, bg="white", highlightthickness=0)
        self.timer_canvas.pack(side="left")
        self.timer_lbl = ctk.CTkLabel(timer_frame, text="30", font=("Arial", 20, "bold"))
        self.timer_lbl.place(relx=0.5, rely=0.5, anchor="center")

        
        ctk.CTkLabel(self.score_root, text=" LOGIC SEQUENCE", font=("Segoe UI", 24, "bold"), text_color="#2563EB").pack(pady=(5, 0))
        
        ctk.CTkLabel(self.score_root, text="Which number comes next in the zone!", font=("Segoe UI", 13, "italic"), text_color="#64748B").pack(pady=(0, 10))
        
        
        cartoon_colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6C5CE7"]
        
        self.cv = tk.Canvas(self.score_root, width=550, height=320, bg="#F1F5F9", highlightthickness=2)
        self.cv.pack(pady=10)
        
        
        self.cv.create_rectangle(50, 200, 500, 300, fill="#E2E8F0", outline="#94A3B8", dash=(5,5))
        self.cv.create_text(275, 250, text="DROP ZONE (2-4-6-8)", fill="#94A3B8", font=("Arial", 10, "bold"))
        
        parts_data = [("NUM 2", "#FF6B6B"), ("NUM 4", "#4ECDC4"), ("NUM 6", "#FFD93D"), ("NUM 8", "#6C5CE7")]
        import random
        random.shuffle(parts_data)
        
        self.placed_order = []

        for i, (p, col) in enumerate(parts_data):
            x, y = 80 + (i * 110), 40
            tag = f"pz_{i}"
            self.cv.create_rectangle(x, y, x+90, y+70, fill=col, outline="white", width=3, tags=tag)
            self.cv.create_text(x+45, y+35, text=p, fill="white", font=("Arial", 11, "bold"), tags=tag)
            
            self.cv.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.start_drag(e, t))
            self.cv.tag_bind(tag, "<B1-Motion>", self.drag)
            self.cv.tag_bind(tag, "<ButtonRelease-1>", lambda e, t=tag: self.stop_puzzle_drag(e, t))

        self.verify_btn = ctk.CTkButton(self.score_root, text="VERIFY LOGIC", 
                                        command=self.check_puzzle_logic, 
                                        fg_color="#10B981", height=45, width=250, corner_radius=12)
        self.verify_btn.pack(pady=10)
        
        self.start_timer()

    def stop_puzzle_drag(self, event, tag):
        if self.cv.coords(tag)[1] > 200:
            val = self.cv.itemcget(self.cv.find_withtag(tag)[1], "text")
            if val not in self.placed_order: self.placed_order.append(val)

    def check_puzzle_logic(self):
        if self.placed_order == ["NUM 2", "NUM 4", "NUM 6", "NUM 8"]:
            self.timer_running = False
            self.finish_custom_game("Logic Test(Individual)")
        else:
            self.show_feedback(False); self.placed_order = []

    def finish_custom_game(self, event_name):
        self.results.append({'name': self.target_var.get(), 'event': event_name, 'points': self.active_base_points + 5})
        self.show_feedback(True)
        self.after(1000, self.show_scoring_selection)

    
    def setup_robot_game(self, node, ev):
        
        import random
        
        
        cancel_btn = ctk.CTkButton(self.score_root, text="⬅ ABORT MISSION", 
                                   command=self.show_scoring_selection, 
                                   fg_color="#475569", width=120, height=32, font=("Arial", 11, "bold"))
        cancel_btn.pack(anchor="nw", padx=20, pady=10)

        # --- منطقة العداد (Timer) ---
        timer_frame = ctk.CTkFrame(self.score_root, fg_color="transparent")
        timer_frame.pack(pady=5)
        self.timer_canvas = tk.Canvas(timer_frame, width=70, height=70, bg="white", highlightthickness=0)
        self.timer_canvas.pack(side="left")
        self.timer_lbl = ctk.CTkLabel(timer_frame, text="30", font=("Arial", 20, "bold"))
        self.timer_lbl.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.score_root, text=" ROBOTIC ASSEMBLY", font=("Segoe UI", 24, "bold"), text_color="#7C3AED").pack(pady=(5, 0))
        ctk.CTkLabel(self.score_root, text="Drag parts to the frame to activate!", font=("Segoe UI", 13, "italic"), text_color="#64748B").pack(pady=(0, 10))

        # الكانفاس
        self.robot_cv = tk.Canvas(self.score_root, width=600, height=450, bg="#F1F5F9", highlightthickness=3, highlightbackground="#E2E8F0")
        self.robot_cv.pack(pady=10)

        # 1. رسم الهيكل الشبحي
        self.robot_cv.create_rectangle(245, 60, 335, 130, outline="#CBD5E1", width=2, dash=(4,4)) 
        self.robot_cv.create_rectangle(220, 140, 360, 280, outline="#CBD5E1", width=2, dash=(4,4)) 

        self.assembled_parts_count = 0
        positions = [(80, 100), (520, 100), (80, 300), (520, 300), (300, 400)]
        random.shuffle(positions)

        # --- رسم القطع الميكانيكية ---
        # الرأس
        x, y = positions[0]
        self.robot_cv.create_rectangle(x-40, y-30, x+40, y+30, fill="#06B6D4", outline="white", width=3, tags="HEAD")
        self.robot_cv.create_oval(x-20, y-10, x-5, y+5, fill="white", tags="HEAD")
        self.robot_cv.create_oval(x+5, y-10, x+20, y+5, fill="white", tags="HEAD")
        
        # الجسم
        x, y = positions[1]
        self.robot_cv.create_rectangle(x-60, y-60, x+60, y+60, fill="#3B82F6", outline="white", width=3, tags="BODY")
        self.robot_cv.create_oval(x-15, y-15, x+15, y+15, fill="#FACC15", tags="BODY") 
        
        # الذراع اليسرى
        x, y = positions[2]
        self.robot_cv.create_rectangle(x-10, y-40, x+10, y+40, fill="#94A3B8", outline="white", tags="L_ARM")
        
        # الذراع اليمنى
        x, y = positions[3]
        self.robot_cv.create_rectangle(x-10, y-40, x+10, y+40, fill="#94A3B8", outline="white", tags="R_ARM")

        # الأرجل
        x, y = positions[4]
        self.robot_cv.create_rectangle(x-35, y-20, x+35, y+20, fill="#1E293B", outline="white", tags="LEGS")

        # ربط السحب والتحريك
        for tag in ["HEAD", "BODY", "L_ARM", "R_ARM", "LEGS"]:
            self.robot_cv.tag_bind(tag, "<Button-1>", lambda e, t=tag: self.start_robot_drag_fixed(e, t))
            self.robot_cv.tag_bind(tag, "<B1-Motion>", self.drag_robot_fixed)
            self.robot_cv.tag_bind(tag, "<ButtonRelease-1>", lambda e, t=tag: self.stop_robot_drag_fixed(e, t))

        
        self.glow_effect = self.robot_cv.create_oval(180, 40, 420, 400, outline="#FACC15", width=0, state="hidden")

        
        self.timer_running = True
        self.start_timer()

    def start_robot_drag_fixed(self, event, tag):
        self._drag_data = {"x": event.x, "y": event.y, "tag": tag}
        self.robot_cv.tag_raise(tag)

    def drag_robot_fixed(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.robot_cv.move(self._drag_data["tag"], dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def stop_robot_drag_fixed(self, event, tag):
        targets = {"HEAD": (290, 95), "BODY": (290, 210), "L_ARM": (195, 210), "R_ARM": (385, 210), "LEGS": (290, 340)}
        bbox = self.robot_cv.bbox(tag)
        cx, cy = (bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2
        tx, ty = targets[tag]

        if abs(cx - tx) < 45 and abs(cy - ty) < 45:
            self.robot_cv.move(tag, tx - cx, ty - cy)
            self.robot_cv.tag_unbind(tag, "<Button-1>")
            self.robot_cv.tag_unbind(tag, "<B1-Motion>")
            self.assembled_parts_count += 1
            
            if self.assembled_parts_count == 5:
                self.timer_running = False
                self.trigger_robot_glow() 

    def trigger_robot_glow(self):
        """تأثير إضاءة صفراء خافتة وقوية (Pulse)"""
        self.robot_cv.itemconfig(self.glow_effect, state="normal")
        
        def pulse(width, growing):
            if not hasattr(self, 'score_root') or not self.score_root.winfo_exists(): return
            self.robot_cv.itemconfig(self.glow_effect, width=width)
            new_width = width + 2 if growing else width - 2
            if new_width > 15: growing = False
            if new_width < 2: growing = True
            self.after(50, lambda: pulse(new_width, growing))
        
        pulse(2, True)
        self.robot_cv.config(bg="#FFFBEB") # تغيير خلفية الكانفاس لصفرة خفيفة
        self.after(1500, lambda: self.finish_custom_game("Robotics Team(Team)"))

    def setup_cloud_game(self, node, ev):
        """لعبة جمع بيانات السحابة - Cloud Data Collector"""
        import random
        
        
        cancel_btn = ctk.CTkButton(self.score_root, text="⬅ ABORT MISSION", 
                                   command=self.show_scoring_selection, 
                                   fg_color="#475569", width=120, height=32, font=("Arial", 11, "bold"))
        cancel_btn.pack(anchor="nw", padx=20, pady=10)

        
        timer_frame = ctk.CTkFrame(self.score_root, fg_color="transparent")
        timer_frame.pack(pady=5)
        self.timer_canvas = tk.Canvas(timer_frame, width=70, height=70, bg="white", highlightthickness=0)
        self.timer_canvas.pack(side="left")
        self.timer_lbl = ctk.CTkLabel(timer_frame, text="30", font=("Arial", 20, "bold"))
        self.timer_lbl.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.score_root, text=" CLOUD DATA COLLECTOR", font=("Segoe UI", 24, "bold"), text_color="#3B82F6").pack()
        self.storage_lbl = ctk.CTkLabel(self.score_root, text="Cloud Storage: 0 GB", font=("Segoe UI", 14, "bold"), text_color="#10B981")
        self.storage_lbl.pack()

        
        self.cloud_cv = tk.Canvas(self.score_root, width=600, height=400, bg="#F0F9FF", highlightthickness=2, highlightbackground="#BAE6FD")
        self.cloud_cv.pack(pady=10)

        
        self.player = self.cloud_cv.create_oval(280, 180, 320, 220, fill="#3B82F6", outline="white", width=2)
        self.cloud_cv.create_text(300, 200, text="👨‍💻", font=("Arial", 16), tags="player_icon")

        self.cloud_storage = 0
        self.game_items = []
        self.timer_running = True
        
        # ربط حركة الماوس لتحريك اللاعب
        self.cloud_cv.bind("<Motion>", self.move_cloud_player)

        # إنشاء البيانات والمخاطر بشكل مستمر
        self.spawn_cloud_items()
        self.start_timer()

    def move_cloud_player(self, event):
        
        if not hasattr(self, 'player'): return
        self.cloud_cv.coords(self.player, event.x-20, event.y-20, event.x+20, event.y+20)
        self.cloud_cv.coords("player_icon", event.x, event.y)
        self.check_cloud_collisions(event.x, event.y)

    def spawn_cloud_items(self):
        
        if not self.timer_running: return
        
        import random
        x, y = random.randint(30, 570), random.randint(30, 370)
        
        # 70% بيانات، 30% مخاطر
        if random.random() > 0.3:
            item_type = random.choice(["⛁", "📑", "🗂️"])
            tag = "data"
            color = "#3B82F6"
        else:
            item_type = random.choice(["🦠", "⚠"])
            tag = "virus"
            color = "#EF4444"

        item = self.cloud_cv.create_text(x, y, text=item_type, font=("Arial", 20), tags=tag)
        self.game_items.append(item)
        
        # حذف العنصر بعد 3 ثوانٍ إذا لم يُجمع
        self.after(3000, lambda: self.remove_cloud_item(item))
        
        # توليد عنصر جديد كل ثانية
        self.after(800, self.spawn_cloud_items)

    def remove_cloud_item(self, item):
        if item in self.game_items:
            self.cloud_cv.delete(item)
            self.game_items.remove(item)

    def check_cloud_collisions(self, px, py):
        """التحقق من الاصطدام بالبيانات أو الفيروسات"""
        for item in self.game_items[:]:
            ix, iy = self.cloud_cv.coords(item)
            if abs(px - ix) < 25 and abs(py - iy) < 25:
                tags = self.cloud_cv.gettags(item)
                
                if "data" in tags:
                    self.cloud_storage += 10
                    self.storage_lbl.configure(text=f"Cloud Storage: {self.cloud_storage} GB")
                    self.cloud_cv.itemconfig(self.player, fill="#10B981") # وميض أخضر
                elif "virus" in tags:
                    self.cloud_storage = max(0, self.cloud_storage - 20)
                    self.storage_lbl.configure(text=f"Cloud Storage: {self.cloud_storage} GB")
                    self.cloud_cv.itemconfig(self.player, fill="#EF4444") # وميض أحمر
                
                self.remove_cloud_item(item)
                self.after(200, lambda: self.cloud_cv.itemconfig(self.player, fill="#3B82F6"))

        
        if self.cloud_storage >= 100:
            self.timer_running = False
            self.cloud_cv.create_text(300, 200, text=" CLOUD SYNCED!", font=("Arial", 30, "bold"), fill="#10B981")
            self.after(1000, lambda: self.finish_custom_game("Cloud Computing(Team)"))
    



    
    def setup_innovation_gallery(self, node):

     for widget in self.score_root.winfo_children():
        widget.destroy()

    # الخلفية
     main_bg = ctk.CTkFrame(self.score_root, fg_color="#B3DAF3")
     main_bg.pack(fill="both", expand=True)

    # الكرت الرئيسي 
     card = ctk.CTkFrame(
        main_bg,
        fg_color="white",
        corner_radius=20,
        width=1100,
        height=600
    )
     card.place(relx=0.5, rely=0.5, anchor="center")

    # تقسيم اليسار واليمين
     left_frame = ctk.CTkFrame(card, fg_color="#B3DAF3", corner_radius=15)
     left_frame.pack(side="left", fill="both", expand=True, padx=30, pady=30)

     right_frame = ctk.CTkFrame(card, fg_color="#ffffff", corner_radius=15)
     right_frame.pack(side="right", fill="both", expand=True, padx=30, pady=30)

    

     upload_icon = ctk.CTkLabel(
        left_frame,
        text="☁",
        font=("Segoe UI", 70),
        text_color="#0d48ac"
    )
     upload_icon.pack(pady=(50,20))

     upload_title = ctk.CTkLabel(
        left_frame,
        text="Upload your files",
        font=("Segoe UI", 22, "bold"),
        text_color="#0d48ac"
    )
     upload_title.pack(pady=5)

     upload_sub = ctk.CTkLabel(
        left_frame,
        text="Drop your files here\nor browse",
        font=("Segoe UI", 12),
        text_color="#9ca3af"
    )
     upload_sub.pack(pady=15)

     upload_btn = ctk.CTkButton(
        left_frame,
        text="Upload",
        fg_color="#3f7ed1",
        hover_color="#92bfee",
        width=100,
        height=45,
        command=self.handle_upload
    )
     upload_btn.pack(pady=25)

    # مكان عرض الصورة
     self.preview_area = ctk.CTkLabel(left_frame, text="")
     self.preview_area.pack(pady=20)

   

     title = ctk.CTkLabel(
        right_frame,
        text="Community Feedback",
        font=("Segoe UI", 20, "bold"),
        text_color="#374151"
    )
     title.pack(anchor="w", pady=(20,25), padx=20)

    # Likes
     self.likes_count = 0

     self.like_btn = ctk.CTkButton(
        right_frame,
        text=f" Like❤︎⁠  {self.likes_count}",
        fg_color="#B3DAF3",
        text_color="#e11d48",
        hover_color="#89bafa",
        height=45,
        command=self.trigger_like
    )
     self.like_btn.pack(fill="x", padx=20, pady=10)

    # Comments Box
     self.chat_box = ctk.CTkTextbox(
        right_frame,
        height=220,
        fg_color="#f9fafb",
        border_width=1,
        border_color="#e5e7eb"
    )
     self.chat_box.pack(fill="both", expand=True, padx=20, pady=20)

     self.chat_box.insert("end", "sushi_lver: Amazing project!\n")
     self.chat_box.insert("end", "cutie_pie: Love the design!\n")

    # Send message area
     send_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
     send_frame.pack(fill="x", padx=20, pady=15)

     self.msg_entry = ctk.CTkEntry(
        send_frame,
        placeholder_text="Write feedback..."
    )
     self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0,15))

     send_btn = ctk.CTkButton(
        send_frame,
        text="Send",
        width=90,
        fg_color="#89bafa",
        hover_color="#2d7feb",
        command=self.submit_feedback
    )
     send_btn.pack(side="right")


    def trigger_like(self):
     self.likes_count += 1
     self.like_btn.configure(text=f"Like❤︎⁠ {self.likes_count}")


    def trigger_clap(self):
        self.claps_count += 1
        self.clap_btn.configure(text=f" CLAP {self.claps_count}")


    def submit_feedback(self):

     comment = self.msg_entry.get()

     if comment:

        self.chat_box.insert(
            "end",
            f"💬:\n{comment}\n\n"
        )

        self.chat_box.see("end")
        self.msg_entry.delete(0, "end")


    def handle_upload(self):

     from tkinter import filedialog
     from PIL import Image, ImageTk

     file_path = filedialog.askopenfilename(
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )

     if file_path:

        img = Image.open(file_path)

        img = img.resize((350,220))

        self.tk_img = ImageTk.PhotoImage(img)

        self.preview_area.configure(image=self.tk_img)
                                         
if __name__ == "__main__":
    app = TechMasterTournament()
    login_gate = LoginScreen(on_success=app.deiconify)
    app.withdraw()
    login_gate.mainloop()



