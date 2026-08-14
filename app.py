from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case, func
from datetime import datetime
from groq import Groq
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuracion de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/activos_it'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu-secret-key-aqui'

db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    nombre1 = db.Column(db.String(50), nullable=False)
    nombre2 = db.Column(db.String(50), nullable=True)
    apellido1 = db.Column(db.String(50), nullable=False)
    apellido2 = db.Column(db.String(50), nullable=True)
    rol = db.Column(db.String(50), nullable=False)
    puesto = db.Column(db.String(100), nullable=True)
    contrasena = db.Column(db.String(255), nullable=False)  # Para futuro hash
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario': self.usuario,
            'nombre1': self.nombre1,
            'nombre2': self.nombre2,
            'apellido1': self.apellido1,
            'apellido2': self.apellido2,
            'rol': self.rol,
            'puesto': self.puesto
        }
    
    def get_nombre_completo(self):
        nombre = f"{self.nombre1}"
        if self.nombre2:
            nombre += f" {self.nombre2}"
        nombre += f" {self.apellido1}"
        if self.apellido2:
            nombre += f" {self.apellido2}"
        return nombre

# Modelos de base de datos
class Equipo(db.Model):
    __tablename__ = 'equipos'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    caracteristica = db.Column(db.String(200), nullable=False)
    propietario = db.Column(db.String(100), nullable=True)
    ubicacion = db.Column(db.String(150), nullable=True)
    area_responsable = db.Column(db.String(150), nullable=True)
    tipo_informacion = db.Column(db.String(150), nullable=True)
    dependencias = db.Column(db.Text, nullable=True)
    sistema_operativo = db.Column(db.String(100), nullable=True)
    version = db.Column(db.String(100), nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    hostname = db.Column(db.String(100), nullable=True)
    ambiente = db.Column(db.String(50), nullable=True)
    fecha_revision = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    vulnerabilidades = db.relationship('Vulnerabilidad', backref='equipo', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'caracteristica': self.caracteristica,
            'propietario': self.propietario,
            'ubicacion': self.ubicacion,
            'area_responsable': self.area_responsable,
            'tipo_informacion': self.tipo_informacion,
            'dependencias': self.dependencias,
            'sistema_operativo': self.sistema_operativo,
            'version': self.version,
            'ip': self.ip,
            'hostname': self.hostname,
            'ambiente': self.ambiente,
            'fecha_revision': self.fecha_revision.strftime('%Y-%m-%d') if self.fecha_revision else None,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_criticidad_maxima(self):
        criticidad_pesos = {'Alta': 3, 'Media': 2, 'Baja': 1}
        max_peso = 0
        criticidad_max = None
        
        for vuln in self.vulnerabilidades:
            if vuln.criticidad and vuln.criticidad in criticidad_pesos:
                peso = criticidad_pesos[vuln.criticidad]
                if peso > max_peso:
                    max_peso = peso
                    criticidad_max = vuln.criticidad
        
        return criticidad_max
    
    def get_criticidad_display(self):
        criticidad = self.get_criticidad_maxima()
        return criticidad or 'N/A'

# Modelo Vulnerabilidad (SIN campo comentarios)
class Vulnerabilidad(db.Model):
    __tablename__ = 'vulnerabilidades'
    
    id = db.Column(db.Integer, primary_key=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    completada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_completada = db.Column(db.DateTime, nullable=True)
    
    codigo = db.Column(db.String(50), nullable=True)
    criticidad = db.Column(db.String(20), nullable=True)
    impacto = db.Column(db.Text, nullable=True)
    plan_remediacion = db.Column(db.Text, nullable=True)
    tiempo_estimado = db.Column(db.String(50), nullable=True)
    responsable = db.Column(db.String(100), nullable=True)
    fecha_objetivo = db.Column(db.DateTime, nullable=True)
    prioridad_remediacion = db.Column(db.String(50), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    evidencia = db.Column(db.String(250), nullable=True)
    riesgo_residual = db.Column(db.String(50), nullable=True)
    estado_remediacion = db.Column(db.String(50), nullable=True, default='Pendiente')
    historial_cambios = db.Column(db.JSON, nullable=True)
    datos_completos = db.Column(db.JSON, nullable=True)
    
    def get_porcentaje_avance(self):
        """
        Calcula el porcentaje de avance automáticamente
        """
        return calcular_porcentaje_avance_dinamico(self)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_equipo': self.id_equipo,
            'descripcion': self.descripcion,
            'codigo': self.codigo,
            'criticidad': self.criticidad,
            'impacto': self.impacto,
            'plan_remediacion': self.plan_remediacion,
            'tiempo_estimado': self.tiempo_estimado,
            'responsable': self.responsable,
            'fecha_objetivo': self.fecha_objetivo.strftime('%Y-%m-%d') if self.fecha_objetivo else None,
            'prioridad_remediacion': self.prioridad_remediacion,
            'estado_remediacion': self.estado_remediacion,
            'observaciones': self.observaciones,
            'evidencia': self.evidencia,
            'porcentaje_avance': self.get_porcentaje_avance(),
            'riesgo_residual': self.riesgo_residual,
            'historial_cambios': self.historial_cambios,
            'datos_completos': self.datos_completos,
            'completada': self.completada,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_completada': self.fecha_completada.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_completada else None,
            'equipo_info': {
                'id': self.equipo.id,
                'tipo': self.equipo.tipo,
                'caracteristica': self.equipo.caracteristica
            } if self.equipo else None
        }

def calcular_porcentaje_avance_dinamico(vulnerabilidad):
    """
    Calcula el porcentaje de avance de forma dinámica combinando múltiples factores
    
    Factores considerados:
    - Responsable asignado: 20%
    - Fecha objetivo definida: 10% + progreso temporal hasta 20%
    - Plan de remediación: 20%
    - Observaciones: 10%
    - Evidencia adjunta: 20%
    - Prioridad Alta: +5% (bonificación)
    
    Máximo: 95% (nunca 100% hasta que se complete)
    """
    # Si está completada, 100%
    if vulnerabilidad.estado_remediacion == 'Completada':
        return 100
    
    # Si está pendiente, 0%
    if vulnerabilidad.estado_remediacion == 'Pendiente':
        return 0
    
    # Si está en proceso, calcular progreso
    if vulnerabilidad.estado_remediacion == 'En proceso':
        avance = 0
        
        # 1. Responsable asignado (20%)
        if vulnerabilidad.responsable:
            avance += 20
        
        # 2. Fecha objetivo definida (10%)
        if vulnerabilidad.fecha_objetivo:
            avance += 10
            
            # 2a. Progreso temporal (hasta 20% adicional)
            hoy = datetime.utcnow().date()
            fecha_creacion = vulnerabilidad.fecha_creacion.date()
            fecha_objetivo = vulnerabilidad.fecha_objetivo.date()
            
            if fecha_objetivo > fecha_creacion:
                dias_totales = (fecha_objetivo - fecha_creacion).days
                dias_transcurridos = (hoy - fecha_creacion).days
                if dias_totales > 0:
                    progreso_temporal = min((dias_transcurridos / dias_totales) * 20, 20)
                    avance += progreso_temporal
        
        # 3. Plan de remediación (20%)
        if vulnerabilidad.plan_remediacion and len(vulnerabilidad.plan_remediacion) > 10:
            avance += 20
        elif vulnerabilidad.plan_remediacion:
            avance += 10
        
        # 4. Observaciones (10%)
        if vulnerabilidad.observaciones and len(vulnerabilidad.observaciones) > 10:
            avance += 10
        elif vulnerabilidad.observaciones:
            avance += 5
        
        # 5. Evidencia (20%)
        if vulnerabilidad.evidencia:
            avance += 20
        
        # 6. Prioridad (bonificación si es Alta)
        if vulnerabilidad.prioridad_remediacion == 'Alta':
            avance += 5
        
        # Limitar a 95% (nunca 100% hasta que se complete)
        avance = min(avance, 95)
        
        return avance
    
    return 0

# Ruta principal - Lista de equipos
@app.route('/')
def index():
    equipos = Equipo.query.order_by(Equipo.fecha_creacion.desc()).all()
    return render_template('index.html', equipos=equipos)

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

# API: Obtener todos los equipos
@app.route('/api/equipos', methods=['GET'])
def get_equipos():
    equipos = Equipo.query.order_by(Equipo.fecha_creacion.desc()).all()
    equipos_data = []
    for e in equipos:
        data = e.to_dict()
        data['criticidad'] = e.get_criticidad_display()
        equipos_data.append(data)
    return jsonify(equipos_data)

# API: Obtener un equipo especifico
@app.route('/api/equipos/<int:id>', methods=['GET'])
def get_equipo(id):
    equipo = Equipo.query.get_or_404(id)
    data = equipo.to_dict()
    data['criticidad'] = equipo.get_criticidad_display()
    return jsonify(data)

# API: Obtener todos los usuarios
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.order_by(Usuario.apellido1, Usuario.nombre1).all()
    return jsonify([u.to_dict() for u in usuarios])

# API: Obtener usuarios para lista de responsables (nombre completo)
@app.route('/api/usuarios/responsables', methods=['GET'])
def get_responsables():
    usuarios = Usuario.query.order_by(Usuario.apellido1, Usuario.nombre1).all()
    return jsonify([{
        'id': u.id,
        'nombre_completo': u.get_nombre_completo(),
        'usuario': u.usuario
    } for u in usuarios])

# API: Lista de vulnerabilidades con filtros y paginación
@app.route('/api/vulnerabilidades', methods=['GET'])
def list_vulnerabilidades():
    query = Vulnerabilidad.query
    criticidad = request.args.get('criticidad')
    estado_remediacion = request.args.get('estado_remediacion')
    equipo_id = request.args.get('equipo_id', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    if criticidad:
        query = query.filter_by(criticidad=criticidad)
    if estado_remediacion:
        query = query.filter_by(estado_remediacion=estado_remediacion)
    if equipo_id:
        query = query.filter_by(id_equipo=equipo_id)
    if search:
        query = query.filter(
            Vulnerabilidad.descripcion.ilike(f'%{search}%') | 
            Vulnerabilidad.codigo.ilike(f'%{search}%') | 
            Vulnerabilidad.impacto.ilike(f'%{search}%')
        )

    paginated = query.order_by(Vulnerabilidad.fecha_creacion.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [v.to_dict() for v in paginated.items],
        'page': paginated.page,
        'per_page': paginated.per_page,
        'total': paginated.total,
        'pages': paginated.pages
    })

# API: Obtener una vulnerabilidad específica por ID
@app.route('/api/vulnerabilidades/<int:id>', methods=['GET'])
def get_vulnerabilidad(id):
    vulnerabilidad = Vulnerabilidad.query.get_or_404(id)
    return jsonify(vulnerabilidad.to_dict())

# API: Crear equipo
@app.route('/api/equipos', methods=['POST'])
def create_equipo():
    data = request.get_json()
    tipo = data.get('tipo', '').strip()
    caracteristica = data.get('caracteristica', '').strip()
    propietario = data.get('propietario', '').strip() or None
    ubicacion = data.get('ubicacion', '').strip() or None
    area_responsable = data.get('area_responsable', '').strip() or None
    tipo_informacion = data.get('tipo_informacion', '').strip() or None
    dependencias = data.get('dependencias', '').strip() or None
    sistema_operativo = data.get('sistema_operativo', '').strip() or None
    version = data.get('version', '').strip() or None
    ip = data.get('ip', '').strip() or None
    hostname = data.get('hostname', '').strip() or None
    ambiente = data.get('ambiente', '').strip() or None
    fecha_revision = data.get('fecha_revision')
    
    if not tipo or not caracteristica:
        return jsonify({'error': 'Tipo y caracteristica son requeridos'}), 400
    
    fecha_revision_obj = None
    if fecha_revision:
        try:
            fecha_revision_obj = datetime.fromisoformat(fecha_revision)
        except ValueError:
            pass
    
    nuevo_equipo = Equipo(
        tipo=tipo,
        caracteristica=caracteristica,
        propietario=propietario,
        ubicacion=ubicacion,
        area_responsable=area_responsable,
        tipo_informacion=tipo_informacion,
        dependencias=dependencias,
        sistema_operativo=sistema_operativo,
        version=version,
        ip=ip,
        hostname=hostname,
        ambiente=ambiente,
        fecha_revision=fecha_revision_obj
    )
    db.session.add(nuevo_equipo)
    db.session.commit()
    
    return jsonify(nuevo_equipo.to_dict()), 201

# API: Actualizar equipo
@app.route('/api/equipos/<int:id>', methods=['PUT'])
def update_equipo(id):
    equipo = Equipo.query.get_or_404(id)
    data = request.get_json() or {}

    equipo.tipo = data.get('tipo', equipo.tipo)
    equipo.caracteristica = data.get('caracteristica', equipo.caracteristica)
    equipo.propietario = data.get('propietario', equipo.propietario)
    equipo.ubicacion = data.get('ubicacion', equipo.ubicacion)
    equipo.area_responsable = data.get('area_responsable', equipo.area_responsable)
    equipo.tipo_informacion = data.get('tipo_informacion', equipo.tipo_informacion)
    equipo.dependencias = data.get('dependencias', equipo.dependencias)
    equipo.sistema_operativo = data.get('sistema_operativo', equipo.sistema_operativo)
    equipo.version = data.get('version', equipo.version)
    equipo.ip = data.get('ip', equipo.ip)
    equipo.hostname = data.get('hostname', equipo.hostname)
    equipo.ambiente = data.get('ambiente', equipo.ambiente)

    fecha_revision = data.get('fecha_revision')
    if fecha_revision:
        try:
            equipo.fecha_revision = datetime.fromisoformat(fecha_revision)
        except ValueError:
            pass

    db.session.commit()
    return jsonify(equipo.to_dict()), 200

# API: Eliminar equipo
@app.route('/api/equipos/<int:id>', methods=['DELETE'])
def delete_equipo(id):
    equipo = Equipo.query.get_or_404(id)
    db.session.delete(equipo)
    db.session.commit()
    return jsonify({'message': 'Equipo eliminado'}), 200

# API: Obtener vulnerabilidades de un equipo
@app.route('/api/equipos/<int:id>/vulnerabilidades', methods=['GET'])
def get_vulnerabilidades(id):
    equipo = Equipo.query.get_or_404(id)
    return jsonify([v.to_dict() for v in equipo.vulnerabilidades])

# API: Dashboard de riesgos y activos
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    equipos = Equipo.query.all()
    total_equipos = len(equipos)
    
    # Pesos de criticidad
    criticidad_pesos = {'Alta': 3, 'Media': 2, 'Baja': 1}
    
    # Variables para el cálculo del riesgo
    total_score = 0
    max_possible_score = 0
    
    # Contadores de vulnerabilidades por criticidad (SOLO activas, no completadas)
    altos = 0
    medios = 0
    bajos = 0
    
    # Procesar cada equipo
    for equipo in equipos:
        # Filtrar vulnerabilidades NO completadas (activas)
        vulnerabilidades_activas = [v for v in equipo.vulnerabilidades if v.estado_remediacion != 'Completada' and not v.completada]
        
        # Si el equipo tiene vulnerabilidades activas
        if vulnerabilidades_activas:
            equipo_score = 0
            
            # Contar cada vulnerabilidad activa por su criticidad
            for vuln in vulnerabilidades_activas:
                if vuln.criticidad and vuln.criticidad in criticidad_pesos:
                    peso = criticidad_pesos[vuln.criticidad]
                    equipo_score += peso
                    
                    # Contar por criticidad
                    if vuln.criticidad == 'Alta':
                        altos += 1
                    elif vuln.criticidad == 'Media':
                        medios += 1
                    elif vuln.criticidad == 'Baja':
                        bajos += 1
            
            # El máximo posible para este equipo es: número de vulnerabilidades activas × 3
            equipo_max_possible = len(vulnerabilidades_activas) * 3
            
            # Acumular
            total_score += equipo_score
            max_possible_score += equipo_max_possible
    
    # Calcular el índice de riesgo
    if max_possible_score > 0:
        risk_index = round((total_score / max_possible_score) * 100, 2)
    else:
        risk_index = 0.0
    
    # Top activos más expuestos
    top_assets = db.session.query(
        Equipo.id,
        Equipo.tipo,
        Equipo.caracteristica,
        func.count(Vulnerabilidad.id).label('total_vulnerabilidades'),
        func.sum(case((Vulnerabilidad.completada == False, 1), else_=0)).label('pendientes'),
        func.sum(case((Vulnerabilidad.completada == True, 1), else_=0)).label('completadas')
    ).outerjoin(Vulnerabilidad).group_by(Equipo.id).order_by(func.count(Vulnerabilidad.id).desc()).limit(10).all()

    top_assets_data = [
        {
            'id': item.id,
            'tipo': item.tipo,
            'caracteristica': item.caracteristica,
            'criticidad': Equipo.query.get(item.id).get_criticidad_display(),
            'total_vulnerabilidades': int(item.total_vulnerabilidades or 0),
            'pendientes': int(item.pendientes or 0),
            'completadas': int(item.completadas or 0)
        }
        for item in top_assets
    ]

    # Vulnerabilidades pendientes y completadas (todas)
    pendientes = Vulnerabilidad.query.filter_by(completada=False).count()
    completadas = Vulnerabilidad.query.filter_by(completada=True).count()
    total_vulnerabilidades = pendientes + completadas
    porcentaje_corregidas = round((completadas / total_vulnerabilidades) * 100, 2) if total_vulnerabilidades else 0.0

    return jsonify({
        'total_equipos': total_equipos,
        'criticos': altos,
        'medios': medios,
        'bajos': bajos,
        'risk_index': risk_index,
        'total_vulnerabilidades': total_vulnerabilidades,
        'pendientes': pendientes,
        'completadas': completadas,
        'porcentaje_corregidas': porcentaje_corregidas,
        'top_activos': top_assets_data,
        'total_score': total_score,
        'max_possible_score': max_possible_score
    })

# API: Obtener vulnerabilidades pendientes con información de equipo
@app.route('/api/vulnerabilidades/pendientes', methods=['GET'])
def get_vulnerabilidades_pendientes():
    vulnerabilidades = Vulnerabilidad.query.filter_by(completada=False).order_by(Vulnerabilidad.fecha_creacion.desc()).all()
    return jsonify([v.to_dict() for v in vulnerabilidades])

# API: Obtener vulnerabilidades completadas
@app.route('/api/vulnerabilidades/completadas', methods=['GET'])
def get_vulnerabilidades_completadas():
    vulnerabilidades = Vulnerabilidad.query.filter_by(completada=True).order_by(Vulnerabilidad.fecha_completada.desc()).all()
    return jsonify([v.to_dict() for v in vulnerabilidades])

# API: Actualizar estado de remediacion de una vulnerabilidad
@app.route('/api/vulnerabilidades/<int:id>/remediacion', methods=['PUT'])
def actualizar_remediacion(id):
    vulnerabilidad = Vulnerabilidad.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Actualizar campos
    if 'estado_remediacion' in data:
        vulnerabilidad.estado_remediacion = data['estado_remediacion']
        if data['estado_remediacion'] == 'Completada':
            vulnerabilidad.completada = True
            vulnerabilidad.fecha_completada = datetime.utcnow()
        elif data['estado_remediacion'] in ['Pendiente', 'En proceso']:
            vulnerabilidad.completada = False
            vulnerabilidad.fecha_completada = None
    
    if 'responsable' in data:
        vulnerabilidad.responsable = data['responsable']
    if 'fecha_objetivo' in data and data['fecha_objetivo']:
        try:
            vulnerabilidad.fecha_objetivo = datetime.fromisoformat(data['fecha_objetivo'])
        except ValueError:
            pass
    if 'prioridad_remediacion' in data:
        vulnerabilidad.prioridad_remediacion = data['prioridad_remediacion']
    if 'observaciones' in data:
        vulnerabilidad.observaciones = data['observaciones']
    if 'evidencia' in data:
        vulnerabilidad.evidencia = data['evidencia']
    if 'riesgo_residual' in data:
        vulnerabilidad.riesgo_residual = data['riesgo_residual']
    
    # Agregar al historial de cambios
    historial = vulnerabilidad.historial_cambios or []
    if not isinstance(historial, list):
        historial = []
    
    historial.append({
        'fecha': datetime.utcnow().isoformat(),
        'usuario': data.get('usuario', 'Sistema'),
        'accion': 'Actualización de remediación',
        'datos': {k: v for k, v in data.items() if k not in ['usuario']}
    })
    vulnerabilidad.historial_cambios = historial
    
    db.session.commit()
    
    # Devolver la vulnerabilidad con el avance calculado automáticamente
    return jsonify(vulnerabilidad.to_dict()), 200

# API: Marcar vulnerabilidad como completada
@app.route('/api/vulnerabilidades/<int:id>/completar', methods=['POST'])
def completar_vulnerabilidad(id):
    vulnerabilidad = Vulnerabilidad.query.get_or_404(id)
    vulnerabilidad.completada = True
    vulnerabilidad.fecha_completada = datetime.utcnow()
    vulnerabilidad.estado_remediacion = 'Completada'
    db.session.commit()
    return jsonify(vulnerabilidad.to_dict()), 200

# API: Desmarcar vulnerabilidad
@app.route('/api/vulnerabilidades/<int:id>/desmarcar', methods=['POST'])
def desmarcar_vulnerabilidad(id):
    vulnerabilidad = Vulnerabilidad.query.get_or_404(id)
    vulnerabilidad.completada = False
    vulnerabilidad.fecha_completada = None
    vulnerabilidad.estado_remediacion = 'Pendiente'
    db.session.commit()
    return jsonify(vulnerabilidad.to_dict()), 200

# API: Eliminar vulnerabilidad
@app.route('/api/vulnerabilidades/<int:id>', methods=['DELETE'])
def delete_vulnerabilidad(id):
    vulnerabilidad = Vulnerabilidad.query.get_or_404(id)
    db.session.delete(vulnerabilidad)
    db.session.commit()
    return jsonify({'message': 'Vulnerabilidad eliminada'}), 200

# API: Agregar vulnerabilidad manual
@app.route('/api/vulnerabilidades', methods=['POST'])
def add_vulnerabilidad():
    data = request.get_json()
    equipo_id = data.get('equipo_id')
    descripcion = data.get('descripcion', '').strip()
    codigo = data.get('codigo', '').strip() or None
    criticidad = data.get('criticidad', '').strip() or None
    impacto = data.get('impacto', '').strip() or None
    plan_remediacion = data.get('plan_remediacion', '').strip() or None
    tiempo_estimado = data.get('tiempo_estimado', '').strip() or None
    responsable = data.get('responsable', '').strip() or None
    fecha_objetivo = data.get('fecha_objetivo')
    prioridad_remediacion = data.get('prioridad_remediacion', '').strip() or None
    estado_remediacion = data.get('estado_remediacion', '').strip() or 'Pendiente'
    observaciones = data.get('observaciones', '').strip() or None
    evidencia = data.get('evidencia', '').strip() or None
    riesgo_residual = data.get('riesgo_residual', '').strip() or None
    datos_completos = data.get('datos_completos')
    
    if not equipo_id or not descripcion:
        return jsonify({'error': 'Equipo ID y descripcion son requeridos'}), 400
    
    equipo = Equipo.query.get_or_404(equipo_id)
    fecha_objetivo_obj = None
    if fecha_objetivo:
        try:
            fecha_objetivo_obj = datetime.fromisoformat(fecha_objetivo)
        except ValueError:
            pass

    nueva_vuln = Vulnerabilidad(
        id_equipo=equipo_id,
        descripcion=descripcion,
        codigo=codigo,
        criticidad=criticidad,
        impacto=impacto,
        plan_remediacion=plan_remediacion,
        tiempo_estimado=tiempo_estimado,
        responsable=responsable,
        fecha_objetivo=fecha_objetivo_obj,
        prioridad_remediacion=prioridad_remediacion,
        estado_remediacion=estado_remediacion,
        observaciones=observaciones,
        evidencia=evidencia,
        riesgo_residual=riesgo_residual,
        datos_completos=datos_completos,
        completada=(estado_remediacion.lower() == 'completada')
    )
    db.session.add(nueva_vuln)
    db.session.commit()
    
    return jsonify(nueva_vuln.to_dict()), 201

# API: Actualizar vulnerabilidad
@app.route('/api/vulnerabilidades/<int:id>', methods=['PUT'])
def update_vulnerabilidad(id):
    vulnerabilidad = Vulnerabilidad.query.get_or_404(id)
    data = request.get_json() or {}

    vulnerabilidad.descripcion = data.get('descripcion', vulnerabilidad.descripcion)
    vulnerabilidad.codigo = data.get('codigo', vulnerabilidad.codigo)
    vulnerabilidad.criticidad = data.get('criticidad', vulnerabilidad.criticidad)
    vulnerabilidad.impacto = data.get('impacto', vulnerabilidad.impacto)
    vulnerabilidad.plan_remediacion = data.get('plan_remediacion', vulnerabilidad.plan_remediacion)
    vulnerabilidad.tiempo_estimado = data.get('tiempo_estimado', vulnerabilidad.tiempo_estimado)
    vulnerabilidad.responsable = data.get('responsable', vulnerabilidad.responsable)
    vulnerabilidad.prioridad_remediacion = data.get('prioridad_remediacion', vulnerabilidad.prioridad_remediacion)
    vulnerabilidad.estado_remediacion = data.get('estado_remediacion', vulnerabilidad.estado_remediacion)
    vulnerabilidad.observaciones = data.get('observaciones', vulnerabilidad.observaciones)
    vulnerabilidad.evidencia = data.get('evidencia', vulnerabilidad.evidencia)
    fecha_objetivo = data.get('fecha_objetivo')
    if fecha_objetivo:
        try:
            vulnerabilidad.fecha_objetivo = datetime.fromisoformat(fecha_objetivo)
        except ValueError:
            pass

    vulnerabilidad.riesgo_residual = data.get('riesgo_residual', vulnerabilidad.riesgo_residual)

    if 'historial_cambios' in data:
        vulnerabilidad.historial_cambios = data.get('historial_cambios')

    if 'completada' in data:
        completada = data.get('completada')
        vulnerabilidad.completada = bool(completada)
        vulnerabilidad.fecha_completada = datetime.utcnow() if vulnerabilidad.completada else None

    db.session.commit()
    return jsonify(vulnerabilidad.to_dict()), 200

# Crear tablas si no existen
with app.app_context():
    db.create_all()
    print("Base de datos creada/verificada")

# Llamada a la API de Groq para obtener vulnerabilidades
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/api/consultar-vulnerabilidades', methods=['POST'])
def consultar_vulnerabilidades():
    data = request.get_json()
    equipo_id = data.get('equipo_id')
    equipo = Equipo.query.get_or_404(equipo_id)

    codigos_existentes = [v.codigo for v in Vulnerabilidad.query.filter_by(id_equipo=equipo_id).all() if v.codigo]
    
    prompt = f"""Eres un experto en ciberseguridad. Para el equipo '{equipo.tipo} {equipo.caracteristica}', 
    proporciona la información ÚNICAMENTE en formato JSON válido.
    
    {f"NO uses estos códigos CVE porque YA EXISTEN en este equipo: {', '.join(codigos_existentes)}" if codigos_existentes else ""}
    
    El JSON debe tener esta estructura exacta, SOLO NECESITO UNA VULNERABILIDAD:
    {{
        "vulnerabilidades": [
            {{
                "codigo": "CVE-XXXX-XXXX o identificador",
                "descripcion": "Descripción detallada de la vulnerabilidad",
                "criticidad": "Alta|Media|Baja",
                "impacto": "Impacto potencial para la organización",
                "recomendacion": "Pasos concretos para remediar",
                "tiempo_estimado": "UNICAMENTE Tiempo estimado de remediación"
            }}
        ]
    }}
    No incluyas texto adicional fuera del JSON. Solo el JSON."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )

        respuesta = chat_completion.choices[0].message.content.strip()
        
        if respuesta.startswith('```json'):
            respuesta = respuesta.replace('```json', '').replace('```', '').strip()
        elif respuesta.startswith('```'):
            respuesta = respuesta.replace('```', '').strip()
            
        datos_json = json.loads(respuesta)
        vulnerabilidades_data = datos_json.get('vulnerabilidades', [])

        vulnerabilidades_creadas = []
        for vuln_data in vulnerabilidades_data:
            nueva_vuln = Vulnerabilidad(
                id_equipo=equipo_id,
                descripcion=vuln_data.get('descripcion', ''),
                codigo=vuln_data.get('codigo', ''),
                criticidad=vuln_data.get('criticidad', 'Media'),
                impacto=vuln_data.get('impacto', ''),
                plan_remediacion=vuln_data.get('recomendacion', ''),
                tiempo_estimado=vuln_data.get('tiempo_estimado', ''),
                estado_remediacion='Pendiente',
                datos_completos=vuln_data,
                completada=False
            )
            db.session.add(nueva_vuln)
            vulnerabilidades_creadas.append(nueva_vuln)

        db.session.commit()
        return jsonify([v.to_dict() for v in vulnerabilidades_creadas]), 201
        
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON: {e}")
        print(f"Respuesta recibida: {respuesta}")
        
        nueva_vuln = Vulnerabilidad(
            id_equipo=equipo_id,
            descripcion=respuesta[:500],
            estado_remediacion='Pendiente',
            completada=False
        )
        db.session.add(nueva_vuln)
        db.session.commit()
        return jsonify([nueva_vuln.to_dict()]), 201
    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Gestion de Activos IT - Servidor Iniciado")
    print("http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)