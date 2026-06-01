"""
Servicio de generación de PDFs — Farmacia Génesis
Genera recetas médicas y facturas de venta en formato PDF.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


# Colores de la marca
CORAL = HexColor("#E05050")
TURQUESA = HexColor("#4EC8D4")
NAVY = HexColor("#0D1B2A")
GRIS = HexColor("#64748B")
BLANCO = HexColor("#FFFFFF")


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Brand', fontSize=22, fontName='Helvetica-Bold', textColor=CORAL, alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle(name='SubBrand', fontSize=10, fontName='Helvetica', textColor=GRIS, alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle(name='DocTitle', fontSize=16, fontName='Helvetica-Bold', textColor=NAVY, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name='Info', fontSize=10, fontName='Helvetica', textColor=NAVY, spaceAfter=3))
    styles.add(ParagraphStyle(name='InfoBold', fontSize=10, fontName='Helvetica-Bold', textColor=NAVY, spaceAfter=3))
    styles.add(ParagraphStyle(name='Footer', fontSize=8, fontName='Helvetica', textColor=GRIS, alignment=TA_CENTER, spaceBefore=20))
    return styles


class PDFService:

    @staticmethod
    def generate_receta(receta: dict, detalles: list, filepath: str):
        """Genera un PDF de receta médica."""
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = _get_styles()
        elements = []

        # Header
        elements.append(Paragraph("Farmacia Génesis", styles['Brand']))
        elements.append(Paragraph("Sistema de Gestión — Receta Médica", styles['SubBrand']))
        elements.append(Spacer(1, 8))

        # Línea separadora
        line_data = [[''] ]
        line_table = Table(line_data, colWidths=[doc.width])
        line_table.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 2, TURQUESA)]))
        elements.append(line_table)
        elements.append(Spacer(1, 12))

        # Datos del paciente y médico
        elements.append(Paragraph(f"<b>Receta No:</b> {receta['id_receta']}", styles['Info']))
        elements.append(Paragraph(f"<b>Fecha:</b> {str(receta['fecha'])[:16]}", styles['Info']))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>Paciente:</b> {receta['paciente']}", styles['Info']))
        elements.append(Paragraph(f"<b>Edad:</b> {receta.get('edad', 'N/A')}  |  <b>Género:</b> {receta.get('genero', 'N/A')}", styles['Info']))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<b>Médico:</b> Dr(a). {receta['medico']}", styles['Info']))
        elements.append(Paragraph(f"<b>Especialidad:</b> {receta.get('especialidad', 'General')}", styles['Info']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Diagnóstico:</b> {receta.get('diagnostico', '')}", styles['Info']))
        elements.append(Paragraph(f"<b>Tratamiento:</b> {receta.get('tratamiento', '')}", styles['Info']))
        elements.append(Spacer(1, 16))

        # Tabla de medicamentos
        if detalles:
            elements.append(Paragraph("Medicamentos Recetados", styles['DocTitle']))
            table_data = [['#', 'Medicamento', 'Cantidad', 'Dosis / Instrucciones']]
            for i, d in enumerate(detalles, 1):
                table_data.append([str(i), d['medicamento'], str(d['cantidad']), d.get('dosis', '')])

            t = Table(table_data, colWidths=[30, 180, 60, 230])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), TURQUESA),
                ('TEXTCOLOR', (0,0), (-1,0), BLANCO),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, GRIS),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [BLANCO, HexColor("#F0F4F8")]),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(t)

        elements.append(Spacer(1, 40))

        # Firma
        firma_data = [['', '_________________________'],
                      ['', f'Dr(a). {receta["medico"]}']]
        firma = Table(firma_data, colWidths=[doc.width*0.5, doc.width*0.5])
        firma.setStyle(TableStyle([
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('FONTNAME', (1,1), (1,1), 'Helvetica-Bold'),
            ('FONTSIZE', (1,0), (1,-1), 10),
            ('TEXTCOLOR', (1,1), (1,1), NAVY),
        ]))
        elements.append(firma)

        elements.append(Paragraph("Farmacia Génesis — Cuidamos tu salud", styles['Footer']))

        doc.build(elements)

    @staticmethod
    def generate_factura(venta: dict, detalles: list, filepath: str):
        """Genera un PDF de factura de venta."""
        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = _get_styles()
        elements = []

        elements.append(Paragraph("Farmacia Génesis", styles['Brand']))
        elements.append(Paragraph("Factura de Venta", styles['SubBrand']))
        elements.append(Spacer(1, 8))

        line_data = [[''] ]
        line_table = Table(line_data, colWidths=[doc.width])
        line_table.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 2, CORAL)]))
        elements.append(line_table)
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"<b>Factura No:</b> {venta['id_venta']}", styles['Info']))
        elements.append(Paragraph(f"<b>Fecha:</b> {str(venta['fecha'])[:16]}", styles['Info']))
        elements.append(Paragraph(f"<b>Cliente:</b> {venta['paciente']}", styles['Info']))
        elements.append(Spacer(1, 16))

        if detalles:
            table_data = [['#', 'Medicamento', 'Cantidad', 'Precio Unit.', 'Subtotal']]
            for i, d in enumerate(detalles, 1):
                table_data.append([
                    str(i), d['medicamento'], str(d['cantidad']),
                    f"Q {d['precio_unitario']:,.2f}", f"Q {d['subtotal']:,.2f}"
                ])
            # Fila de total
            table_data.append(['', '', '', 'TOTAL:', f"Q {venta['total']:,.2f}"])

            t = Table(table_data, colWidths=[30, 200, 60, 100, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), CORAL),
                ('TEXTCOLOR', (0,0), (-1,0), BLANCO),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (3,-1), (4,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-2), 0.5, GRIS),
                ('ROWBACKGROUNDS', (0,1), (-1,-2), [BLANCO, HexColor("#F0F4F8")]),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('FONTNAME', (3,-1), (4,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (3,-1), (4,-1), 12),
                ('TEXTCOLOR', (4,-1), (4,-1), CORAL),
                ('LINEABOVE', (3,-1), (4,-1), 2, NAVY),
            ]))
            elements.append(t)

        elements.append(Spacer(1, 30))
        elements.append(Paragraph("¡Gracias por su compra!", styles['DocTitle']))
        elements.append(Paragraph("Farmacia Génesis — Cuidamos tu salud", styles['Footer']))

        doc.build(elements)
