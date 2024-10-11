import datetime
import smtplib
import shutil
import subprocess
import os
import argparse
import tkinter as tk
from tkinter import messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from ping_hosts import ping_hosts, format_ping_result
import install_apache
import run_additional_playbook
import update_packages
import html_formatter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkhtmlview import HTMLLabel
from tkinter import font
import glob
from dotenv import load_dotenv

# Load environment variables from the .env file (if present)
load_dotenv()
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# File paths
log_file = "/root/CityUniversityProject/script.log"
report_file = "/root/CityUniversityProject/report.txt"
temp_report_file = "/root/CityUniversityProject/current_report.txt"
archive_folder = "/root/CityUniversityProject/archive_reports"

def log_message(message):
    with open(log_file, 'a') as log:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{timestamp} - {message}\n")

def send_email(subject, body, recipients, attachment_path=None):
    sender_email = "cityuniproject@gmail.com"
    password = EMAIL_PASSWORD  # Replace with your generated App Password
    # Create the email message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    # Convert body to UTF-8 if it's not already
    if isinstance(body, str):
        body = body.encode('utf-8', 'replace').decode('utf-8')  # Encode and decode to enforce UTF-8
    # Replace any non-breaking spaces with regular spaces
    body = body.replace('\xa0', ' ')
    # Attach the email body with UTF-8 encoding
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    # Attach the file if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)
    try:
        print(f"Sending email from: {sender_email} to: {recipients} with subject: {subject}")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipients, msg.as_string())
        print("Email sent successfully!")
        log_message("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
        log_message(f"Failed to send email: {e}")

def store_data(filename, data, section):
    with open(filename, 'a') as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {section}:\n{data}\n\n")
    log_message(f"Data stored in {filename} under section {section}")

def send_report(email_addresses):
   # ensure_report_exists(temp_report_file)
    try:
        if not os.path.exists(temp_report_file):
            log_message("Current report not found. Attempting to retrieve the latest archived report.")
            latest_archived_report = get_latest_archived_report()
            if latest_archived_report:
                shutil.copy(latest_archived_report, temp_report_file)
                log_message(f"Latest archived report copied: {latest_archived_report}")
            else:
                log_message("No archived reports found.")
                return
        with open(temp_report_file, 'r') as file:
            data = file.read()
        html_report = html_formatter.format_report_to_html(data)
        pdf_path = generate_pdf_report(html_report)
        recipients = [email.strip() for email in email_addresses.split(',')]
        send_email("Report", html_report, recipients, attachment_path=pdf_path)
        log_message("Report sent successfully.")
    except Exception as e:
        log_message(f"Failed to send report: {e}")
    finally:
        archive_current_report()

def get_latest_archived_report():
    try:
        # List all text reports in the archive folder
        archived_reports = glob.glob(os.path.join(archive_folder, "report_*.txt"))
        if archived_reports:
            # Sort by modification time (latest first) and return the latest report
            latest_report = max(archived_reports, key=os.path.getmtime)
            return latest_report
        else:
            log_message("No archived reports found.")
            return None
    except Exception as e:
        log_message(f"Error finding latest archived report: {e}")
        return None

def archive_current_report():
    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)
    if os.path.exists(temp_report_file):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(archive_folder, f"report_{timestamp}.txt")
        shutil.move(temp_report_file, archive_path)
        log_message(f"Archived current report to {archive_path}")
    else:
        log_message("No current report file found to archive.")

def generate_pdf_report(html_content):
    pdf_path = "/root/CityUniversityProject/report.pdf"
    from weasyprint import HTML
    HTML(string=html_content).write_pdf(pdf_path)
    log_message(f"PDF report generated at {pdf_path}")
    return pdf_path

def ping_hosts_function():
    # Get the raw result from the ping_hosts command
    raw_result = ping_hosts()
    print(f"Debug: Raw ping result = {raw_result}")  # Debug print
    # If there's a result, format it
    if raw_result:
        formatted_result = format_ping_result(raw_result)
    else:
	    formatted_result = "Ping operation did not return any results."
    # store_data(temp_report_file, formatted_result, "Machine Availability")
    
