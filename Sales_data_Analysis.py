import sqlite3
import tkinter as tk 
from PIL import Image, ImageTk, ImageDraw
from tkinter import ttk,messagebox,filedialog
import pandas as pd
import os
import json

# ===== EMAIL SECURITY (ENV VARIABLES) =====
import smtplib
EMAIL_ID = os.getenv("APP_EMAIL")
EMAIL_PASS = os.getenv("APP_PASS")

import matplotlib.pyplot as plt
import random
import string
from tkinter import Listbox
from tkcalendar import DateEntry
import datetime
import time
import hashlib

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

#=========Top msg======================
def toast(msg, color="#2dbd6e", parent=None):
    try:
        p = parent if parent else root
        t = tk.Toplevel(p)
        t.overrideredirect(True)
        t.attributes("-topmost", True)

        sw = p.winfo_screenwidth()
        t.geometry(f"+{sw-350}+30")

        tk.Label(t, text=msg, bg=color, fg="white",
                 font=("Segoe UI",11,"bold"),
                 padx=20, pady=10).pack()

        t.after(2500, t.destroy)

        print("TOAST:", msg)   # debug
    except Exception as e:
        print("Toast Error:", e)


# ================= FILES ==================
def create_db():
    conn = sqlite3.connect("sales.db", timeout=5)
    cur = conn.cursor()

    #  USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        email TEXT,
        mobile TEXT,
    showpass TEXT
    )
    """)

    #  SALES TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales(
        order_id INTEGER PRIMARY KEY,
        date TEXT,
        product TEXT,
        category TEXT,
        quantity INTEGER,
        price REAL,
        region TEXT
    )
    """)

    conn.commit()
    conn.close()


#===================================
def log_user(username, action):

    conn = sqlite3.connect("sales.db")
    cur = conn.cursor()

    #  TABLE CREATE (NO DELETE)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_log(
        username TEXT,
        login_time TEXT,
        logout_time TEXT
    )
    """)

    if action == "login":
        cur.execute("""
        INSERT INTO login_log (username, login_time, logout_time)
        VALUES (?, datetime('now'), NULL)
        """, (username,))

    elif action == "logout":
        cur.execute("""
        UPDATE login_log
        SET logout_time = datetime('now')
        WHERE username=? AND logout_time IS NULL
        """, (username,))

    conn.commit()
    conn.close()
# ================= LOGIN ==================
def login():
    toast("Checking...", "#ffa500")

    if captcha_entry.get().strip() != cap.get():
        root.after(1200, lambda: toast("Invalid Captcha ❌", "#ff4d4d"))
        new_captcha()
        return

    u = username.get().strip()
    p = password.get().strip()

    if not u or not p:
        root.after(1200, lambda: toast("Username & Password required ❌", "#ff4d4d"))
        return

    try:
        conn = sqlite3.connect("sales.db", timeout=5)
        cur = conn.cursor()

        hp = hash_pass(p)

        cur.execute(
            "SELECT username, role FROM users WHERE username=? AND password=?",
            (u, hp)
        )

        result = cur.fetchone()

        if result:
            log_user(u, "login")
            global current_user, current_role

            current_user = result[0]
            role = result[1]
            current_role = role.capitalize() if role else "User"

           
            conn.commit()

            #  PROPER FLOW
            def show_welcome():
                toast(f"Welcome {u} 🎉", "#2dbd6e")

            def go_dashboard():
                root.withdraw()
                dashboard()

            root.after(1200, show_welcome)   # gap after Checking
            root.after(2500, go_dashboard)   # gap after Welcome

        else:
            root.after(1200, lambda: toast("Invalid Username or Password ❌", "#ff4d4d"))

    except Exception as e:
        print("Login Error:", e)
        root.after(1200, lambda: toast("Login Error ❌", "#ff4d4d"))

    finally:
        if conn:
            conn.close()

# ================= ENTER KEY NAVIGATION ==================
def focus_next(event):
    event.widget.tk_focusNext().focus()
    return "break"
#==================Forgot ===============================


import re

# Forgot Password OTP
OTP_STORE_FP = ""
OTP_TIME_FP = 0

# Register OTP
OTP_STORE_REG = ""
OTP_TIME_REG = 0

# ===== PASSWORD STRENGTH CHECK =====
def check_strong(passw):

    if len(passw) < 8:
        return "Minimum 8 characters password required "

    if not re.search("[A-Z]", passw):
        return "At least 1 Capital letter required"

    if not re.search("[a-z]", passw):
        return "At least 1 Small letter required"

    if not re.search("[0-9]", passw):
        return "At least 1 Number required"

    if not re.search("[@#$%&*!]", passw):
        return "At least 1 Special symbol @#$%&*!"

    return "OK"


def forgot_password():

    global OTP_STORE_FP, OTP_TIME_FP

    fw = tk.Toplevel(root)
    fw.title("Forgot Password")
    fw.state("zoomed")

    try:
        bg_img = Image.open("forgot.png")
        bg_img = bg_img.resize(
            (fw.winfo_screenwidth(), fw.winfo_screenheight()),
            Image.LANCZOS
        )
        bg_photo = ImageTk.PhotoImage(bg_img)

        bg_label = tk.Label(fw, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        fw.config(bg="#f5f5f5")

    box = tk.Frame(fw, bg="#ffffff", bd=3, relief="solid")
    box.place(relx=0.5, rely=0.5, anchor="center", width=560, height=680)

    content = tk.Frame(box, bg="#ffffff")
    content.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(content, text="🔐 FORGOT PASSWORD",
             font=("Arial", 24, "bold"),
             fg="#4a148c", bg="#ffffff").pack(pady=10)

    def input_box(label, show=""):
        tk.Label(content, text=label, bg="#ffffff",
                 font=("Arial", 12, "bold")).pack(anchor="w")

        f = tk.Frame(content, bg="black")
        f.pack(pady=6)

        e = tk.Entry(f, width=30, font=("Arial", 13), bd=0, show=show)
        e.pack(side="left", padx=6, pady=6)

        return e, f

    fu,_ = input_box("Username")
    fe,_ = input_box("Gmail")
    fo,_ = input_box("OTP")
    fn, pf = input_box("New Password", "*")

    eye = tk.Label(pf, text="👁", bg="white", cursor="hand2")
    eye.pack(side="right", padx=5)
    eye.bind("<Button-1>", lambda e: fn.config(show="" if fn.cget("show")=="*" else "*"))

    timer_lbl = tk.Label(content, font=("Arial", 14, "bold"), bg="#ffffff")
    timer_lbl.pack(pady=5)

    otp_verified = {"status": False}
    otp_attempts = {"count": 0}

    def start_timer(sec=60):
        def count():
            nonlocal sec

            if otp_verified["status"]:
                return

            if sec <= 0:
                timer_lbl.config(text="OTP Expired ❌", fg="red")
                btn_send.config(text="RESEND OTP", bg="#ff9933")
                return

            timer_lbl.config(text=f"⏳ {sec}s remaining", fg="#333")
            sec -= 1
            fw.after(1000, count)

        count()

    def send():
        global OTP_STORE_FP, OTP_TIME_FP

        conn = sqlite3.connect("sales.db")
        df = pd.read_sql_query("SELECT * FROM users", conn)
        conn.close()

        df.columns = df.columns.str.lower()

        u = fu.get().strip()
        email = fe.get().strip().lower()

        df["email"] = df["email"].astype(str).str.strip().str.lower()

        chk = df[(df["username"] == u) & (df["email"] == email)]
        if chk.empty:
            toast("Username & Gmail not matched ❌", "#ff4d4d", fw)
            return

        toast("Sending OTP...", "#ffa500")
        fw.update()

        OTP_STORE_FP = str(random.randint(100000, 999999))
        OTP_TIME_FP = time.time()
        otp_attempts["count"] = 0

        from email.mime.text import MIMEText

        try:
            if not EMAIL_ID or not EMAIL_PASS:
                toast("Email service not configured ❌", "#ff4d4d", fw)
                return

            
            msg = f"""

