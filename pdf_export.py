import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime

def pdf_bytes(sample_inputs: dict, pred: float, lo: float, hi: float,
              spec_min: float, status: str, roi: dict | None = None,
              logo_path: str = "electro-pi.png"):

    buff = io.BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    w, h = A4
    y = h - 90

    try:
        # === Logo ===
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, (w - 60) / 2, y,
                        width=60, height=60,
                        preserveAspectRatio=True, mask="auto")
            y -= 70
        except Exception as e:
            print("Logo not added:", e)

        # === Title ===
        c.setFont("Times-Bold", 14)
        c.drawCentredString(w / 2, y, "Cement 28-Day Strength Prediction Report")
        y -= 20

        # === Prediction ===
        c.setFont("Times-Roman", 11)
        c.drawString(60, y, f"Prediction: {pred:.2f} MPa (90% CI {lo:.2f}-{hi:.2f})")
        y -= 14
        c.drawString(60, y, f"Spec Minimum: {spec_min:.2f} MPa")
        y -= 14

        # === Status with color ===
        if "pass" in status.lower():
            c.setFillColor(colors.green)
        else:
            c.setFillColor(colors.red)

        c.drawString(60, y, f"Status: {status}")
        c.setFillColor(colors.black)  # reset back to black
        y -= 20

        # === Inputs Table ===
        inputs_data = [["Input", "Value"]] + [[k, str(v)] for k, v in sample_inputs.items()]
        inputs_table = Table(inputs_data, colWidths=[120, 100])
        inputs_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        _, inputs_h = inputs_table.wrap(0, 0)

        # === ROI Table ===
        roi_table, roi_h = None, 0
        if roi:
            roi_data = [["ROI Metric", "Value"]]
            roi_data.append(["Cement Savings", f"${roi['cement_saved_cost']:,.0f}"])
            roi_data.append(["Scrap Savings", f"${roi['scrap_savings']:,.0f}"])
            roi_data.append(["Lab Savings", f"${roi['lab_savings']:,.0f}"])
            roi_data.append(["Total Savings", f"${roi['total_savings']:,.0f}"])
            if roi.get("roi") is not None:
                roi_data.append(["ROI", f"{roi['roi']*100:,.0f}%"])
            if roi.get("payback_months") is not None:
                roi_data.append(["Payback", f"{roi['payback_months']:.1f} months"])

            roi_table = Table(roi_data, colWidths=[120, 100])
            roi_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]))
            _, roi_h = roi_table.wrap(0, 0)

        # === Align Tables by TOP ===
        table_h = max(inputs_h, roi_h)
        table_y = y - table_h
        inputs_table.drawOn(c, 60, table_y + (table_h - inputs_h))
        if roi_table:
            roi_table.drawOn(c, w / 2 + 40, table_y + (table_h - roi_h))

        y = table_y - 40

        # === Footer ===
        c.setFont("Times-Italic", 9)
        c.drawString(40, 30, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        c.save()
        buff.seek(0)
        return buff.getvalue()

    except Exception as e:
        print("PDF generation error:", e)
        return None
