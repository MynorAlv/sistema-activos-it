"""
Módulo de Evaluación de Ciberseguridad basada en NIST Cybersecurity Framework (CSF 2.0).
Evalúa la postura de seguridad, madurez y cumplimiento a partir de los Activos IT y Vulnerabilidades registradas.
"""

def evaluar_postura_nist(equipos, vulnerabilidades):
    """
    Calcula la puntuación y madurez según las 6 funciones de NIST CSF 2.0:
    - GOVERN (GV): Gobernanza y asignación de responsabilidades
    - IDENTIFY (ID): Gestión y completitud del inventario de activos
    - PROTECT (PR): Clasificación de seguridad y protección preventiva
    - DETECT (DE): Detección continua de vulnerabilidades y CVEs
    - RESPOND (RS): Planificación de remediación y asignación de responsables
    - RECOVER (RC): Tasa de mitigación, riesgo residual y cierre de incidentes
    """
    total_equipos = len(equipos)
    total_vulns = len(vulnerabilidades)
    
    # -------------------------------------------------------------
    # 1. GOBERNAR (GOVERN - GV)
    # -------------------------------------------------------------
    # Criterios: Equipos con área responsable asignada, propietarios definidos y trazabilidad de cambios
    equipos_con_area = sum(1 for e in equipos if e.area_responsable)
    equipos_con_propietario = sum(1 for e in equipos if e.propietario)
    vulns_con_historial = sum(1 for v in vulnerabilidades if v.historial_cambios and len(v.historial_cambios) > 0)
    
    score_gv = 0.0
    if total_equipos > 0:
        p_area = (equipos_con_area / total_equipos) * 40
        p_prop = (equipos_con_propietario / total_equipos) * 30
        p_hist = ((vulns_con_historial / total_vulns) * 30) if total_vulns > 0 else 20
        score_gv = min(100.0, p_area + p_prop + p_hist)
    else:
        score_gv = 10.0

    # -------------------------------------------------------------
    # 2. IDENTIFICAR (IDENTIFY - ID)
    # -------------------------------------------------------------
    # Criterios: Completitud del inventario (SO, IP, Hostname, Ubicación, Ambiente, Fecha de revisión)
    equipos_con_so = sum(1 for e in equipos if e.sistema_operativo)
    equipos_con_ip_host = sum(1 for e in equipos if e.ip or e.hostname)
    equipos_con_ubicacion = sum(1 for e in equipos if e.ubicacion)
    equipos_con_ambiente = sum(1 for e in equipos if e.ambiente)
    equipos_con_revision = sum(1 for e in equipos if e.fecha_revision)
    
    score_id = 0.0
    if total_equipos > 0:
        score_id = (
            (equipos_con_so / total_equipos) * 25 +
            (equipos_con_ip_host / total_equipos) * 25 +
            (equipos_con_ubicacion / total_equipos) * 15 +
            (equipos_con_ambiente / total_equipos) * 15 +
            (equipos_con_revision / total_equipos) * 20
        )
    else:
        score_id = 5.0

    # -------------------------------------------------------------
    # 3. PROTEGER (PROTECT - PR)
    # -------------------------------------------------------------
    # Criterios: Activos con tipo de información clasificada, dependencias identificadas y control de criticidad
    equipos_con_tipo_info = sum(1 for e in equipos if e.tipo_informacion)
    equipos_con_dependencias = sum(1 for e in equipos if e.dependencias)
    equipos_evaluados = sum(1 for e in equipos if e.get_criticidad_display() != 'N/A')
    
    score_pr = 0.0
    if total_equipos > 0:
        score_pr = (
            (equipos_con_tipo_info / total_equipos) * 35 +
            (equipos_con_dependencias / total_equipos) * 30 +
            (equipos_evaluados / total_equipos) * 35
        )
    else:
        score_pr = 5.0

    # -------------------------------------------------------------
    # 4. DETECTAR (DETECT - DE)
    # -------------------------------------------------------------
    # Criterios: Activos con vulnerabilidades auditadas (CVEs), criticidad identificada y descripción
    equipos_con_vulns = sum(1 for e in equipos if len(e.vulnerabilidades) > 0)
    vulns_con_cve = sum(1 for v in vulnerabilidades if v.codigo)
    vulns_con_impacto = sum(1 for v in vulnerabilidades if v.impacto)
    
    score_de = 0.0
    if total_equipos > 0 and total_vulns > 0:
        p_cobertura = (equipos_con_vulns / total_equipos) * 40
        p_cve = (vulns_con_cve / total_vulns) * 30
        p_impacto = (vulns_con_impacto / total_vulns) * 30
        score_de = min(100.0, p_cobertura + p_cve + p_impacto)
    elif total_equipos > 0 and total_vulns == 0:
        score_de = 30.0 # Requiere realizar escaneos
    else:
        score_de = 5.0

    # -------------------------------------------------------------
    # 5. RESPONDER (RESPOND - RS)
    # -------------------------------------------------------------
    # Criterios: Vulnerabilidades con plan de remediación, responsable asignado y fecha objetivo
    vulns_con_plan = sum(1 for v in vulnerabilidades if v.plan_remediacion and len(v.plan_remediacion) > 5)
    vulns_con_responsable = sum(1 for v in vulnerabilidades if v.responsable)
    vulns_con_fecha = sum(1 for v in vulnerabilidades if v.fecha_objetivo)
    vulns_en_proceso = sum(1 for v in vulnerabilidades if v.estado_remediacion == 'En proceso')
    
    score_rs = 0.0
    if total_vulns > 0:
        score_rs = (
            (vulns_con_plan / total_vulns) * 30 +
            (vulns_con_responsable / total_vulns) * 30 +
            (vulns_con_fecha / total_vulns) * 20 +
            (vulns_en_proceso / total_vulns) * 20
        )
    else:
        score_rs = 50.0 if total_equipos > 0 else 10.0

    # -------------------------------------------------------------
    # 6. RECUPERAR (RECOVER - RC)
    # -------------------------------------------------------------
    # Criterios: Tasa de remediación completada, gestión de riesgo residual y observaciones de cierre
    vulns_completadas = sum(1 for v in vulnerabilidades if v.completada or v.estado_remediacion == 'Completada')
    vulns_con_riesgo_res = sum(1 for v in vulnerabilidades if v.riesgo_residual)
    vulns_con_evidencia = sum(1 for v in vulnerabilidades if v.evidencia)
    
    score_rc = 0.0
    if total_vulns > 0:
        score_rc = (
            (vulns_completadas / total_vulns) * 50 +
            (vulns_con_riesgo_res / total_vulns) * 25 +
            (vulns_con_evidencia / total_vulns) * 25
        )
    else:
        score_rc = 50.0 if total_equipos > 0 else 10.0

    # Puntuación global ponderada NIST CSF
    score_global = round((score_gv + score_id + score_pr + score_de + score_rs + score_rc) / 6.0, 1)
    
    # Nivel de Madurez (Tiers 1 a 4)
    if score_global >= 80.0:
        tier = "Tier 4: Adaptable (Avanzado)"
        tier_nivel = 4
        tier_desc = "La organización cuenta con procesos continuos de gestión de ciberseguridad, automatización asistida por IA y respuesta preventiva."
    elif score_global >= 60.0:
        tier = "Tier 3: Repetible (Formalizado)"
        tier_nivel = 3
        tier_desc = "Las prácticas de seguridad de TI y planes de remediación están formalmente documentados, asignados y supervisados periódicamente."
    elif score_global >= 40.0:
        tier = "Tier 2: Informado por Riesgo"
        tier_nivel = 2
        tier_desc = "Existe conciencia de los riesgos y activos clave, pero la ejecución de controles y remediaciones es parcialmente reactiva."
    else:
        tier = "Tier 1: Parcial (Inicial)"
        tier_nivel = 1
        tier_desc = "Las prácticas de inventario y seguridad son reactivas e informales; se requiere estandarizar el registro de activos y remediación."

    # Recomendaciones automáticas según los puntos de mejora
    recomendaciones = []
    
    if score_id < 70:
        recomendaciones.append({
            'funcion': 'IDENTIFICAR',
            'icono': 'fas fa-search',
            'prioridad': 'Alta',
            'titulo': 'Completar datos de infraestructura en el inventario',
            'detalle': 'Asegurar que todos los activos tengan documentada su IP, Sistema Operativo con versión exacta y fecha de última revisión.'
        })
        
    if score_de < 70:
        recomendaciones.append({
            'funcion': 'DETECTAR',
            'icono': 'fas fa-shield-alt',
            'prioridad': 'Alta',
            'titulo': 'Auditar vulnerabilidades en activos desprotegidos',
            'detalle': 'Ejecutar la consulta asistida por IA para identificar CVEs y riesgos en activos que aún no tienen hallazgos documentados.'
        })

    if score_rs < 70:
        recomendaciones.append({
            'funcion': 'RESPONDER',
            'icono': 'fas fa-tools',
            'prioridad': 'Media',
            'titulo': 'Formalizar planes y fechas de remediación',
            'detalle': 'Asignar responsables nominales y fechas objetivo a todas las vulnerabilidades en estado pendiente.'
        })
        
    if score_rc < 60:
        recomendaciones.append({
            'funcion': 'RECUPERAR',
            'icono': 'fas fa-check-circle',
            'prioridad': 'Media',
            'titulo': 'Documentar evidencia y riesgo residual',
            'detalle': 'Adjuntar evidencia verificable al cerrar vulnerabilidades y clasificar el riesgo residual resultante.'
        })

    if not recomendaciones:
        recomendaciones.append({
            'funcion': 'GOBERNAR',
            'icono': 'fas fa-award',
            'prioridad': 'Baja',
            'titulo': 'Mantener ciclo de mejora continua',
            'detalle': 'Excelente nivel de cumplimiento NIST CSF. Mantener revisiones periódicas y trazabilidad activa.'
        })

    funciones_detalle = [
        {
            'codigo': 'GV',
            'nombre': 'Gobernar (Govern)',
            'score': round(score_gv, 1),
            'icono': 'fas fa-landmark',
            'color': '#2563eb',
            'descripcion': 'Políticas, asignación de áreas y trazabilidad de cambios organizacionales.'
        },
        {
            'codigo': 'ID',
            'nombre': 'Identificar (Identify)',
            'score': round(score_id, 1),
            'icono': 'fas fa-fingerprint',
            'color': '#2563eb',
            'descripcion': 'Gestión de inventario de activos, direccionamiento de red y criticidad.'
        },
        {
            'codigo': 'PR',
            'nombre': 'Proteger (Protect)',
            'score': round(score_pr, 1),
            'icono': 'fas fa-shield-alt',
            'color': '#2563eb',
            'descripcion': 'Clasificación de datos, control de dependencias y salvaguardas de seguridad.'
        },
        {
            'codigo': 'DE',
            'nombre': 'Detectar (Detect)',
            'score': round(score_de, 1),
            'icono': 'fas fa-binoculars',
            'color': '#2563eb',
            'descripcion': 'Identificación continua de CVEs, análisis asistido por IA y evaluación de impacto.'
        },
        {
            'codigo': 'RS',
            'nombre': 'Responder (Respond)',
            'score': round(score_rs, 1),
            'icono': 'fas fa-tasks',
            'color': '#2563eb',
            'descripcion': 'Asignación de responsables, fechas límite y planes de mitigación.'
        },
        {
            'codigo': 'RC',
            'nombre': 'Recuperar (Recover)',
            'score': round(score_rc, 1),
            'icono': 'fas fa-rotate-left',
            'color': '#2563eb',
            'descripcion': 'Efectividad en resolución, verificación de mitigaciones y riesgo residual.'
        }
    ]

    return {
        'score_global': score_global,
        'tier': tier,
        'tier_nivel': tier_nivel,
        'tier_desc': tier_desc,
        'total_equipos': total_equipos,
        'total_vulnerabilidades': total_vulns,
        'funciones': funciones_detalle,
        'recomendaciones': recomendaciones,
        'scores_por_codigo': {
            'GV': round(score_gv, 1),
            'ID': round(score_id, 1),
            'PR': round(score_pr, 1),
            'DE': round(score_de, 1),
            'RS': round(score_rs, 1),
            'RC': round(score_rc, 1)
        }
    }
