from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import textwrap
import mysql.connector

now = datetime.now()
datetime = now.strftime("%d/%m/%Y %H:%M:%S")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="spartans@123",
    database="complaint_system"
)

cursor = conn.cursor()

def register_complaint():
    name = input("Enter your Name: ")
    division = input("Enter your class and div: ")
    complaint = input("Enter your Complaint: ")

    sql = "INSERT INTO complaints (name, division, complaint) VALUES (%s, %s, %s)"
    values = (name, division, complaint)
    cursor.execute(sql, values)
    conn.commit()
    print("Complaint registered successfully!")


def print_complaints():
    cursor.execute("SELECT * FROM complaints")
    results = cursor.fetchall()
    for row in results:
        print(row)

def download_complaints_pdf(filename="complaints.pdf"):
    # Fetch complaints from MySQL
    cursor.execute("SELECT id, name, division, complaint, date_time, status FROM complaints")
    results = cursor.fetchall()

    # Add table header
    data = [["ID", "Name", "Division", "Complaint", "Date & Time", "Status"]]

    # Helper function for wrapping long text
    def wrap_text(text, width=50):
        return "\n".join(textwrap.wrap(text, width))

        # Wrap complaint text manually
    for row in results:
        wrapped_row = [
            str(row[0]),
            row[1],
            row[2],
            wrap_text(row[3], 30),  # complaint wrapped
            str(row[4]),
            row[5]
            ]
        data.append(wrapped_row)

    # Create PDF
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    table = Table(data, repeatRows=1,  colWidths=[40, 110, 75, 145, 110, 70])  # repeat header on new pages

    # Add style to the table
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.cyan),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.rgb2cmyk(24, 181, 13)),
    ])

    table.setStyle(style)

    # Build the PDF
    pdf.build([table])

    print("PDF generated successfully:", filename)
