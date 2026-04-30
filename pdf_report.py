from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)

    y = 800
    c.setFont("Helvetica", 10)

    for item in data:
        c.drawString(50, y, str(item))
        y -= 20

    c.save()