Dear {u},

We received a request to reset your password for your account.

🔑 Your One-Time Password (OTP) is:

        {OTP_STORE_FP}

⏳ This OTP is valid for 60 seconds only.

⚠️ Please do not share this OTP with anyone for security reasons.

----------------------------------------
Sales Management System
Security Team
----------------------------------------

Thank you,
Team Sales System 🚀
"""
            msg_obj = MIMEText(msg)
            msg_obj["From"] = EMAIL_ID
            msg_obj["To"] = email
            msg_obj["Subject"] = "Password Reset OTP"

            s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            s.login(EMAIL_ID, EMAIL_PASS)
            s.send_message(msg_obj)
            s.quit()

            toast("OTP Sent ✔", "#2dbd6e", fw)
            start_timer()

        except Exception as err:
            print("Mail Error:", err)
            toast("Mail Failed ❌", "#ff4d4d", fw)

    def verify():
        if time.time() - OTP_TIME_FP > 60:
            toast("OTP Expired ❌", "#ff4d4d", fw)
            return

        if fo.get() != OTP_STORE_FP:
            otp_attempts["count"] += 1

            if otp_attempts["count"] >= 3:
                toast("Too many attempts ❌", "#ff4d4d", fw)
                return

            toast(f"Invalid OTP ({otp_attempts['count']}/3) ❌", "#ff4d4d", fw)
            return

        otp_verified["status"] = True
        timer_lbl.config(text="✔ VERIFIED", fg="green")

        btn_verify.config(state="disabled")
        btn_change.config(state="normal")

        toast("OTP Verified ✔", "#2dbd6e", fw)

    def change_password():
        if not otp_verified["status"]:
            toast("Verify OTP First ❌", "#ff4d4d", fw)
            return

        p = fn.get().strip()
        res = check_strong(p)

        if res != "OK":
            toast(res, "#ff4d4d", fw)
            return

        conn = sqlite3.connect("sales.db")
        cur = conn.cursor()

        cur.execute("""
        UPDATE users 
        SET password=?, showpass=?
        WHERE username=? AND email=?
        """, (
            hash_pass(p),
            p,
            fu.get().strip(),
            fe.get().strip().lower()
        ))

        conn.commit()
        conn.close()

        toast("Password Changed Successfully ✔", "#2dbd6e", fw)
        fw.after(1200, fw.destroy)

    btn_send = tk.Button(content, text="SEND OTP",
        bg="#4da6ff", fg="white", font=("Arial",12,"bold"),
        width=26, height=2, command=send)
    btn_send.pack(pady=6)

    btn_verify = tk.Button(content, text="VERIFY OTP",
        bg="#2dbd6e", fg="white", font=("Arial",12,"bold"),
        width=26, height=2, command=verify)
    btn_verify.pack(pady=6)

    btn_change = tk.Button(content, text="CHANGE PASSWORD",
        bg="#6a0dad", fg="white", font=("Arial",13,"bold"),
        width=26, height=2, state="disabled",
        command=change_password)
    btn_change.pack(pady=6)


# ================= REGISTER WINDOW =================
def register_window():

    global OTP_STORE_REG, OTP_TIME_REG

    fw = tk.Toplevel(root)
    fw.title("Register New User")
    fw.state("zoomed")

    try:
        reg_bg = Image.open("register.png")
        reg_bg = reg_bg.resize(
            (fw.winfo_screenwidth(), fw.winfo_screenheight()),
            Image.LANCZOS
        )
        reg_bg_img = ImageTk.PhotoImage(reg_bg)

        bg_lbl = tk.Label(fw, image=reg_bg_img)
        bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
        bg_lbl.lower()

        fw.reg_bg_img = reg_bg_img

    except:
        fw.config(bg="#f5f5f5")

    box = tk.Frame(fw, bg="white", bd=3)
    box.place(relx=0.5, rely=0.5, anchor="center", width=560, height=720)

    content = tk.Frame(box, bg="white")
    content.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(content, text="CREATE ACCOUNT",
             font=("Arial", 24, "bold"),
             fg="#4a148c", bg="white").pack(pady=10)

    def input_box(label, show=""):
        tk.Label(content, text=label, bg="white",
                 font=("Arial", 12, "bold")).pack(anchor="w")

        f = tk.Frame(content, bg="black")
        f.pack(pady=6)

        e = tk.Entry(f, width=30, font=("Arial", 13),
                     bd=0, show=show)
        e.pack(side="left", padx=6, pady=6)

        return e, f

    fu,_ = input_box("Username")
    fe,_ = input_box("Email")
    fm,_ = input_box("Mobile")
    fo,_ = input_box("OTP")
    fn,_ = input_box("Password", "*")
    fc,_ = input_box("Confirm Password", "*")

    timer_lbl = tk.Label(content, text="", font=("Arial", 12, "bold"), bg="white")
    timer_lbl.pack()

    otp_verified = {"status": False}
    timer_running = {"run": False}

    def start_timer(sec=60):
        timer_running["run"] = True

        def count():
            nonlocal sec

            if not timer_running["run"]:
                return

            if sec <= 0:
                timer_lbl.config(text="OTP Expired ❌", fg="red")
                return

            timer_lbl.config(text=f"⏳ {sec}s remaining", fg="#333")
            sec -= 1
            fw.after(1000, count)

        count()

    def send():
        global OTP_STORE_REG, OTP_TIME_REG

        username = fu.get().strip()
        email = fe.get().strip().lower()

        if not username or not email:
            toast("Username & Email required ❌", "#ff4d4d", fw)
            return

        OTP_STORE_REG = str(random.randint(100000, 999999))
        OTP_TIME_REG = time.time()

        toast("Sending OTP...", "#ffa500", fw)
        fw.update()

        #  OLD STYLE OTP MESSAGE
        msg_text = f"""
Hello {username},

Your OTP for registration is: {OTP_STORE_REG}

⏳ Valid for 60 seconds.

If you did not request this, ignore this email.

