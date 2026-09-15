import os
import smtplib
import mimetypes
import pandas as pd

from email.message import EmailMessage

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# -----------------------------
# Globals
# -----------------------------

excel_file = ""
resume_file = ""


# -----------------------------
# Browse Excel
# -----------------------------
def browse_excel():
    global excel_file

    excel_file = filedialog.askopenfilename(
        filetypes=[
            ("Excel", "*.xlsx"),
            ("CSV", "*.csv")
        ]
    )

    excel_path.set(excel_file)


# -----------------------------
# Browse Resume
# -----------------------------
def browse_resume():
    global resume_file

    resume_file = filedialog.askopenfilename(
        filetypes=[
            ("Resume", "*.pdf *.doc *.docx")
        ]
    )

    resume_path.set(resume_file)


# -----------------------------
# Read Data
# -----------------------------
def load_data(path):

    if path.endswith(".csv"):
        return pd.read_csv(path)

    return pd.read_excel(path)


# -----------------------------
# Mail Body
# -----------------------------
def create_body(job):

    return f"""
Dear Hiring Team,

I hope you are doing well.

I am writing to express my interest in the {job} position.

I have 4+ years of experience in Python, React, Node.js, SQL Server and MongoDB.

Please find my resume attached for your review.

Looking forward to hearing from you.

Regards,
Your Name
Phone:
LinkedIn:
"""


# -----------------------------
# Send Mail
# -----------------------------
def send_mail():

    if excel_file == "":
        messagebox.showerror("Error", "Select Excel/CSV")
        return

    if resume_file == "":
        messagebox.showerror("Error", "Select Resume")
        return

    sender = sender_email.get().strip()
    password = sender_password.get().strip()

    if sender == "" or password == "":
        messagebox.showerror("Error", "Enter Email and App Password")
        return

    df = load_data(excel_file)

    total = len(df)

    progress["maximum"] = total

    status.delete(1.0, tk.END)

    try:

        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(sender,password)

    except Exception as e:

        messagebox.showerror("Login Failed",str(e))
        return

    sent = 0

    for index,row in df.iterrows():

        receiver = str(row["Email"]).strip()
        job = str(row["Job_Name"]).strip()

        company = ""

        if "Company" in row:
            company = row["Company"]

        msg = EmailMessage()

        msg["Subject"] = f"Application for {job}"

        msg["From"] = sender

        msg["To"] = receiver

        msg.set_content(create_body(job))

        mime_type, _ = mimetypes.guess_type(resume_file)

        if mime_type is None:
            mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split("/")

        with open(resume_file,"rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(resume_file)
            )

        try:

            server.send_message(msg)

            status.insert(
                tk.END,
                f"✓ Sent -> {receiver}\n"
            )

            sent += 1

        except Exception as e:

            status.insert(
                tk.END,
                f"✗ Failed -> {receiver}\n{e}\n\n"
            )

        progress["value"] = index+1

        root.update()

    server.quit()

    messagebox.showinfo(
        "Completed",
        f"Total : {total}\nSent : {sent}"
    )


# -----------------------------
# UI
# -----------------------------

root = tk.Tk()

root.title("Bulk Job Mail Sender")

root.geometry("750x650")

sender_email = tk.StringVar()
sender_password = tk.StringVar()

excel_path = tk.StringVar()
resume_path = tk.StringVar()

tk.Label(root,text="Sender Gmail").pack()

tk.Entry(root,textvariable=sender_email,width=60).pack()

tk.Label(root,text="App Password").pack()

tk.Entry(
    root,
    textvariable=sender_password,
    show="*",
    width=60
).pack(pady=5)

tk.Button(
    root,
    text="Select Excel/CSV",
    command=browse_excel
).pack()

tk.Entry(
    root,
    textvariable=excel_path,
    width=80
).pack(pady=5)

tk.Button(
    root,
    text="Select Resume",
    command=browse_resume
).pack()

tk.Entry(
    root,
    textvariable=resume_path,
    width=80
).pack(pady=5)

tk.Button(
    root,
    text="Send Emails",
    bg="green",
    fg="white",
    font=("Arial",12,"bold"),
    command=send_mail
).pack(pady=10)

progress = ttk.Progressbar(
    root,
    length=500
)

progress.pack(pady=10)

status = tk.Text(
    root,
    height=20
)

status.pack(fill="both",expand=True)

root.mainloop()