import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def pdf_bytes(sample_inputs: dict, pred: float, lo: float, hi: float, spec_min: float, status: str, roi: dict | None = None):
    buff = io.BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    w, h = A4
    y = h - 50

    try:
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, "Cement 28-Day Strength Prediction Report")
        y -= 30

        # Prediction
        c.setFont("Helvetica", 11)
        c.drawString(40, y, f"Prediction: {pred:.2f} MPa  (90% CI: {lo:.2f} – {hi:.2f} MPa)")
        y -= 18
        c.drawString(40, y, f"Spec Minimum: {spec_min:.2f} MPa")
        y -= 18
        c.drawString(40, y, f"Status: {status}")
        y -= 30

        # Inputs
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Inputs")
        y -= 16
        c.setFont("Helvetica", 10)
        for k, v in sample_inputs.items():
            c.drawString(50, y, f"{k}: {v}")
            y -= 14
            if y < 100:
                c.showPage()
                y = h - 50

        # ROI
        if roi:
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "ROI Summary")
            y -= 16
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Cement Savings: ${roi['cement_saved_cost']:,.0f}")
            y -= 14
            c.drawString(50, y, f"Scrap Savings: ${roi['scrap_savings']:,.0f}")
            y -= 14
            c.drawString(50, y, f"Lab Savings: ${roi['lab_savings']:,.0f}")
            y -= 14
            c.drawString(50, y, f"Total Savings: ${roi['total_savings']:,.0f}")
            y -= 14
            if roi.get("roi") is not None:
                c.drawString(50, y, f"ROI: {roi['roi']*100:,.0f}%")
                y -= 14
            if roi.get("payback_months") is not None:
                c.drawString(50, y, f"Payback: {roi['payback_months']:.1f} months")
                y -= 14

        c.showPage()
        c.save()
        buff.seek(0)
        return buff.getvalue()

    except Exception:
        return None