#    print(f"Debug: Formatted ping result = {formatted_result}")  # Debug print
    # Store the result in the report file
    
    store_data(temp_report_file, formatted_result, "Machine Availability")
    log_message("ping_hosts_function executed")
    
    # Return the formatted result for display
    return formatted_result

def install_apache_function():
    result = install_apache.install_apache()
    store_data(temp_report_file, result, "Software Installation")
    log_message("install_apache_function executed")
    return result

def run_python_playbook_function():
    result = run_additional_playbook.run_additional_playbook()
    store_data(temp_report_file, result, "Python Playbook Execution")
    log_message("run_python_playbook_function executed")
    return result

def update_packages_function():
    result = update_packages.update_packages()
    store_data(temp_report_file, result, "Package Updates")
    log_message("update_packages_function executed")
    return result

def send_report_function(email_addresses):
    send_report(email_addresses)

def create_main_window():
    global email_entry
    root = tk.Tk()
    root.title("Patch Management Tool")
    frame = tk.Frame(root, padx=15, pady=15)
    frame.pack(padx=5, pady=5)
    tk.Label(frame, text="Choose a function to run:").pack(pady=5)
    tk.Button(frame, text="Machine availability", command=lambda: display_result("Machine Availability", ping_hosts_function()), width=25).pack(pady=5)
    tk.Button(frame, text="Install Software", command=lambda: display_result("Software Installation", install_apache_function()), width=25).pack(pady=5)
    tk.Button(frame, text="Install Python", command=lambda: display_result("Python Playbook Execution", run_python_playbook_function()), width=25).pack(pady=5)
    tk.Button(frame, text="Update Softwares", command=lambda: display_result("Package Updates", update_packages_function()), width=25).pack(pady=5)
    tk.Label(frame, text="Enter recipient email addresses (comma-separated):").pack(pady=5)
    email_entry = tk.Entry(frame, width=50)
    email_entry.pack(pady=5)
    tk.Button(frame, text="Send Email Report", command=lambda: send_report_function(email_entry.get()), width=25).pack(pady=5)
    tk.Button(frame, text="Exit", command=root.quit, width=25).pack(pady=5)
    root.mainloop()


def display_result(title, raw_result):
    result_window = tk.Toplevel()
    result_window.title(title)
    result_window.geometry("800x600")  # Set window size (width x height)
    # Frame to hold the text widget and scrollbar
    text_frame = tk.Frame(result_window, padx=20, pady=20)  # Add padding around the frame
    text_frame.pack(fill='both', expand=True)
    # Text widget for displaying results
    text_widget = tk.Text(text_frame, wrap='word', padx=10, pady=10)
    
    # Ensure raw_result is a string before inserting it into the Text widget
    if not isinstance(raw_result, str):
        raw_result = str(raw_result)
    text_widget.insert('1.0', raw_result)  # Insert the result text into the text widget
    text_widget.config(state='disabled')  # Make the text widget read-only
    text_widget.pack(side='left', fill='both', expand=True)
    # Scrollbar for the text widget
    scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
    scrollbar.pack(side='right', fill='y')
    text_widget.config(yscrollcommand=scrollbar.set)
    # Button to close the result window
    close_button = tk.Button(result_window, text="Close", command=result_window.destroy)
    close_button.pack(pady=10)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch Management Tool")
    parser.add_argument('--task', choices=['ping', 'install', 'run_playbook', 'update', 'send_report', 'check_updates', 'impact_assessment'], help='Task to execute')
    parser.add_argument('--emails', help='Comma-separated list of email addresses for the report')
    args = parser.parse_args()
    log_message(f"Script started with arguments: {args}")
    log_message(f"Current working directory: {os.getcwd()}")
    if args.task:
        if args.task == 'ping':
            print(ping_hosts_function())
        elif args.task == 'install':
            print(install_apache_function())
        elif args.task == 'run_playbook':
            print(run_python_playbook_function())
        elif args.task == 'update':            
            print(update_packages_function())
        elif args.task == 'send_report' and args.emails:
            send_report_function(args.emails)
        else:
            print("Invalid task or missing email addresses for sending report.")
            log_message("Invalid task or missing email addresses for sending report.")
    else:
        create_main_window()
