from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def make_pdf(path, lines):
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER
    y = height - 72
    for line in lines:
        c.drawString(72, y, line)
        y -= 14
        if y < 72:
            c.showPage()
            y = height - 72
    c.save()

make_pdf("data/pdfs/guide_ai.pdf", [
    "This PDF is a mini guide about AI agents.",
    "Agents use tools to answer questions grounded in data.",
    "RAG means retrieve relevant context and generate an answer.",
    "Evaluation should include citation checking for reliability."
])

make_pdf("data/pdfs/travel_notes.pdf", [
    "Travel notes: Srinagar, Sonamarg, Gulmarg, Pahalgam.",
    "Dal Lake, Shalimar Bagh, Nishat Bagh are popular attractions.",
    "Wear layers in the valley; weather changes quickly.",
    "Always verify road conditions before planning long drives."
])

print("PDF files created successfully!")
