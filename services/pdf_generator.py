import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas empresarial con numeración dinámica 'Página X de Y',
    marca de agua de seguridad y pie de página corporativo.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Línea de pie de página
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(36, 32, self._pagesize[0] - 36, 32)
        
        # Texto izquierdo
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.drawString(36, 20, f"Sistema de Gestión de Activos IT & Vulnerabilidades | Generado: {fecha_str}")
        
        # Clasificación central
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#94a3b8"))
        centro_x = self._pagesize[0] / 2
        self.drawCentredString(centro_x, 20, "CONFIDENCIAL — USO INTERNO")
        
        # Numeración derecha
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        texto_pagina = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(self._pagesize[0] - 36, 20, texto_pagina)
        self.restoreState()


def _crear_encabezado_senior(titulo, subtitulo, total_items=None, ancho_total=720):
    """
    Crea un bloque de cabecera ejecutivo con estética moderna y limpia
    """
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a')
    )
    
    tag_style = ParagraphStyle(
        'HeaderTag',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#1e40af'),
        alignment=2 # Right aligned
    )
    
    meta_style = ParagraphStyle(
        'HeaderMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569')
    )
    
    meta_right_style = ParagraphStyle(
        'HeaderMetaRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b'),
        alignment=2 # Right aligned
    )
    
    fecha_actual = datetime.now().strftime('%d de %B de %Y, %H:%M').replace('August', 'Agosto').replace('January', 'Enero')
    
    header_data = [
        [
            Paragraph(f"<b>{titulo}</b>", title_style),
            Paragraph("<font color='#2563eb'>●</font> <b>GESTIÓN DE CIBERSEGURIDAD IT</b>", tag_style)
        ],
        [
            Paragraph(f"{subtitulo}", meta_style),
            Paragraph(f"<b>Emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", meta_right_style)
        ]
    ]
    
    if total_items is not None:
        header_data.append([
            Paragraph(f"<b>Registros incluidos:</b> <font color='#0f172a'><b>{total_items}</b></font>", meta_style),
            Paragraph("<b>Estado del informe:</b> Oficial / Vigente", meta_right_style)
        ])
    
    header_table = Table(header_data, colWidths=[ancho_total * 0.65, ancho_total * 0.35])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements = [
        header_table,
        Spacer(1, 6),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=10)
    ]
    
    return elements