------------------------------
Sales Management System
------------------------------
"""

        try:
            s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            s.login(EMAIL_ID, EMAIL_PASS)

            from email.mime.text import MIMEText
            msg = MIMEText(msg_text, "plain", "utf-8")
            msg["Subject"] = "OTP Verification"
            msg["From"] = EMAIL_ID
            msg["To"] = email

            s.send_message(msg)
            s.quit()

            toast("OTP Sent ✔", "#2dbd6e", fw)
            start_timer(60)

        except Exception as e:
            print("MAIL ERROR:", e)
            toast("Email Failed ❌", "#ff4d4d", fw)

    def verify():
        if time.time() - OTP_TIME_REG > 60:
            toast("OTP Expired ❌", "#ff4d4d", fw)
            return

        if fo.get().strip() != OTP_STORE_REG:
            toast("Invalid OTP ❌", "#ff4d4d", fw)
            return

        otp_verified["status"] = True
        timer_running["run"] = False

        timer_lbl.config(text="✔ VERIFIED", fg="green")

        btn_verify.config(state="disabled")
        btn_reg.config(state="normal")

        toast("OTP Verified ✔", "#2dbd6e", fw)

    def register_user():

        if not otp_verified["status"]:
            toast("Verify OTP First ❌", "#ff4d4d", fw)
            return

        if fn.get() != fc.get():
            toast("Password not matching ❌", "#ff4d4d", fw)
            return

        username = fu.get().strip()
        email = fe.get().strip().lower()
        password_plain = fn.get().strip()
        mobile = fm.get().strip()

        if not mobile.isdigit() or len(mobile) != 10:
            toast("Invalid Mobile Number ❌", "#ff4d4d", fw)
            return

        conn = sqlite3.connect("sales.db")
        cur = conn.cursor()

        try:
            cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
            if cur.fetchone():
                toast("Username already exists ❌", "#ff4d4d", fw)
                return

            cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
            if cur.fetchone():
                toast("Email already exists ❌", "#ff4d4d", fw)
                return

            cur.execute("""
            INSERT INTO users (username, password, email, mobile, role, showpass)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username,
                hash_pass(password_plain),
                email,
                int(mobile),
                "User",
                password_plain
            ))

            conn.commit()

        except Exception as err:
            print("REAL ERROR:", err)
            toast("DB Error ❌", "#ff4d4d", fw)
            return

        finally:
            conn.close()

        #  OLD STYLE WELCOME MESSAGE
        welcome_msg = f"""
Hello {username},

🎉 Your account has been created successfully!

Login Details:
Username: {username}
Password: {password_plain}

Please keep your credentials safe.

------------------------------
Sales Management System
------------------------------
"""

        try:
            s = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            s.login(EMAIL_ID, EMAIL_PASS)

            from email.mime.text import MIMEText
            msg = MIMEText(welcome_msg, "plain", "utf-8")
            msg["Subject"] = "Registration Successful"
            msg["From"] = EMAIL_ID
            msg["To"] = email

            s.send_message(msg)
            s.quit()

        except Exception as e:
            print("MAIL ERROR:", e)

        toast("Registered Successfully ✔", "#2dbd6e", fw)
        fw.after(1200, fw.destroy)

    tk.Button(content, text="SEND OTP",
              bg="#4da6ff", fg="white",
              font=("Arial",12,"bold"),
              width=25, command=send).pack(pady=5)

    btn_verify = tk.Button(content, text="VERIFY OTP",
              bg="#2dbd6e", fg="white",
              font=("Arial",12,"bold"),
              width=25, command=verify)
    btn_verify.pack(pady=5)

    btn_reg = tk.Button(content, text="REGISTER",
              bg="#6a0dad", fg="white",
              font=("Arial",13,"bold"),
              width=25,
              state="disabled",
              command=register_user)
    btn_reg.pack(pady=10)
#======================Card UI Function=================
def create_card(parent, title, value, color):

    frame = tk.Frame(parent, bg="white", bd=0)
    frame.config(width=180, height=100)  
    frame.pack_propagate(False)

    inner = tk.Frame(frame, bg=color)
    inner.place(relwidth=1, relheight=1)

    tk.Label(inner,
             text=title,
             bg=color,
             fg="white",
             font=("Segoe UI",10,"bold")).pack(pady=(10,3))

    tk.Label(inner,
             text=value,
             bg=color,
             fg="white",
             font=("Segoe UI",16,"bold")).pack()

    return frame

# ================= GLOBAL (MUST BE TOP) =================
if not os.path.exists("theme.json"):
    with open("theme.json", "w") as f:
        json.dump({"dark": False}, f)

with open("theme.json") as f:
    is_dark = json.load(f)["dark"]
current_role = "User"

# ================= BUTTON =================
def dash_btn(parent, text, cmd, color):

    btn = tk.Button(
        parent,
        text=text,
        bg=color,
        fg="white",
        font=("Segoe UI",14,"bold"),   
        width=20,                     
        height=1,                      
        command=cmd,
        cursor="hand2",
        bd=0,
        activebackground=color,
        activeforeground="white"
    )

    # Hover
    def on_enter(e):
        btn.config(bg="#0ea5e9")   # softer blue

    def on_leave(e):
        btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn

    

#==============Import Fun===========================
def import_excel():
    toast("Processing Excel...", "#ffa500")
    try:
        file = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if not file:
            return

        new_df = pd.read_excel(file)

        #  FIX 1: column normalize
        new_df.columns = new_df.columns.str.strip().str.lower()

        required_cols = ["order_id","date","product","category","quantity","price","region"]

        #  CHECK missing columns
        if not all(col in new_df.columns for col in required_cols):
            messagebox.showerror("Error", "Invalid Excel format ❌")
            return

        #  FIX 2: rename properly
        new_df.rename(columns={"order_id": "order_id"}, inplace=True)

        #  convert types
        new_df["order_id"] = pd.to_numeric(new_df["order_id"], errors="coerce").fillna(0).astype(int)
        new_df["quantity"] = pd.to_numeric(new_df["quantity"], errors="coerce").fillna(0)
        new_df["price"] = pd.to_numeric(new_df["price"], errors="coerce").fillna(0)

        conn = sqlite3.connect("sales.db", timeout=5)
        old_df = pd.read_sql_query("SELECT * FROM sales", conn)

        #  avoid duplicate IDs
        new_df = new_df[~new_df["order_id"].isin(old_df["order_id"])]

        #  FINAL COLUMN ORDER
        new_df = new_df[["order_id","date","product","category","quantity","price","region"]]

        new_df.to_sql("sales", conn, if_exists="append", index=False)
        conn.close()

        backup_db()  #  AUTO BACKUP

        toast("Excel Imported Successfully ✔")

    except Exception as e:
        print("Import Error:", e)
        messagebox.showerror("Error", "Import Failed ❌")
#=============================================================
def get_dashboard_stats():
    try:
        conn = sqlite3.connect("sales.db", timeout=5)
        df = pd.read_sql_query("SELECT * FROM sales", conn)
        conn.close()

        if df.empty:
            return 0, 0, "N/A", "N/A"

        #  COLUMN SAFE
        df.columns = df.columns.str.strip().str.lower()

        required = ["product", "region", "quantity", "price"]
        if not all(col in df.columns for col in required):
            return 0, 0, "N/A", "N/A"

        #  CLEAN DATA
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

        df["total"] = df["quantity"] * df["price"]

        #  CALCULATIONS
        total_sales = int(df["total"].sum())
        total_orders = len(df)

        #  SAFE idxmax (no crash if empty)
        product_group = df.groupby("product")["total"].sum()
        region_group = df.groupby("region")["total"].sum()

        top_product = product_group.idxmax() if not product_group.empty else "N/A"
        top_region = region_group.idxmax() if not region_group.empty else "N/A"

        return total_sales, total_orders, top_product, top_region

    except Exception as e:
        print("Stats Error:", e)
        return 0, 0, "N/A", "N/A"

# ================= VIEW USERS (ADMIN) =================
def view_users():
    w = open_colored_page("#e6f2ff","All Users")

    conn = sqlite3.connect("sales.db")
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()

    df.columns = df.columns.str.strip().str.lower()

    #  ADMIN → show real password
    if current_role == "Admin":
        if "showpass" in df.columns:
            df["password"] = df["showpass"]

    #  USER → hide password
    else:
        if "password" in df.columns:
            df = df.drop(columns=["password"])

    #  always hide showpass column
    if "showpass" in df.columns:
        df = df.drop(columns=["showpass"])

    # ===== TABLE =====
    tree = ttk.Treeview(w, columns=list(df.columns), show="headings")
    tree.pack(fill="both", expand=True)

    for col in df.columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center", width=150)

    for row in df.values:
        tree.insert("", "end", values=list(row))
#============Admin Login Log View==============
def view_logs():
    w = open_colored_page("#eef2ff", "Login Logs")

    conn = sqlite3.connect("sales.db")
    df = pd.read_sql_query("SELECT * FROM login_log", conn)
    conn.close()

    tree = ttk.Treeview(
        w,
        columns=["Username","Login Time","Logout Time"],
        show="headings"
    )
    tree.pack(fill="both", expand=True)

    tree.heading("Username", text="Username")
    tree.heading("Login Time", text="Login Time")
    tree.heading("Logout Time", text="Logout Time")

    tree.column("Username", anchor="center", width=150)
    tree.column("Login Time", anchor="center", width=200)
    tree.column("Logout Time", anchor="center", width=200)

    for _, row in df.iterrows():
        tree.insert("", "end", values=(
            row["username"],
            row["login_time"],
            row["logout_time"] if row["logout_time"] else "Active"
        ))
# ================= DASHBOARD =================
def dashboard():

    global is_dark

    dash = tk.Toplevel(root)
    dash.state("zoomed")
    dash.title("Sales Dashboard")

    # ===== THEME COLORS =====
    DARK_BG = "#0f172a"
    LIGHT_BG = "#f1f5f9"

    CARD_DARK = "#1e293b"
    CARD_LIGHT = "#ffffff"

    TEXT_DARK = "#ffffff"
    TEXT_LIGHT = "#000000"

    # ===== DEFAULT BG =====
    bg_color = DARK_BG if is_dark else LIGHT_BG
    card_color = CARD_DARK if is_dark else CARD_LIGHT
    text_color = TEXT_DARK if is_dark else TEXT_LIGHT

    dash.config(bg=bg_color)

    # ===== PROFILE =====
    profile_frame = tk.Frame(dash, bg=card_color, padx=10, pady=5)
    profile_frame.place(relx=0.01, rely=0.02, anchor="nw")

    user_lbl = tk.Label(
        profile_frame,
        text=f"👤 {current_user}",
        font=("Segoe UI", 11, "bold"),
        bg=card_color,
        fg=text_color
    )
    user_lbl.pack(anchor="w")

    role_lbl = tk.Label(
        profile_frame,
        text=f"Role: {current_role}",
        font=("Segoe UI", 9),
        bg=card_color,
        fg="#facc15" if is_dark else "#1f5cff"
    )
    role_lbl.pack(anchor="w")

    # ===== LOGOUT =====
    img = Image.open("logout.png").convert("RGBA")
    img = img.resize((60, 60), Image.LANCZOS)

    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 60, 60), fill=255)
    img.putalpha(mask)

    logout_photo = ImageTk.PhotoImage(img)
    dash.logout_photo = logout_photo  

    logout_frame = tk.Frame(dash, cursor="hand2", bg=bg_color)
    logout_frame.place(relx=0.97, rely=0.02, anchor="ne")

    icon_lbl = tk.Label(logout_frame, image=logout_photo, bd=0,
                        cursor="hand2", bg=bg_color)
    icon_lbl.pack()

    text_lbl = tk.Label(logout_frame, text="Logout",
                        font=("Segoe UI",10,"bold"),
                        cursor="hand2",
                        bg=bg_color,
                        fg="#f87171")
    text_lbl.pack()

    def logout_click(e):
        log_user(current_user, "logout")
        dash.destroy()
        root.deiconify()
        root.after(100, lambda: root.state("zoomed"))

    for w in (logout_frame, icon_lbl, text_lbl):
        w.bind("<Button-1>", logout_click)

    # ===== TITLE =====
    title_lbl = tk.Label(
        dash,
        text="📊 SALES DASHBOARD",
        font=("Segoe UI", 26, "bold"),
        bg=bg_color,
        fg="#38bdf8" if is_dark else "#1f5cff"
    )
    title_lbl.pack(pady=(25,15))

    # ===== STATS =====
    total_sales, total_orders, top_product, top_region = get_dashboard_stats()

    stats_frame = tk.Frame(dash, bg=bg_color)
    stats_frame.pack(pady=(20, 10))

    create_card(stats_frame, "💰 Total Sales", f"₹ {total_sales}", "#2563eb").grid(row=0, column=0, padx=20)
    create_card(stats_frame, "📦 Total Orders", total_orders, "#16a34a").grid(row=0, column=1, padx=20)
    create_card(stats_frame, "🏆 Top Product", top_product, "#ea580c").grid(row=0, column=2, padx=20)
    create_card(stats_frame, "🌍 Top Region", top_region, "#9333ea").grid(row=0, column=3, padx=20)

    # ===== PANEL =====
    canvas = tk.Canvas(dash, highlightthickness=0, bg=bg_color)
    scrollbar = tk.Scrollbar(dash, orient="vertical", command=canvas.yview)

    panel = tk.Frame(canvas, bg=bg_color)

    panel.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    window_id = canvas.create_window((0, 0), window=panel, anchor="n")

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def center_panel(event):
        canvas_width = event.width
        panel_width = panel.winfo_reqwidth()
        x = (canvas_width - panel_width) // 2
        canvas.coords(window_id, x, 0)

    canvas.bind("<Configure>", center_panel)

    # ===== BUTTONS =====
    dash_btn(panel,"➕ Add Record", add_record_form, "#1f5cff").pack(pady=15)
    dash_btn(panel,"📋 View Records", view_records, "#2dbd6e").pack(pady=15)

    if current_role == "Admin":
        dash_btn(panel,"📜 Login Logs", view_logs, "#444").pack(pady=10)
        dash_btn(panel,"👥 View Users", view_users, "#6a0dad").pack(pady=15)
        dash_btn(panel,"✏ Update Record", update_form, "#ff9933").pack(pady=15)
        dash_btn(panel,"🗑 Delete Record", delete_form, "#ff4d4d").pack(pady=15)

    dash_btn(panel,"📊 Sales Analysis", sales_analysis, "#7b2cff").pack(pady=15)
    dash_btn(panel,"📈 Show Charts", show_charts, "#17a2b8").pack(pady=15)
    dash_btn(panel,"📤 Export Excel", export_excel, "#5c6bc0").pack(pady=15)
    dash_btn(panel,"📥 Import Excel", import_excel, "#0ea5e9").pack(pady=15)

    # ===== THEME BUTTON =====
    theme_btn = tk.Label(
        dash,
        font=("Segoe UI Emoji", 16, "bold"),
        cursor="hand2",
        padx=10,
        pady=5,
        bg=bg_color,
        fg="#facc15"
    )
    theme_btn.place(relx=0.02, rely=0.95, anchor="sw")

    def update_theme():
        icon = "🌙" if is_dark else "☀️"
        mode = "Dark Mode" if is_dark else "Light Mode"
        theme_btn.config(text=f"{icon} {mode}")

    update_theme()

    # ===== TOGGLE =====
    def toggle_theme(e):
        nonlocal bg_color, card_color, text_color
        global is_dark

        is_dark = not is_dark

        bg_color = DARK_BG if is_dark else LIGHT_BG
        card_color = CARD_DARK if is_dark else CARD_LIGHT
        text_color = TEXT_DARK if is_dark else TEXT_LIGHT

        dash.config(bg=bg_color)
        stats_frame.config(bg=bg_color)
        panel.config(bg=bg_color)
        canvas.config(bg=bg_color)
        logout_frame.config(bg=bg_color)

        profile_frame.config(bg=card_color)
        user_lbl.config(bg=card_color, fg=text_color)
        role_lbl.config(bg=card_color,
                        fg="#facc15" if is_dark else "#1f5cff")

        text_lbl.config(bg=bg_color)

        title_lbl.config(
            bg=bg_color,
            fg="#38bdf8" if is_dark else "#1f5cff"
        )

        theme_btn.config(bg=bg_color)

        update_theme()

        with open("theme.json","w") as f:
            json.dump({"dark": is_dark}, f)

    theme_btn.bind("<Button-1>", toggle_theme)