def generar_pdf_equipos(equipos):
    """
    Genera un PDF de nivel Senior con la tabla de inventario de Activos IT
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )
    
    story = []
    ancho_util = 720
    
    story.extend(_crear_encabezado_senior(
        titulo="Inventario de Activos IT y Criticidad",
        subtitulo="Auditoría de servidores, dispositivos de seguridad perimetral y estaciones",
        total_items=len(equipos),
        ancho_total=ancho_util
    ))
    
    styles = getSampleStyleSheet()
    
    # Métricas resumidas en la parte superior
    total_equipos = len(equipos)
    altos = sum(1 for e in equipos if e.get_criticidad_display() == 'Alta')
    medios = sum(1 for e in equipos if e.get_criticidad_display() == 'Media')
    bajos = sum(1 for e in equipos if e.get_criticidad_display() == 'Baja')
    
    stat_label = ParagraphStyle('StatLbl', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#64748b'))
    stat_val = ParagraphStyle('StatVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#0f172a'))
    
    stats_data = [[
        [Paragraph("TOTAL ACTIVOS", stat_label), Spacer(1, 2), Paragraph(str(total_equipos), stat_val)],
        [Paragraph("CRITICIDAD ALTA", stat_label), Spacer(1, 2), Paragraph(f"<font color='#dc2626'>{altos}</font>", stat_val)],
        [Paragraph("CRITICIDAD MEDIA", stat_label), Spacer(1, 2), Paragraph(f"<font color='#f59e0b'>{medios}</font>", stat_val)],
        [Paragraph("CRITICIDAD BAJA", stat_label), Spacer(1, 2), Paragraph(f"<font color='#16a34a'>{bajos}</font>", stat_val)]
    ]]
    
    stats_table = Table(stats_data, colWidths=[180, 180, 180, 180])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 10))
    
    # Estilos de celda
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('CellB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0f172a'))
    header_style = ParagraphStyle('HeadC', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    
    table_data = [[
        Paragraph("ID", header_style),
        Paragraph("Tipo de Activo", header_style),
        Paragraph("Modelo / Característica", header_style),
        Paragraph("Sistema Operativo", header_style),
        Paragraph("Direccionamiento / Host", header_style),
        Paragraph("Ambiente", header_style),
        Paragraph("Ubicación", header_style),
        Paragraph("Responsable / Área", header_style),
        Paragraph("Criticidad", header_style)
    ]]
    
    if not equipos:
        table_data.append([
            Paragraph("<font color='#64748b'>No hay activos registrados en la base de datos.</font>", cell_style),
            "", "", "", "", "", "", "", ""
        ])
    else:
        for eq in equipos:
            so_txt = eq.sistema_operativo or "N/A"
            if eq.version:
                so_txt += f" ({eq.version})"
                
            ip_host = []
            if eq.hostname:
                ip_host.append(eq.hostname)
            if eq.ip:
                ip_host.append(f"[{eq.ip}]")
            ip_host_str = " ".join(ip_host) if ip_host else "N/A"
            
            resp_area = []
            if eq.area_responsable:
                resp_area.append(eq.area_responsable)
            if eq.propietario:
                resp_area.append(f"({eq.propietario})")
            resp_area_str = " ".join(resp_area) if resp_area else "N/A"
            
            crit = eq.get_criticidad_display()
            if crit == 'Alta':
                crit_html = "<font color='#dc2626'><b>● Alta</b></font>"
            elif crit == 'Media':
                crit_html = "<font color='#f59e0b'><b>● Media</b></font>"
            elif crit == 'Baja':
                crit_html = "<font color='#16a34a'><b>● Baja</b></font>"
            else:
                crit_html = "<font color='#64748b'>N/A</font>"
                
            table_data.append([
                Paragraph(str(eq.id), cell_bold),
                Paragraph(f"<b>{eq.tipo or 'N/A'}</b>", cell_style),
                Paragraph(eq.caracteristica or 'N/A', cell_style),
                Paragraph(so_txt, cell_style),
                Paragraph(ip_host_str, cell_style),
                Paragraph(eq.ambiente or 'N/A', cell_style),
                Paragraph(eq.ubicacion or 'N/A', cell_style),
                Paragraph(resp_area_str, cell_style),
                Paragraph(crit_html, cell_style)
            ])
            
    col_widths = [28, 85, 115, 95, 115, 68, 74, 95, 45]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    story.append(t)
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


def generar_pdf_vulnerabilidades(vulnerabilidades, titulo="Reporte de Vulnerabilidades y Remediación"):
    """
    Genera un PDF de nivel Senior con la lista de vulnerabilidades, progreso y planes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )
    
    story = []
    ancho_util = 720
    
    story.extend(_crear_encabezado_senior(
        titulo=titulo,
        subtitulo="Gestión del ciclo de vida de vulnerabilidades, criticidad y avance de mitigación",
        total_items=len(vulnerabilidades),
        ancho_total=ancho_util
    ))
    
    styles = getSampleStyleSheet()
    
    # Resumen superior
    total = len(vulnerabilidades)
    completadas = sum(1 for v in vulnerabilidades if v.completada or v.estado_remediacion == 'Completada')
    pendientes = sum(1 for v in vulnerabilidades if not v.completada and v.estado_remediacion == 'Pendiente')
    en_proceso = total - completadas - pendientes
    if en_proceso < 0: en_proceso = 0
    
    stat_label = ParagraphStyle('StatLbl', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#64748b'))
    stat_val = ParagraphStyle('StatVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#0f172a'))
    
    stats_data = [[
        [Paragraph("TOTAL HALLAZGOS", stat_label), Spacer(1, 2), Paragraph(str(total), stat_val)],
        [Paragraph("PENDIENTES", stat_label), Spacer(1, 2), Paragraph(f"<font color='#f59e0b'>{pendientes}</font>", stat_val)],
        [Paragraph("EN PROCESO", stat_label), Spacer(1, 2), Paragraph(f"<font color='#3b82f6'>{en_proceso}</font>", stat_val)],
        [Paragraph("REMEDIADAS", stat_label), Spacer(1, 2), Paragraph(f"<font color='#16a34a'>{completadas}</font>", stat_val)]
    ]]
    
    stats_table = Table(stats_data, colWidths=[180, 180, 180, 180])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 10))
    
    cell_style = ParagraphStyle('VCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('VCellB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0f172a'))
    header_style = ParagraphStyle('VHeadC', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    
    table_data = [[
        Paragraph("Código / ID", header_style),
        Paragraph("Activo Afectado", header_style),
        Paragraph("Descripción del Hallazgo", header_style),
        Paragraph("Criticidad", header_style),
        Paragraph("Estado", header_style),
        Paragraph("Responsable", header_style),
        Paragraph("Avance", header_style),
        Paragraph("Fecha Obj.", header_style)
    ]]
    
    if not vulnerabilidades:
        table_data.append([
            Paragraph("<font color='#64748b'>No se encontraron vulnerabilidades para los filtros seleccionados.</font>", cell_style),
            "", "", "", "", "", "", ""
        ])
    else:
        for v in vulnerabilidades:
            codigo = v.codigo or f"VULN-{v.id}"
            
            eq_txt = "N/A"
            if v.equipo:
                eq_txt = f"<b>{v.equipo.tipo}</b><br/>{v.equipo.caracteristica or ''}"
                
            crit = v.criticidad or "Media"
            if crit == 'Alta':
                crit_html = "<font color='#dc2626'><b>● Alta</b></font>"
            elif crit == 'Media':
                crit_html = "<font color='#f59e0b'><b>● Media</b></font>"
            else:
                crit_html = "<font color='#16a34a'><b>● Baja</b></font>"
                
            estado = v.estado_remediacion or ("Completada" if v.completada else "Pendiente")
            if estado == 'Completada':
                estado_html = "<font color='#16a34a'><b>Completada</b></font>"
            elif estado == 'En proceso':
                estado_html = "<font color='#2563eb'><b>En proceso</b></font>"
            else:
                estado_html = "<font color='#d97706'><b>Pendiente</b></font>"
                
            avance = v.get_porcentaje_avance()
            avance_str = f"{avance:.1f}%" if isinstance(avance, (int, float)) else "0%"
            
            fecha_str = v.fecha_objetivo.strftime('%d/%m/%Y') if v.fecha_objetivo else "<font color='#94a3b8'>Sin fecha</font>"
            
            desc_corta = v.descripcion if len(v.descripcion) <= 220 else v.descripcion[:217] + "..."
            
            table_data.append([
                Paragraph(f"<b>{codigo}</b>", cell_bold),
                Paragraph(eq_txt, cell_style),
                Paragraph(desc_corta, cell_style),
                Paragraph(crit_html, cell_style),
                Paragraph(estado_html, cell_style),
                Paragraph(v.responsable or "<font color='#94a3b8'>Sin asignar</font>", cell_style),
                Paragraph(f"<b>{avance_str}</b>", cell_bold),
                Paragraph(fecha_str, cell_style)
            ])
            
    col_widths = [85, 105, 230, 55, 65, 80, 45, 55]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    
    story.append(t)
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


def generar_pdf_dashboard(datos_dash):
    """
    Genera un Informe Ejecutivo de Ciberseguridad en formato vertical (Portrait)
    con métricas ejecutivas, desglose de riesgos y top activos.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )
    
    story = []
    ancho_util = 540
    
    story.extend(_crear_encabezado_senior(
        titulo="Informe Ejecutivo de Ciberseguridad",
        subtitulo="Evaluación de postura de seguridad, exposición al riesgo y plan de remediación",
        total_items=None,
        ancho_total=ancho_util
    ))
    
    styles = getSampleStyleSheet()
    
    section_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=5
    )
    
    card_label = ParagraphStyle('CLbl', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#64748b'))
    card_val = ParagraphStyle('CVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#0f172a'))
    
    risk_index = datos_dash.get('risk_index', 0.0)
    risk_color = '#dc2626' if risk_index >= 60 else ('#f59e0b' if risk_index >= 30 else '#16a34a')
    risk_badge = 'ALTO' if risk_index >= 60 else ('MODERADO' if risk_index >= 30 else 'BAJO')
    
    risk_style = ParagraphStyle('RVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=17, textColor=colors.HexColor(risk_color))
    
    kpi_data = [
        [
            [Paragraph("ÍNDICE DE RIESGO", card_label), Spacer(1, 2), Paragraph(f"{risk_index}% <font size='8' color='{risk_color}'>({risk_badge})</font>", risk_style)],
            [Paragraph("TOTAL ACTIVOS IT", card_label), Spacer(1, 2), Paragraph(str(datos_dash.get('total_equipos', 0)), card_val)],
            [Paragraph("VULNERABILIDADES", card_label), Spacer(1, 2), Paragraph(str(datos_dash.get('total_vulnerabilidades', 0)), card_val)]
        ],
        [
            [Paragraph("CRÍTICAS / ALTAS", card_label), Spacer(1, 2), Paragraph(f"<font color='#dc2626'>{datos_dash.get('criticos', 0)}</font>", card_val)],
            [Paragraph("MEDIAS ACTIVAS", card_label), Spacer(1, 2), Paragraph(f"<font color='#f59e0b'>{datos_dash.get('medios', 0)}</font>", card_val)],
            [Paragraph("EFECTIVIDAD REMEDIACIÓN", card_label), Spacer(1, 2), Paragraph(f"<font color='#16a34a'>{datos_dash.get('porcentaje_corregidas', 0)}%</font>", card_val)]
        ]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[180, 180, 180])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#e2e8f0')),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 10))
    
    # 2. Resumen de Estados
    story.append(Paragraph("Estado de Remediación de Vulnerabilidades", section_title))
    
    pendientes = datos_dash.get('pendientes', 0)
    completadas = datos_dash.get('completadas', 0)
    total_vuln = datos_dash.get('total_vulnerabilidades', 1) or 1
    
    rem_data = [
        [
            Paragraph("<b>Estado de Mitigación</b>", card_label),
            Paragraph("<b>Cantidad</b>", card_label),
            Paragraph("<b>Porcentaje del Total</b>", card_label)
        ],
        [
            Paragraph("<font color='#d97706'><b>● Pendientes de Atención</b></font>", card_label),
            Paragraph(str(pendientes), card_val),
            Paragraph(f"<b>{(pendientes / total_vuln * 100):.1f}%</b>", card_label)
        ],
        [
            Paragraph("<font color='#16a34a'><b>● Remediadas y Verificadas</b></font>", card_label),
            Paragraph(str(completadas), card_val),
            Paragraph(f"<b>{(completadas / total_vuln * 100):.1f}%</b>", card_label)
        ]
    ]
    
    rem_table = Table(rem_data, colWidths=[240, 150, 150])
    rem_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(rem_table)
    story.append(Spacer(1, 10))
    
    # 3. Top Activos
    story.append(Paragraph("Activos con Mayor Nivel de Exposición", section_title))
    
    top_activos = datos_dash.get('top_activos', [])
    top_data = [[
        Paragraph("ID", card_label),
        Paragraph("Activo / Equipo", card_label),
        Paragraph("Modelo / Característica", card_label),
        Paragraph("Criticidad", card_label),
        Paragraph("Total", card_label),
        Paragraph("Pendientes", card_label),
        Paragraph("Completadas", card_label)
    ]]
    
    if not top_activos:
        top_data.append([
            Paragraph("<font color='#64748b'>No hay activos con hallazgos activos.</font>", card_label),
            "", "", "", "", "", ""
        ])
    else:
        for item in top_activos[:8]:
            crit = item.get('criticidad', 'N/A')
            crit_color = '#dc2626' if crit == 'Alta' else ('#f59e0b' if crit == 'Media' else '#16a34a')
            
            top_data.append([
                Paragraph(str(item.get('id', '')), card_label),
                Paragraph(f"<b>{item.get('tipo', 'N/A')}</b>", card_label),
                Paragraph(item.get('caracteristica', 'N/A'), card_label),
                Paragraph(f"<font color='{crit_color}'><b>● {crit}</b></font>", card_label),
                Paragraph(f"<b>{item.get('total_vulnerabilidades', 0)}</b>", card_label),
                Paragraph(f"<font color='#d97706'><b>{item.get('pendientes', 0)}</b></font>", card_label),
                Paragraph(f"<font color='#16a34a'><b>{item.get('completadas', 0)}</b></font>", card_label)
            ])
            
    top_table = Table(top_data, colWidths=[25, 115, 150, 65, 55, 65, 65])
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(top_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


def generar_pdf_nist(datos_nist):
    """
    Genera un Informe Oficial de Evaluación y Madurez de Ciberseguridad NIST CSF 2.0 (Portrait)
    con scores por función, nivel de Tier y recomendaciones de auditoría.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45
    )
    
    story = []
    ancho_util = 540
    
    story.extend(_crear_encabezado_senior(
        titulo="Evaluación de Ciberseguridad NIST CSF 2.0",
        subtitulo="Auditoría de madurez por funciones de seguridad, gobernanza y gestión del riesgo",
        total_items=None,
        ancho_total=ancho_util
    ))
    
    styles = getSampleStyleSheet()
    
    sec_title = ParagraphStyle(
        'NISTSecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=5
    )
    
    card_label = ParagraphStyle('NISTCLbl', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#64748b'))
    card_val = ParagraphStyle('NISTCVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#0f172a'))
    
    score_global = datos_nist.get('score_global', 0.0)
    score_color = '#16a34a' if score_global >= 80 else ('#2563eb' if score_global >= 60 else ('#f59e0b' if score_global >= 40 else '#dc2626'))
    
    score_style = ParagraphStyle('NISTScoreVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=18, textColor=colors.HexColor(score_color))
    
    # 1. Resumen de Madurez Global
    tier_txt = datos_nist.get('tier', 'Tier 1: Parcial')
    tier_desc = datos_nist.get('tier_desc', '')
    
    summary_data = [
        [
            [Paragraph("MADUREZ GLOBAL NIST CSF", card_label), Spacer(1, 2), Paragraph(f"{score_global}%", score_style)],
            [Paragraph("NIVEL DE TIER ALCANZADO", card_label), Spacer(1, 2), Paragraph(f"<b>{tier_txt}</b>", card_val)],
            [Paragraph("ACTIVOS AUDITADOS", card_label), Spacer(1, 2), Paragraph(f"<b>{datos_nist.get('total_equipos', 0)} Equipos</b>", card_val)]
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[180, 220, 140])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#e2e8f0')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 4))
    
    desc_style = ParagraphStyle('NISTDesc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor('#475569'))
    story.append(Paragraph(f"<b>Diagnóstico de Madurez:</b> {tier_desc}", desc_style))
    story.append(Spacer(1, 10))
    
    # 2. Desglose por las 6 Funciones de NIST CSF 2.0
    story.append(Paragraph("Evaluación por Funciones del Marco NIST CSF 2.0", sec_title))
    
    funciones = datos_nist.get('funciones', [])
    func_header = ParagraphStyle('FH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
    cell_txt = ParagraphStyle('FC', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('FCB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#0f172a'))
    
    func_table_data = [[
        Paragraph("Función NIST", func_header),
        Paragraph("Código", func_header),
        Paragraph("Alcance y Controles Evaluados", func_header),
        Paragraph("Cumplimiento", func_header),
        Paragraph("Estado", func_header)
    ]]
    
    for f in funciones:
        sc = f.get('score', 0.0)
        st_color = '#16a34a' if sc >= 75 else ('#2563eb' if sc >= 50 else ('#f59e0b' if sc >= 30 else '#dc2626'))
        st_label = 'Optimizado' if sc >= 75 else ('Gestionado' if sc >= 50 else ('En Desarrollo' if sc >= 30 else 'Inicial'))
        
        func_table_data.append([
            Paragraph(f"<b>{f.get('nombre', '')}</b>", cell_bold),
            Paragraph(f"<b>{f.get('codigo', '')}</b>", cell_bold),
            Paragraph(f.get('descripcion', ''), cell_txt),
            Paragraph(f"<b>{sc}%</b>", ParagraphStyle('Sc', parent=cell_bold, textColor=colors.HexColor(st_color))),
            Paragraph(f"<font color='{st_color}'><b>● {st_label}</b></font>", cell_txt)
        ])
        
    func_table = Table(func_table_data, colWidths=[130, 45, 235, 65, 65])
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(func_table)
    story.append(Spacer(1, 10))
    
    # 3. Recomendaciones y Plan de Acción de Auditoría
    story.append(Paragraph("Plan de Acción y Recomendaciones Prioritarias", sec_title))
    
    recoms = datos_nist.get('recomendaciones', [])
    recom_data = [[
        Paragraph("Prioridad", func_header),
        Paragraph("Función", func_header),
        Paragraph("Medida de Mitigación / Mejora Recomendada", func_header)
    ]]
    
    for r in recoms:
        prio = r.get('prioridad', 'Media')
        p_color = '#dc2626' if prio == 'Alta' else ('#f59e0b' if prio == 'Media' else '#16a34a')
        
        recom_data.append([
            Paragraph(f"<font color='{p_color}'><b>● {prio}</b></font>", cell_bold),
            Paragraph(f"<b>{r.get('funcion', '')}</b>", cell_bold),
            Paragraph(f"<b>{r.get('titulo', '')}:</b> {r.get('detalle', '')}", cell_txt)
        ])
        
    recom_table = Table(recom_data, colWidths=[65, 85, 390])
    recom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(recom_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