# ========= helper fun ==========
def open_colored_page(color, title=""):
    w = tk.Toplevel()
    w.state("zoomed")      # ⭐ AUTO FULL SCREEN
    w.configure(bg=color)
    w.title(title)
    return w

# ================= CRUD ==================
def add_record_form():

    w = open_colored_page("#dbe7ff","Add Record")

    f = tk.Frame(w, bg="#dbe7ff")
    f.pack(expand=True, pady=40)

    e = {}

    region_values = ["North","South","West","East"]

    STYLE_WIDTH = 34
    FONT_STYLE = ("Segoe UI", 12)

    def next_order_id():
        try:
            conn = sqlite3.connect("sales.db")
            df = pd.read_sql_query("SELECT * FROM sales", conn)
            conn.close()
            if df.empty:
                return 1
            return int(df["order_id"].max()) + 1
        except:
            return 1

    def mark_error(widget):
        try:
            widget.config(highlightbackground="red", highlightthickness=2)
        except:
            pass

    def clear_error(widget):
        try:
            widget.config(highlightbackground="#999", highlightthickness=1)
        except:
            pass

    def focus_next(event):
        event.widget.tk_focusNext().focus()
        return "break"

    def lbl(text,r,c):
        tk.Label(
            f,
            text=text,
            bg="#dbe7ff",
            font=("Segoe UI",15,"bold")
        ).grid(row=r,column=c,padx=45,pady=(20,8),sticky="w")

    # ===== UI =====
    lbl("Order ID",0,0)
    lbl("Date",0,1)
    lbl("Product",0,2)

    lbl("Category",2,0)
    lbl("Quantity",2,1)
    lbl("Price",2,2)

    lbl("Region",4,1)

    # ===== FIELDS =====
    e["order_id"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["order_id"].grid(row=1,column=0,padx=60,pady=15)
    e["order_id"].insert(0, next_order_id())

    #  FIX: readonly remove
    e["order_id"].config(state="normal")

    e["Date"] = DateEntry(
        f,
        width=STYLE_WIDTH-2,
        date_pattern="dd-mm-yyyy",
        state="readonly",
        font=FONT_STYLE
    )
    e["Date"].grid(row=1,column=1,padx=45,pady=12)

    e["Product"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["Product"].grid(row=1,column=2,padx=45,pady=12)

    e["Category"] = ttk.Combobox(f,width=STYLE_WIDTH-2,font=FONT_STYLE)
    e["Category"].grid(row=3,column=0,padx=45,pady=12)

    e["Quantity"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["Quantity"].grid(row=3,column=1,padx=45,pady=12)

    e["Price"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["Price"].grid(row=3,column=2,padx=45,pady=12)

    e["Region"] = ttk.Combobox(f,values=region_values,width=STYLE_WIDTH-2,font=FONT_STYLE)
    e["Region"].grid(row=5,column=1,padx=45,pady=12)

    # ===== SAVE LOGIC =====
    def process_save():

        for k in e:
            clear_error(e[k])

        if not e["Product"].get().strip():
            toast("Product required ❌", "#ff4d4d", w)
            mark_error(e["Product"])
            return

        if not e["Category"].get().strip():
            toast("Category required ❌", "#ff4d4d", w)
            return

        if not e["Quantity"].get().isdigit():
            toast("Quantity must be number ❌", "#ff4d4d", w)
            return

        if not e["Price"].get().strip():
            toast("Price required ❌", "#ff4d4d", w)
            return

        try:
            price = float(e["Price"].get())
        except:
            toast("Price must be numeric ❌", "#ff4d4d", w)
            return

        reg = e["Region"].get()
        if reg not in region_values:
            toast("Select valid Region ❌", "#ff4d4d", w)
            return

        conn = sqlite3.connect("sales.db")
        cur = conn.cursor()

        try:
            oid_text = e["order_id"].get().strip()

            if not oid_text.isdigit():
                toast("Invalid Order ID ❌", "#ff4d4d", w)
                return

            oid = int(oid_text)

            #  SAFE COLUMN CHECK
            cur.execute("PRAGMA table_info(sales)")
            cols = [c[1].lower() for c in cur.fetchall()]

            if "order_id" not in cols:
                toast("order_id column missing ❌", "#ff4d4d", w)
                return

            #  DUPLICATE CHECK
            cur.execute("SELECT 1 FROM sales WHERE order_id=?", (oid,))
            if cur.fetchone():
                toast("Order ID exists ❌", "#ff4d4d", w)
                return

            #  INSERT
            cur.execute("""
                INSERT INTO sales 
                (order_id, date, product, category, quantity, price, region)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                oid,
                e["Date"].get(),
                e["Product"].get(),
                e["Category"].get(),
                int(e["Quantity"].get()),
                price,
                reg
            ))

            conn.commit()

        except Exception as err:
            print("DB ERROR:", err)
            toast("DB Error ❌", "#ff4d4d", w)
            return

        finally:
            conn.close()

        backup_db()
        toast("Saved ✔", "#2dbd6e", w)

    # ===== BUTTON =====
    def save():
        toast("Processing...", "#ffa500", w)
        w.after(800, process_save)

    # ===== ENTER KEY =====
    for field in e.values():
        field.bind("<Return>", focus_next)

    e["Region"].bind("<Return>", lambda e: save())

    tk.Button(
        f,
        text="SAVE",
        font=("Segoe UI",15,"bold"),
        bg="#2563eb",
        fg="white",
        width=24,
        height=2,
        bd=0,
        cursor="hand2",
        command=save
    ).grid(row=6,column=1,pady=40)


def view_records():
    toast("Loading Records...", "#ffa500")

    w = open_colored_page("#d9f3e7","View Records")
    w.geometry("1200x650")

    # ===== SEARCH BAR =====
    top = tk.Frame(w, bg="#d9f3e7")
    top.pack(fill="x", pady=10)

    tk.Label(top, text="Search Category :",
             bg="#d9f3e7",
             font=("Segoe UI",12,"bold")).pack(side="left", padx=10)

    search_cat = tk.Entry(top, width=30, font=("Segoe UI",12))
    search_cat.pack(side="left", padx=10)

    tk.Label(top, text="Search order_id :",
             bg="#d9f3e7",
             font=("Segoe UI",12,"bold")).pack(side="left", padx=10)

    search_id = tk.Entry(top, width=20, font=("Segoe UI",12))
    search_id.pack(side="left", padx=10)

    # ===== TABLE =====
    frame = tk.Frame(w)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(
        frame,
        columns=["order_id","Date","Product","Category","Quantity","Price","Region"],
        show="headings",
        height=20
    )
    tree.pack(fill="both", expand=True)

    for c in tree["columns"]:
        tree.heading(c, text=c)
        tree.column(c, width=150, anchor="center")

    tree.tag_configure("found", background="#fff2a8")

    # ===== LOAD DATA =====
    def load_data():
        tree.delete(*tree.get_children())

        conn = sqlite3.connect("sales.db")
        df = pd.read_sql_query("SELECT * FROM sales", conn)
        conn.close()

        df.columns = df.columns.str.lower()

        df.rename(columns={
            "order_id": "order_id",
            "date": "Date",
            "product": "Product",
            "category": "Category",
            "quantity": "Quantity",
            "price": "Price",
            "region": "Region"
        }, inplace=True)

        for row in df.values:
            tree.insert("", "end", values=list(row))

    # ===== CATEGORY SEARCH =====
    def search_category(event=None):

        text = search_cat.get().strip().lower()

        if not text:
            load_data()
            return

        found = False

        for item in tree.get_children():
            cat = tree.set(item, "Category").lower()

            if text in cat:
                tree.item(item, tags=("found",))
                found = True
            else:
                tree.delete(item)

        if not found:
            toast("No record found ❌", "#ff4d4d", w)
            load_data()

    # ===== ORDERID SEARCH =====
    def search_order_id(event=None):

        text = search_id.get().strip()

        if not text:
            load_data()
            return

        found = False

        for item in tree.get_children():
            oid = tree.set(item, "order_id")

            if text in oid:
                tree.item(item, tags=("found",))
                found = True
            else:
                tree.delete(item)

        if not found:
            toast("No record found ❌", "#ff4d4d", w)
            load_data()

    # ===== BIND =====
    search_cat.bind("<KeyRelease>", search_category)
    search_id.bind("<KeyRelease>", search_order_id)

    load_data()


def delete_form():
    toast("Processing...", "#ffa500")

    w = open_colored_page("#ffe0e0","Delete Record")

    f = tk.Frame(w,bg="#ffe0e0")
    f.pack(expand=True)

    tk.Label(
        f,
        text="DELETE RECORD",
        bg="#ffe0e0",
        font=("Segoe UI",22,"bold")
    ).pack(pady=20)

    # ===== FORMAT GUIDE =====
    tk.Label(
        f,
        text="Enter Order ID (Formats allowed):",
        bg="#ffe0e0",
        font=("Segoe UI",12,"bold")
    ).pack()

    tk.Label(
        f,
        text="Single → 5\nMultiple → 1,2,3\nRange → 1-10\nMix → 1,3-6,10",
        bg="#ffe0e0",
        fg="#333",
        font=("Segoe UI",11)
    ).pack(pady=5)

    oid = tk.Entry(f,width=35,font=("Segoe UI",14))
    oid.pack(pady=20)

    # ===== PARSE =====
    def parse_ids(text):
        ids = set()

        for p in text.split(","):
            p = p.strip()

            if "-" in p:
                try:
                    start, end = map(int, p.split("-"))
                    for i in range(start, end+1):
                        ids.add(i)
                except:
                    pass
            else:
                try:
                    ids.add(int(p))
                except:
                    pass

        return list(ids)

    # ===== DELETE FUNCTION =====
    def delete(event=None):

        raw = oid.get().strip()

        if not raw:
            toast("Enter Order ID ❌", "#ff4d4d", w)
            return

        ids = parse_ids(raw)

        if not ids:
            toast("Invalid input ❌", "#ff4d4d", w)
            return

        conn = sqlite3.connect("sales.db")
        cur = conn.cursor()

        # ===== COLUMN SAFE =====
        cur.execute("PRAGMA table_info(sales)")
        cols = [c[1].lower() for c in cur.fetchall()]

        if "order_id" in cols:
            col = "order_id"
        elif "order_id" in cols:
            col = "order_id"
        else:
            toast("order_id column not found ❌", "#ff4d4d", w)
            conn.close()
            return

        found_ids = []
        not_found = []

        for i in ids:
            cur.execute(f"SELECT 1 FROM sales WHERE {col}=?", (i,))
            if cur.fetchone():
                found_ids.append(i)
            else:
                not_found.append(i)

        if not found_ids:
            toast("No matching order_id found ❌", "#ff4d4d", w)
            conn.close()
            return

        # ===== DELETE =====
        for i in found_ids:
            cur.execute(f"DELETE FROM sales WHERE {col}=?", (i,))

        conn.commit()
        conn.close()

        backup_db()

        # ===== MESSAGE =====
        msg = f"Deleted: {found_ids}"
        if not_found:
            msg += f"\nNot Found: {not_found}"

        toast(msg + " ✔", "#2dbd6e", w)

        # REMOVE AUTO CLOSE
        # w.destroy()

        #  CLEAR FIELD AFTER DELETE
        oid.delete(0, tk.END)

    # ===== ENTER KEY DELETE =====
    oid.bind("<Return>", delete)

    # ===== BUTTON =====
    tk.Button(
        f,
        text="DELETE",
        bg="#ff4d4d",
        fg="white",
        font=("Segoe UI",13,"bold"),
        width=20,
        command=delete
    ).pack(pady=20)

def update_form():
    toast("Processing...", "#ffa500")
    w = open_colored_page("#fff0d9","Update Record")

    f = tk.Frame(w,bg="#fff0d9")
    f.pack(expand=True)

    e = {}
    region_values = ["North","South","West","East"]

    import re

    # ===== ERROR =====
    def mark_error(widget):
        try:
            widget.config(highlightbackground="red", highlightthickness=2)
            widget.focus()
        except:
            pass

    def clear_error(widget):
        try:
            widget.config(highlightbackground="#999", highlightthickness=1)
        except:
            pass

    # ===== CHECK ORDER ID FIRST =====
    def check_order_id(event=None):

        oid = e["order_id"].get().strip()

        if not oid:
            toast("Enter order_id first ❌","#ff4d4d", w)
            return "break"

        if not oid.isdigit():
            toast("OrderID must be number ❌","#ff4d4d", w)
            mark_error(e["order_id"])
            return "break"

        conn = sqlite3.connect("sales.db")
        cur = conn.cursor()

        #  COLUMN SAFE DETECT
        cur.execute("PRAGMA table_info(sales)")
        cols = [c[1].lower() for c in cur.fetchall()]

        if "order_id" in cols:
            col = "order_id"
        elif "order_id" in cols:
            col = "order_id"
        else:
            toast("OrderID column not found ❌", "#ff4d4d", w)
            return "break"

        cur.execute(f"SELECT * FROM sales WHERE {col}=?", (int(oid),))
        row = cur.fetchone()
        conn.close()

        if not row:
            toast("Order ID not found ❌","#ff4d4d", w)
            mark_error(e["order_id"])
            return "break"

        #  FOUND → MOVE NEXT
        e["Product"].focus()
        return "break"

    # ===== NEXT FIELD =====
    def focus_next(event):
        event.widget.tk_focusNext().focus()
        return "break"

    # ===== LABEL =====
    def lbl(text,r,c):
        tk.Label(f,text=text,bg="#fff0d9",
                 font=("Segoe UI",13,"bold")
        ).grid(row=r,column=c,padx=40,pady=(20,6),sticky="w")

    lbl("Order ID",0,0)
    lbl("Date",0,1)
    lbl("Product",0,2)

    lbl("Category",2,0)
    lbl("Quantity",2,1)
    lbl("Price",2,2)

    lbl("Region",4,1)

    STYLE_WIDTH = 34
    FONT_STYLE = ("Segoe UI", 12)

    # ===== FIELDS =====
    e["order_id"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["order_id"].grid(row=1,column=0,padx=45,pady=12)

    e["Date"] = DateEntry(f,width=STYLE_WIDTH-2,
                          date_pattern="dd-mm-yyyy",
                          state="readonly",
                          font=FONT_STYLE)
    e["Date"].grid(row=1,column=1,padx=45,pady=12)

    e["Product"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["Product"].grid(row=1,column=2,padx=45,pady=12)

    e["Category"] = ttk.Combobox(f,width=STYLE_WIDTH-2,font=FONT_STYLE)
    e["Category"].grid(row=3,column=0,padx=45,pady=12)

    e["Quantity"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["Quantity"].grid(row=3,column=1,padx=45,pady=12)

    e["Price"] = tk.Entry(f,width=STYLE_WIDTH,font=FONT_STYLE)
    e["Price"].grid(row=3,column=2,padx=45,pady=12)

    e["Region"] = ttk.Combobox(f,values=region_values,
                              width=STYLE_WIDTH-2,font=FONT_STYLE,
                              state="readonly")
    e["Region"].grid(row=5,column=1,padx=45,pady=12)

    # ===== ENTER CONTROL =====
    e["order_id"].bind("<Return>", check_order_id)

    for key in ["Product","Category","Quantity","Price"]:
        e[key].bind("<Return>", focus_next)

    e["Region"].bind("<Return>", lambda e: update())

    # ============== UPDATE FUNCTION ==============
    def update():

        for k in e:
            clear_error(e[k])

        # ===== EMPTY CHECK =====
        for key in ["order_id","Product","Category","Quantity","Price","Region"]:
            if not e[key].get().strip():
                toast(f"{key} required ❌","#ff4d4d", w)
                mark_error(e[key])
                return

        oid = e["order_id"].get().strip()

        if not oid.isdigit():
            toast("OrderID must be number ❌","#ff4d4d", w)
            return

        # ===== PRODUCT =====
        if not re.fullmatch(r"[A-Za-z ]+", e["Product"].get()):
            toast("Product must be letters ❌","#ff4d4d", w)
            return

        # ===== CATEGORY =====
        if not re.fullmatch(r"[A-Za-z ]+", e["Category"].get()):
            toast("Category must be letters ❌","#ff4d4d", w)
            return

        # ===== QUANTITY =====
        if not e["Quantity"].get().isdigit():
            toast("Quantity must be number ❌","#ff4d4d", w)
            return

        # ===== PRICE =====
        try:
            price = float(e["Price"].get())
        except:
            toast("Price must be number ❌","#ff4d4d", w)
            return

        # ===== REGION =====
        reg = e["Region"].get()
        if reg not in region_values:
            toast("Select valid Region ❌","#ff4d4d", w)
            return

        conn = sqlite3.connect("sales.db")
        cur = conn.cursor()

        cur.execute("""
        UPDATE sales SET date=?, product=?, category=?, quantity=?, price=?, region=?
        WHERE order_id=?
        """, (
            e["Date"].get(),
            e["Product"].get(),
            e["Category"].get(),
            int(e["Quantity"].get()),
            price,
            reg,
            oid
        ))

        conn.commit()
        conn.close()

        backup_db()

        toast("Record Updated ✔","#2dbd6e", w)
        w.destroy()

    # ===== BUTTON =====
    tk.Button(
        f,
        text="UPDATE",
        font=("Segoe UI",13,"bold"),
        bg="#ff9933",
        fg="white",
        width=22,
        height=2,
        command=update
    ).grid(row=6,column=1,pady=30)

def sales_analysis():
    toast("Calculating...", "#ffa500")
    try:
        conn = sqlite3.connect("sales.db", timeout=5)
        df = pd.read_sql_query("SELECT * FROM sales", conn)
        conn.close()

        if df.empty:
            messagebox.showerror("Error","No data ❌")
            return

        #  COLUMN FIX
        df.columns = df.columns.str.strip().str.lower()

        #  CLEAN DATA
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

        df["total"] = df["quantity"] * df["price"]

        #  CALCULATIONS
        total_sales = int(df["total"].sum())
        total_orders = len(df)

        top_product = df.groupby("product")["total"].sum().idxmax()
        top_region = df.groupby("region")["total"].sum().idxmax()

        avg_order = int(total_sales / total_orders) if total_orders > 0 else 0

        # ===== UI =====
        w = open_colored_page("#f0e6ff","Sales Analysis")

        tk.Label(
            w,
            text="📊 SALES ANALYSIS",
            font=("Segoe UI", 24, "bold"),
            fg="#6a0dad",
            bg="#f0e6ff"
        ).pack(pady=20)

        # ===== TOTAL =====
        tk.Label(
            w,
            text="💰 Total Sales",
            font=("Segoe UI",18,"bold"),
            bg="#f0e6ff"
        ).pack()

        tk.Label(
            w,
            text=f"₹ {total_sales}",
            font=("Segoe UI",42,"bold"),
            fg="#1f5cff",
            bg="#f0e6ff"
        ).pack(pady=10)

        # ===== EXTRA INFO =====
        info_frame = tk.Frame(w, bg="#f0e6ff")
        info_frame.pack(pady=20)

        def card(text, value, color):
            frame = tk.Frame(info_frame, bg=color, padx=20, pady=10)
            frame.pack(side="left", padx=20)

            tk.Label(frame, text=text, bg=color,
                     fg="white", font=("Segoe UI",12,"bold")).pack()

            tk.Label(frame, text=value, bg=color,
                     fg="white", font=("Segoe UI",16,"bold")).pack()

        card("📦 Orders", total_orders, "#16a34a")
        card("🏆 Top Product", top_product, "#ea580c")
        card("🌍 Top Region", top_region, "#9333ea")
        card("📊 Avg Order", f"₹ {avg_order}", "#2563eb")

    except Exception as e:
        print("Analysis Error:", e)
        messagebox.showerror("Error","Analysis Failed ❌")
# ================= CHARTS ==================
def show_charts():
    toast("Loading Charts...", "#ffa500")
    try:
        conn = sqlite3.connect("sales.db", timeout=5)
        df = pd.read_sql_query("SELECT * FROM sales", conn)
        conn.close()

        if df.empty:
            messagebox.showerror("Error", "No data to show charts ❌")
            return

        #  COLUMN SAFE
        df.columns = df.columns.str.strip().str.lower()

        required = ["category","region","product","quantity","price","date"]
        if not all(col in df.columns for col in required):
            messagebox.showerror("Error", "Invalid data format ❌")
            return

        #  CLEAN DATA
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

        df["total"] = df["quantity"] * df["price"]

        # ===== STYLE IMPROVEMENT =====
        plt.figure(figsize=(7,5))

        # 1️⃣ Category Wise (BAR)
        df.groupby("category")["total"].sum().plot(
            kind="bar",
            title="📊 Category Wise Sales"
        )
        plt.ylabel("Total Sales")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()

        # 2️⃣ Region Wise (PIE)
        plt.figure(figsize=(6,6))
        df.groupby("region")["total"].sum().plot(
            kind="pie",
            autopct="%1.1f%%",
            startangle=90,
            title="🌍 Sales by Region"
        )
        plt.ylabel("")
        plt.tight_layout()
        plt.show()

        # 3️⃣ Top Products (BAR)
        plt.figure(figsize=(7,5))
        df.groupby("product")["total"].sum() \
            .sort_values(ascending=False) \
            .head(5) \
            .plot(kind="bar", title="🏆 Top 5 Products")

        plt.ylabel("Total Sales")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()

        # 4️⃣ Monthly Trend (LINE)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")

        plt.figure(figsize=(8,5))
        df.groupby(df["date"].dt.to_period("M"))["total"].sum().plot(
            kind="line",
            marker="o",
            title="📈 Monthly Sales Trend"
        )

        plt.ylabel("Total Sales")
        plt.xlabel("Month")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print("Chart Error:", e)
        messagebox.showerror("Error", "Chart Failed ❌")
# ================= EXPORT EXCEL ==================

def export_excel():
    path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel File","*.xlsx")]
    )

    if path:
        try:
            #  get data from DB
            conn = sqlite3.connect("sales.db", timeout=5)
            df = pd.read_sql_query("SELECT * FROM sales", conn)
            conn.close()

            if df.empty:
                messagebox.showerror("Error", "No data to export ❌")
                return

            #  Excel export
            df.to_excel(path, index=False)

            messagebox.showinfo("Export", "Excel Exported Successfully ✔")

        except Exception as e:
            print("Export Error:", e)
            messagebox.showerror("Error", "Export Failed ❌")


#==========Backup data================
def backup_db():
    import shutil
    shutil.copy("sales.db", "backup_latest.db")
# ================= LOGIN UI ==================
create_db()
root = tk.Tk()
cap = tk.StringVar()

def new_captcha():
    s = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    cap.set(s)

new_captcha()



root.title("Login")
root.state("zoomed")

from PIL import ImageFilter

bg = Image.open("pg.png")
bg = bg.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.BICUBIC)
bg = bg.filter(ImageFilter.GaussianBlur(4))
bg_img = ImageTk.PhotoImage(bg)


tk.Label(root,image=bg_img).place(x=0,y=0,relwidth=1,relheight=1)
# ===== GLASS LOGIN CARD =====
card = tk.Frame(root, bg="#ffffff", bd=0, highlightthickness=0)
card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=780)

# subtle border (shadow feel)
card.config(highlightbackground="#ddd", highlightthickness=1)
content = tk.Frame(card,bg="#ffffff")
content.place(relx=0.5,rely=0.46,anchor="center")


# ===== LOGO =====

big_logo = Image.open("logo.png")
big_logo = big_logo.resize((300,180), Image.LANCZOS)
big_logo_photo = ImageTk.PhotoImage(big_logo)

logo_label = tk.Label(content, image=big_logo_photo)
logo_label.image = big_logo_photo
logo_label.pack(pady=(15,10))
tk.Label(content,
         text="SALES DATA ANALYSIS SYSTEM",
         bg="#ffffff",
         fg="#1f2937",
         font=("Segoe UI",16,"bold")
).pack()
def box(lbl, show=None):
    tk.Label(content, text=lbl, bg="white", font=("Segoe UI",11,"bold")).pack(anchor="w")

    e = tk.Entry(content, width=28, font=("Segoe UI",12),
                 bd=0,
                 highlightthickness=2,
                 highlightbackground="#ccc",
                 highlightcolor="#2563eb",
                 show=show)
    e.pack(pady=8, ipady=6)
    return e

username = box("User ID")

password = box("Password","*")

show_pass = tk.IntVar()
def toggle_pass():
    password.config(show="" if show_pass.get() else "*")

tk.Checkbutton(content,text="Show Password",variable=show_pass,
               bg="white",font=("Segoe UI",9),command=toggle_pass).pack(anchor="w")


tk.Label(content,text="Captcha",bg="white",font=("Segoe UI",11,"bold")).pack(anchor="w")
tk.Label(content,textvariable=cap,bg="#e6ebff",font=("Segoe UI",14,"bold"),width=8).pack(pady=3)
cap_box = tk.Frame(content, bg="#ccd4ff")
cap_box.pack(pady=4)

captcha_entry = tk.Entry(content, width=28, font=("Segoe UI",12),
                          bd=2, relief="solid", highlightthickness=1,
                          highlightbackground="#999", highlightcolor="#1f5cff")
captcha_entry.pack(pady=6, ipady=6)

username.bind("<Return>", focus_next)
password.bind("<Return>", focus_next)
captcha_entry.bind("<Return>", lambda e: login())
tk.Button(content,text="Refresh Captcha",command=new_captcha).pack(pady=4)



# ===== HOVER FUNCTION (add once above UI) =====
def hover(btn, c1, c2):
    btn.bind("<Enter>", lambda e: btn.config(bg=c1))
    btn.bind("<Leave>", lambda e: btn.config(bg=c2))


# ===== LOGIN BUTTON =====
login_btn = tk.Button(
    content,
    text="LOGIN",
    bg="#2563eb",
    fg="white",
    font=("Segoe UI",12,"bold"),
    width=22,
    height=2,
    bd=0,
    activebackground="#1e40af",
    cursor="hand2",
    command=login
)

login_btn.pack(pady=12)

# ===== APPLY HOVER =====
hover(login_btn, "#1e40af", "#2563eb")
fp=tk.Label(content,text="Forgot Password?",fg="#1f5cff",bg="white",
            cursor="hand2",font=("Segoe UI",10,"underline"))
fp.pack()
fp.bind("<Button-1>",lambda e:forgot_password())
tk.Frame(content,bg="#aaa",height=2,width=250).pack(pady=8)

tk.Button(content,
          text="Create New Account",
          bg="#2dbd6e",
          fg="white",
          font=("Segoe UI Semibold",11),
          width=20,
          height=1,
          bd=0,
          cursor="hand2",
          command=register_window).pack(pady=(5,5))

tk.Label(root,
         text="Existing users login above   |   New users create account",
         bg="#1f5cff",
         fg="white",
         font=("Segoe UI",11,"bold"),
         padx=12, pady=6).place(relx=0.5,rely=0.97,anchor="center")

root.mainloop()

