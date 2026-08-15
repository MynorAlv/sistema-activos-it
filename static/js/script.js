// API Base URL
const API_URL = '/api';

// Estado global
let equipoActual = null;
let equipoEditId = null;
let vulnerabilidadActual = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
    
    if (document.getElementById('equiposBody')) {
        cargarEquipos();
    }

    if (document.getElementById('riskIndex')) {
        cargarDashboard();
    }

    if (document.getElementById('nistScoreGlobal')) {
        cargarEvaluacionNIST();
    }

    // Cargar usuarios para la lista de responsables
    cargarResponsables();
});

function initEventListeners() {
    const agregarEquipoBtn = document.getElementById('agregarEquipoBtn');
    if (agregarEquipoBtn) {
        agregarEquipoBtn.addEventListener('click', agregarEquipo);
    }

    const tipoInput = document.getElementById('tipoInput');
    const caracteristicaInput = document.getElementById('caracteristicaInput');
    if (tipoInput && caracteristicaInput) {
        tipoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                caracteristicaInput.focus();
            }
        });
        caracteristicaInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                agregarEquipo();
            }
        });
    }
    
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) modal.style.display = 'none';
        });
    });
    
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    const consultarVulnerabilidadesBtn = document.getElementById('consultarVulnerabilidadesBtn');
    if (consultarVulnerabilidadesBtn) {
        consultarVulnerabilidadesBtn.addEventListener('click', consultarVulnerabilidades);
    }

    const exportModalBtnVer = document.getElementById('exportModalBtnVer');
    if (exportModalBtnVer) {
        exportModalBtnVer.addEventListener('click', function() {
            if (!exportContextoActual) return;
            const sep = exportContextoActual.urlBase.includes('?') ? '&' : '?';
            descargarReportePDF(exportContextoActual.urlBase + sep + 'view=1', exportContextoActual.nombreArchivo, this, true);
        });
    }

    const exportModalBtnDescargar = document.getElementById('exportModalBtnDescargar');
    if (exportModalBtnDescargar) {
        exportModalBtnDescargar.addEventListener('click', function() {
            if (!exportContextoActual) return;
            descargarReportePDF(exportContextoActual.urlBase, exportContextoActual.nombreArchivo, this, false);
        });
    }

    const showPendientesLink = document.getElementById('showPendientes');
    if (showPendientesLink) {
        showPendientesLink.addEventListener('click', (e) => {
            e.preventDefault();
            mostrarPendientes();
        });
    }

    const showCompletadasLink = document.getElementById('showCompletadas');
    if (showCompletadasLink) {
        showCompletadasLink.addEventListener('click', (e) => {
            e.preventDefault();
            mostrarCompletadas();
        });
    }

    const guardarEdicionEquipoBtn = document.getElementById('guardarEdicionEquipoBtn');
    if (guardarEdicionEquipoBtn) {
        guardarEdicionEquipoBtn.addEventListener('click', guardarEdicionEquipo);
    }

    const guardarRemediacionBtn = document.getElementById('guardarRemediacionBtn');
    if (guardarRemediacionBtn) {
        guardarRemediacionBtn.addEventListener('click', guardarRemediacion);
    }

    const verHistorialBtn = document.getElementById('verHistorialBtn');
    if (verHistorialBtn) {
        verHistorialBtn.addEventListener('click', toggleHistorial);
    }

    const detalleGestionBtn = document.getElementById('detalleGestionRemediacionBtn');
    if (detalleGestionBtn) {
        detalleGestionBtn.addEventListener('click', () => {
            document.getElementById('detallePendienteModal').style.display = 'none';
            abrirModalRemediacion(vulnerabilidadActual);
        });
    }

    // Slider de porcentaje
    const porcentajeRange = document.getElementById('remediacionPorcentajeRange');
    if (porcentajeRange) {
        porcentajeRange.addEventListener('input', function() {
            document.getElementById('remediacionPorcentajeDisplay').textContent = this.value + '%';
            document.getElementById('remediacionPorcentaje').value = this.value;
        });
    }
}

async function cargarResponsables() {
    try {
        const response = await fetch(`${API_URL}/usuarios/responsables`);
        const usuarios = await response.json();
        
        const datalist = document.getElementById('responsablesList');
        if (datalist) {
            datalist.innerHTML = usuarios.map(u => 
                `<option value="${escapeHtml(u.nombre_completo)}">`
            ).join('');
        }
    } catch (error) {
        console.error('Error cargando responsables:', error);
    }
}

async function cargarEquipos() {
    try {
        const response = await fetch(`${API_URL}/equipos`);
        const equipos = await response.json();
        
        const tbody = document.getElementById('equiposBody');
        tbody.innerHTML = '';
        
        if (equipos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">No hay equipos registrados</td></tr>`;
            return;
        }
        
        equipos.forEach(equipo => {
            const tr = document.createElement('tr');
            tr.dataset.id = equipo.id;
            
            // Mostrar SO y versión combinados
            let soVersion = 'N/A';
            if (equipo.sistema_operativo) {
                soVersion = equipo.sistema_operativo;
                if (equipo.version) {
                    soVersion += ` (${equipo.version})`;
                }
            } else if (equipo.version) {
                soVersion = equipo.version;
            }
            
            // Mostrar IP y hostname combinados
            let ipHostname = 'N/A';
            if (equipo.hostname) {
                ipHostname = equipo.hostname;
                if (equipo.ip) {
                    ipHostname += ` (${equipo.ip})`;
                }
            } else if (equipo.ip) {
                ipHostname = equipo.ip;
            }
            
            tr.innerHTML = `
                <td>${equipo.id}</td>
                <td><span class="tag">${escapeHtml(equipo.tipo)}</span></td>
                <td><strong>${escapeHtml(equipo.caracteristica)}</strong></td>
                <td><span class="text-sm">${escapeHtml(soVersion)}</span></td>
                <td><span class="text-sm">${escapeHtml(ipHostname)}</span></td>
                <td><span class="tag ${equipo.ambiente === 'Producción' ? 'tag-danger' : 'tag-info'}">${escapeHtml(equipo.ambiente || 'N/A')}</span></td>
                <td><span class="text-sm">${escapeHtml(equipo.ubicacion || 'N/A')}</span></td>
                <td><span class="text-sm">${equipo.fecha_creacion ? new Date(equipo.fecha_creacion).toLocaleDateString() : 'N/A'}</span></td>
                <td>
                    <button class="btn btn-sm btn-vulnerabilidades" data-id="${equipo.id}">
                        <i class="fas fa-shield-alt"></i>
                    </button>
                    <button class="btn btn-sm btn-edit" data-id="${equipo.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-eliminar" data-id="${equipo.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        // Event listeners...
        document.querySelectorAll('.btn-vulnerabilidades').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                abrirModalVulnerabilidades(id);
            });
        });
        
        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                if (confirm('¿Estás seguro de eliminar este equipo y todas sus vulnerabilidades?')) {
                    await eliminarEquipo(id);
                }
            });
        });

        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                abrirModalEdicionEquipo(id);
            });
        });
        
    } catch (error) {
        console.error('Error cargando equipos:', error);
        mostrarNotificacion('Error al cargar equipos', 'error');
    }
}

async function agregarEquipo() {
    // Obtener todos los campos del formulario
    const tipo = document.getElementById('tipoInput').value.trim();
    const caracteristica = document.getElementById('caracteristicaInput').value.trim();
    const propietario = document.getElementById('propietarioInput').value.trim();
    const ubicacion = document.getElementById('ubicacionInput').value.trim();
    const area_responsable = document.getElementById('areaInput').value.trim();
    const tipo_informacion = document.getElementById('tipoInformacionInput').value.trim();
    const dependencias = document.getElementById('dependenciasInput').value.trim();
    const sistema_operativo = document.getElementById('sistemaOperativoInput').value.trim();
    const version = document.getElementById('versionInput').value.trim();
    const ip = document.getElementById('ipInput').value.trim();
    const hostname = document.getElementById('hostnameInput').value.trim();
    const ambiente = document.getElementById('ambienteInput').value;
    const estado = document.getElementById('estadoInput').value;
    const fecha_revision = document.getElementById('fechaRevisionInput').value;
    
    // Validar campos obligatorios
    if (!tipo || !caracteristica) {
        mostrarNotificacion('Tipo y Característica son campos obligatorios', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/equipos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tipo,
                caracteristica,
                propietario: propietario || null,
                ubicacion: ubicacion || null,
                area_responsable: area_responsable || null,
                tipo_informacion: tipo_informacion || null,
                dependencias: dependencias || null,
                sistema_operativo: sistema_operativo || null,
                version: version || null,
                ip: ip || null,
                hostname: hostname || null,
                ambiente: ambiente || null,
                estado: estado || null,
                fecha_revision: fecha_revision || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al agregar equipo');
        }
        
        // Limpiar formulario
        document.getElementById('tipoInput').value = '';
        document.getElementById('caracteristicaInput').value = '';
        document.getElementById('propietarioInput').value = '';
        document.getElementById('ubicacionInput').value = '';
        document.getElementById('areaInput').value = '';
        document.getElementById('tipoInformacionInput').value = '';
        document.getElementById('dependenciasInput').value = '';
        document.getElementById('sistemaOperativoInput').value = '';
        document.getElementById('versionInput').value = '';
        document.getElementById('ipInput').value = '';
        document.getElementById('hostnameInput').value = '';
        document.getElementById('ambienteInput').value = '';
        document.getElementById('estadoInput').value = '';
        document.getElementById('fechaRevisionInput').value = '';
        
        mostrarNotificacion('Equipo agregado correctamente', 'success');
        cargarEquipos();
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion(error.message, 'error');
    }
}

async function eliminarEquipo(id) {
    try {
        const response = await fetch(`${API_URL}/equipos/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Error al eliminar equipo');
        }
        
        mostrarNotificacion('Equipo eliminado correctamente', 'success');
        cargarEquipos();
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al eliminar equipo', 'error');
    }
}

async function abrirModalVulnerabilidades(id) {
    try {
        const response = await fetch(`${API_URL}/equipos/${id}`);
        const equipo = await response.json();
        
        equipoActual = equipo;
        
        document.getElementById('modalTipo').textContent = equipo.tipo;
        document.getElementById('modalCaracteristica').textContent = equipo.caracteristica;
        document.getElementById('modalCriticidad').textContent = equipo.criticidad || 'N/A';
        
        await cargarVulnerabilidades(id);
        
        document.getElementById('vulnerabilidadesModal').style.display = 'block';
        document.getElementById('consultarVulnerabilidadesBtn').dataset.id = id;
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar vulnerabilidades', 'error');
    }
}

async function abrirModalEdicionEquipo(id) {
    try {
        const response = await fetch(`${API_URL}/equipos/${id}`);
        const equipo = await response.json();

        equipoEditId = equipo.id;
        
        // Llenar todos los campos del modal de edición
        document.getElementById('editTipoInput').value = equipo.tipo || '';
        document.getElementById('editCaracteristicaInput').value = equipo.caracteristica || '';
        document.getElementById('editPropietarioInput').value = equipo.propietario || '';
        document.getElementById('editUbicacionInput').value = equipo.ubicacion || '';
        document.getElementById('editAreaInput').value = equipo.area_responsable || '';
        document.getElementById('editTipoInformacionInput').value = equipo.tipo_informacion || '';
        document.getElementById('editDependenciasInput').value = equipo.dependencias || '';
        document.getElementById('editSistemaOperativoInput').value = equipo.sistema_operativo || '';
        document.getElementById('editVersionInput').value = equipo.version || '';
        document.getElementById('editIpInput').value = equipo.ip || '';
        document.getElementById('editHostnameInput').value = equipo.hostname || '';
        document.getElementById('editAmbienteInput').value = equipo.ambiente || '';
        document.getElementById('editEstadoInput').value = equipo.estado || '';
        document.getElementById('editFechaRevisionInput').value = equipo.fecha_revision || '';

        document.getElementById('editarEquipoModal').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar datos del equipo', 'error');
    }
}

async function guardarEdicionEquipo() {
    if (!equipoEditId) {
        mostrarNotificacion('Equipo no seleccionado para editar', 'warning');
        return;
    }

    const tipo = document.getElementById('editTipoInput').value.trim();
    const caracteristica = document.getElementById('editCaracteristicaInput').value.trim();
    const propietario = document.getElementById('editPropietarioInput').value.trim();
    const ubicacion = document.getElementById('editUbicacionInput').value.trim();
    const area_responsable = document.getElementById('editAreaInput').value.trim();
    const tipo_informacion = document.getElementById('editTipoInformacionInput').value.trim();
    const dependencias = document.getElementById('editDependenciasInput').value.trim();
    const sistema_operativo = document.getElementById('editSistemaOperativoInput').value.trim();
    const version = document.getElementById('editVersionInput').value.trim();
    const ip = document.getElementById('editIpInput').value.trim();
    const hostname = document.getElementById('editHostnameInput').value.trim();
    const ambiente = document.getElementById('editAmbienteInput').value;
    const estado = document.getElementById('editEstadoInput').value;
    const fecha_revision = document.getElementById('editFechaRevisionInput').value;

    if (!tipo || !caracteristica) {
        mostrarNotificacion('Tipo y Característica son campos obligatorios', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/equipos/${equipoEditId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tipo,
                caracteristica,
                propietario: propietario || null,
                ubicacion: ubicacion || null,
                area_responsable: area_responsable || null,
                tipo_informacion: tipo_informacion || null,
                dependencias: dependencias || null,
                sistema_operativo: sistema_operativo || null,
                version: version || null,
                ip: ip || null,
                hostname: hostname || null,
                ambiente: ambiente || null,
                estado: estado || null,
                fecha_revision: fecha_revision || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al actualizar equipo');
        }

        mostrarNotificacion('Equipo actualizado correctamente', 'success');
        document.getElementById('editarEquipoModal').style.display = 'none';
        equipoEditId = null;
        cargarEquipos();
        cargarDashboard();
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion(error.message, 'error');
    }
}

async function cargarDashboard() {
    if (!document.getElementById('riskIndex')) {
        return;
    }
    try {
        const response = await fetch(`${API_URL}/dashboard`);
        const data = await response.json();

        // --- Tarjeta 1: Riesgo General ---
        const riskIndex = data.risk_index || 0;
        document.getElementById('riskIndex').textContent = `${riskIndex.toFixed(2)}%`;
        
        // Barra de riesgo
        const riskBarFill = document.getElementById('riskBarFill');
        if (riskBarFill) {
            const clampedRisk = Math.min(riskIndex, 100);
            riskBarFill.style.width = `${clampedRisk}%`;
            // Color dinámico de la barra
            if (clampedRisk > 70) {
                riskBarFill.style.background = 'linear-gradient(90deg, #f59e0b, #dc2626)';
            } else if (clampedRisk > 40) {
                riskBarFill.style.background = 'linear-gradient(90deg, #fbbf24, #f59e0b)';
            } else {
                riskBarFill.style.background = 'linear-gradient(90deg, #22c55e, #16a34a)';
            }
        }

        // Badge de nivel de riesgo
        const riskLevel = document.getElementById('riskLevel');
        if (riskLevel) {
            let level, cls;
            if (riskIndex > 70) { level = 'Crítico'; cls = 'critico'; }
            else if (riskIndex > 50) { level = 'Alto'; cls = 'alto'; }
            else if (riskIndex > 30) { level = 'Medio'; cls = 'medio'; }
            else { level = 'Bajo'; cls = 'bajo'; }
            riskLevel.textContent = level;
            riskLevel.className = `badge-risk ${cls}`;
        }

        document.getElementById('riskAnalisis').textContent = 
            `Puntaje: ${data.total_score || 0} de ${data.max_possible_score || 1} puntos posibles`;

        document.getElementById('totalEquipos').textContent = data.total_equipos || 0;
        document.getElementById('totalVulns').textContent = (data.criticos || 0) + (data.medios || 0) + (data.bajos || 0);

        // --- Tarjeta 2: Criticidad ---
        const criticos = data.criticos || 0;
        const medios = data.medios || 0;
        const bajos = data.bajos || 0;
        const totalCrit = criticos + medios + bajos || 1;

        document.getElementById('criticaAlta').textContent = criticos;
        document.getElementById('criticaMedia').textContent = medios;
        document.getElementById('criticaBaja').textContent = bajos;

        // Barras de criticidad
        document.querySelectorAll('.criticidad-item').forEach(el => {
            const bar = el.querySelector('.criticidad-bar');
            if (!bar) return;
            const count = parseInt(el.querySelector('strong').textContent) || 0;
            const pct = Math.min((count / totalCrit) * 100, 100);
            bar.style.setProperty('--bar-width', pct + '%');
        });

        // --- Tarjeta 3: Remediación ---
        const pendientes = data.pendientes || 0;
        const completadas = data.completadas || 0;
        const enProceso = data.en_proceso || 0;
        const totalVulns = pendientes + completadas + enProceso || 1;

        document.getElementById('vulnPendientes').textContent = pendientes;
        document.getElementById('vulnEnProceso').textContent = enProceso;
        document.getElementById('vulnCompletadas').textContent = completadas;

        const pctCorregidas = (completadas / totalVulns) * 100;
        document.getElementById('vulnPorcentajeCorregidas').textContent = `${pctCorregidas.toFixed(2)}%`;
        
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = `${Math.min(pctCorregidas, 100)}%`;
        }

        // --- Tarjeta 4: Top Activos ---
        const topActivosContainer = document.getElementById('topActivosContainer');
        if (Array.isArray(data.top_activos) && data.top_activos.length) {
            topActivosContainer.innerHTML = data.top_activos.slice(0, 5).map(activo => `
                <div class="top-activo-item">
                    <div class="activo-info">
                        <span class="badge-tipo">${escapeHtml(activo.tipo || 'N/A')}</span>
                        <span>${escapeHtml(activo.caracteristica || '')}</span>
                    </div>
                    <div class="activo-metricas">
                        <span><i class="fas fa-shield-alt"></i> ${activo.total_vulnerabilidades || 0}</span>
                        <span><i class="fas fa-hourglass-half"></i> ${activo.pendientes || 0}</span>
                        <span><i class="fas fa-check-circle"></i> ${activo.completadas || 0}</span>
                    </div>
                </div>
            `).join('');
        } else {
            topActivosContainer.innerHTML = `
                <p class="text-muted" style="padding: 20px 0; text-align: center;">
                    <i class="fas fa-check-circle" style="color: var(--success);"></i> 
                    No hay activos con vulnerabilidades
                </p>
            `;
        }

    } catch (error) {
        console.error('Error cargando dashboard:', error);
    }
}

async function cargarVulnerabilidades(id) {
    try {
        const response = await fetch(`${API_URL}/equipos/${id}/vulnerabilidades`);
        const vulnerabilidades = await response.json();
        
        const container = document.getElementById('vulnerabilidadesContainer');
        container.innerHTML = '';
        
        if (vulnerabilidades.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay vulnerabilidades registradas para este equipo.</p>';
            return;
        }
        
        vulnerabilidades.forEach(vuln => {
            const div = document.createElement('div');
            div.className = `vulnerabilidad-item ${vuln.completada ? 'completada' : ''}`;
            div.dataset.id = vuln.id;
            
            let codigo = vuln.codigo || '';
            let criticidad = vuln.criticidad || '';
            let impacto = vuln.impacto || '';
            let planRemediacion = vuln.plan_remediacion || '';
            let tiempoEstimado = vuln.tiempo_estimado || '';
            let descripcion = vuln.descripcion || '';
            
            let criticidadClass = '';
            let criticidadDisplay = '';
            if (criticidad) {
                const criticidadMap = {'Alta': 'danger', 'Media': 'warning', 'Baja': 'success'};
                criticidadClass = criticidadMap[criticidad] || 'info';
                criticidadDisplay = criticidad;
            }
            
            const estadoRemediacion = vuln.estado_remediacion || 'Pendiente';
            const estadoClass = estadoRemediacion === 'Completada' ? 'completada' :
                               estadoRemediacion === 'En proceso' ? 'en-proceso' : 'pendiente';
            
            let html = `<div class="texto">`;
            
            if (codigo) {
                html += `<div class="vuln-codigo"><span class="badge info"><i class="fas fa-search"></i> ${escapeHtml(codigo)}</span></div>`;
            }
            
            html += `<div class="vuln-descripcion">${escapeHtml(descripcion)}</div>`;
            
            if (impacto) {
                html += `<div class="vuln-impacto"><strong><i class="fas fa-bolt"></i> Impacto:</strong> ${escapeHtml(impacto)}</div>`;
            }
            
            if (planRemediacion) {
                html += `<div class="vuln-plan"><strong><i class="fas fa-wrench"></i> Plan de remediación:</strong> ${escapeHtml(planRemediacion)}</div>`;
            }
            
            html += `<div class="vuln-meta">`;
            
            if (criticidadDisplay) {
                html += `<span class="badge ${criticidadClass}"><i class="fas fa-exclamation-triangle"></i> ${escapeHtml(criticidadDisplay)}</span>`;
            }
            
            if (tiempoEstimado) {
                html += `<span class="badge tiempo"><i class="fas fa-clock"></i> ${escapeHtml(tiempoEstimado)}</span>`;
            }
            
            html += `<span class="badge ${estadoClass}"><i class="fas fa-tag"></i> ${escapeHtml(estadoRemediacion)}</span>`;
            
            if (vuln.responsable) {
                html += `<span class="badge responsable"><i class="fas fa-user"></i> ${escapeHtml(vuln.responsable)}</span>`;
            }
            
            html += `</div>`;
            html += `</div>`;
            
            html += `<div class="acciones">`;
            
            html += `
                <button class="btn btn-sm warning gestionar-remediacion" data-id="${vuln.id}" title="Gestionar remediación">
                    <i class="fas fa-tools"></i> Gestionar
                </button>
            `;
            
            // ELIMINADO: Botón de marcar como completada según solicitud
            
            html += `
                <button class="btn btn-sm danger eliminar-vuln" data-id="${vuln.id}" title="Eliminar vulnerabilidad">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            
            html += `</div>`;
            
            div.innerHTML = html;
            container.appendChild(div);
        });
        
        document.querySelectorAll('.gestionar-remediacion').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                await abrirModalRemediacion(id);
            });
        });
        
        document.querySelectorAll('.eliminar-vuln').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                if (confirm('¿Eliminar esta vulnerabilidad?')) {
                    await eliminarVulnerabilidad(id);
                    await cargarVulnerabilidades(equipoActual.id);
                    cargarDashboard();
                }
            });
        });
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar vulnerabilidades', 'error');
    }
}

// En script.js - abrirModalRemediacion (versión simplificada)

async function abrirModalRemediacion(vulnId) {
    try {
        let vulnerabilidad;
        if (typeof vulnId === 'object' && vulnId.id) {
            vulnerabilidad = vulnId;
            vulnId = vulnerabilidad.id;
        } else {
            const response = await fetch(`${API_URL}/vulnerabilidades/${vulnId}`);
            if (!response.ok) {
                throw new Error('No se encontró la vulnerabilidad');
            }
            vulnerabilidad = await response.json();
            if (!vulnerabilidad) {
                mostrarNotificacion('No se encontró la vulnerabilidad', 'error');
                return;
            }
        }
        
        vulnerabilidadActual = vulnerabilidad;
        
        document.getElementById('remediacionCodigo').textContent = vulnerabilidad.codigo || 'Sin código';
        document.getElementById('remediacionCriticidad').textContent = vulnerabilidad.criticidad || 'N/A';
        document.getElementById('remediacionResponsable').value = vulnerabilidad.responsable || '';
        document.getElementById('remediacionFechaObjetivo').value = vulnerabilidad.fecha_objetivo || '';
        document.getElementById('remediacionPrioridad').value = vulnerabilidad.prioridad_remediacion || '';
        document.getElementById('remediacionEstado').value = vulnerabilidad.estado_remediacion || 'Pendiente';
        document.getElementById('remediacionObservaciones').value = vulnerabilidad.observaciones || '';
        document.getElementById('remediacionEvidencia').value = vulnerabilidad.evidencia || '';
        document.getElementById('remediacionRiesgoResidual').value = vulnerabilidad.riesgo_residual || '';
        
        // ELIMINADO: No hay campo de porcentaje manual
        
        // Mostrar info del avance automático
        actualizarInfoAvance(vulnerabilidad);
        
        cargarHistorial(vulnerabilidad);
        
        document.getElementById('guardarRemediacionBtn').dataset.id = vulnId;
        
        document.getElementById('remediacionModal').style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar datos de remediación: ' + error.message, 'error');
    }
}

function actualizarInfoAvance(vulnerabilidad) {
    const avance = vulnerabilidad.porcentaje_avance || 0;
    const avanceDisplay = avance.toFixed(2) + '%';
    
    let infoHtml = `
        <div style="background: var(--bg); padding: 12px; border-radius: 8px; margin-top: 10px; border-left: 3px solid var(--primary);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">
                    <i class="fas fa-robot"></i> Avance automático
                </span>
                <span style="font-weight: bold; font-size: 1.1rem; color: var(--primary);">${avanceDisplay}</span>
            </div>
            <div style="background: var(--border-color); height: 8px; border-radius: 4px; margin-top: 8px; overflow: hidden;">
                <div style="height: 100%; width: ${avance}%; background: var(--primary); border-radius: 4px; transition: width 0.5s ease;"></div>
            </div>
    `;
    
    // Mostrar factores que contribuyen al avance
    const factores = [];
    if (vulnerabilidad.responsable) factores.push('Responsable (20%)');
    if (vulnerabilidad.fecha_objetivo) factores.push('Fecha objetivo (10%+tiempo)');
    if (vulnerabilidad.plan_remediacion && vulnerabilidad.plan_remediacion.length > 10) factores.push('Plan detallado (20%)');
    else if (vulnerabilidad.plan_remediacion) factores.push('Plan básico (10%)');
    if (vulnerabilidad.observaciones && vulnerabilidad.observaciones.length > 10) factores.push('Observaciones detalladas (10%)');
    else if (vulnerabilidad.observaciones) factores.push('Observaciones básicas (5%)');
    if (vulnerabilidad.evidencia) factores.push('Evidencia (20%)');
    // ELIMINADA: if (vulnerabilidad.comentarios && vulnerabilidad.comentarios.length > 0) factores.push('Comentarios (10%)');
    if (vulnerabilidad.prioridad_remediacion === 'Alta') factores.push('Prioridad Alta (+5%)');
    
    if (factores.length > 0) {
        infoHtml += `
            <div style="margin-top: 8px; font-size: 0.75rem; color: var(--text-muted); display: flex; flex-wrap: wrap; gap: 4px;">
                <i class="fas fa-info-circle" style="margin-right: 4px;"></i>
                ${factores.map(f => `<span style="background: var(--border-color); padding: 2px 10px; border-radius: 10px;">${f}</span>`).join('')}
            </div>
        `;
    } else {
        infoHtml += `
            <div style="margin-top: 8px; font-size: 0.75rem; color: var(--text-muted);">
                <i class="fas fa-info-circle"></i> Complete los campos para aumentar el avance automático
            </div>
        `;
    }
    
    infoHtml += `</div>`;
    
    let infoContainer = document.getElementById('avanceInfoContainer');
    if (!infoContainer) {
        const modalBody = document.querySelector('#remediacionModal .modal-body');
        if (modalBody) {
            infoContainer = document.createElement('div');
            infoContainer.id = 'avanceInfoContainer';
            const riesgoField = document.getElementById('remediacionRiesgoResidual').closest('.form-group');
            if (riesgoField) {
                riesgoField.after(infoContainer);
            } else {
                modalBody.appendChild(infoContainer);
            }
        }
    }
    
    if (infoContainer) {
        infoContainer.innerHTML = infoHtml;
    }
}

function cargarHistorial(vulnerabilidad) {
    const historialContainer = document.getElementById('historialContainer');
    const historialLista = document.getElementById('historialLista');
    
    if (vulnerabilidad.historial_cambios && Array.isArray(vulnerabilidad.historial_cambios) && vulnerabilidad.historial_cambios.length > 0) {
        historialLista.innerHTML = vulnerabilidad.historial_cambios.map(item => `
            <div class="historial-item" style="padding: 5px 0; border-bottom: 1px solid var(--border-color);">
                <small><strong>${escapeHtml(item.fecha || '')}</strong> - ${escapeHtml(item.usuario || 'Sistema')}</small>
                <p style="margin: 2px 0;">${escapeHtml(item.accion || '')}</p>
            </div>
        `).join('');
        historialContainer.style.display = 'block';
    } else {
        historialLista.innerHTML = '<p class="text-muted">No hay cambios registrados.</p>';
        historialContainer.style.display = 'block';
    }
    historialContainer.style.display = 'none';
}

function toggleHistorial() {
    const container = document.getElementById('historialContainer');
    container.style.display = container.style.display === 'none' ? 'block' : 'none';
}

// Modificar guardarRemediacion - sin porcentaje manual
async function guardarRemediacion() {
    const id = parseInt(document.getElementById('guardarRemediacionBtn').dataset.id);
    if (!id) {
        mostrarNotificacion('No se ha seleccionado una vulnerabilidad', 'warning');
        return;
    }
    
    const estadoRemediacion = document.getElementById('remediacionEstado').value;
    
    const data = {
        estado_remediacion: estadoRemediacion,
        responsable: document.getElementById('remediacionResponsable').value.trim(),
        fecha_objetivo: document.getElementById('remediacionFechaObjetivo').value,
        prioridad_remediacion: document.getElementById('remediacionPrioridad').value,
        observaciones: document.getElementById('remediacionObservaciones').value.trim(),
        evidencia: document.getElementById('remediacionEvidencia').value.trim(),
        riesgo_residual: document.getElementById('remediacionRiesgoResidual').value,
        usuario: 'Usuario'
    };
    
    try {
        const response = await fetch(`${API_URL}/vulnerabilidades/${id}/remediacion`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al guardar remediación');
        }
        
        const result = await response.json();
        mostrarNotificacion('Remediación actualizada correctamente', 'success');
        document.getElementById('remediacionModal').style.display = 'none';
        
        if (equipoActual && equipoActual.id) {
            await cargarVulnerabilidades(equipoActual.id);
        }
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion(error.message, 'error');
    }
}
async function consultarVulnerabilidades() {
    const btn = document.getElementById('consultarVulnerabilidadesBtn');
    const id = parseInt(btn.dataset.id);
    
    if (!id) return;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Consultando...';
    
    try {
        const response = await fetch(`${API_URL}/consultar-vulnerabilidades`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ equipo_id: id })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al consultar vulnerabilidades');
        }
        
        const data = await response.json();
        mostrarNotificacion('Vulnerabilidades consultadas y guardadas', 'success');
        await cargarVulnerabilidades(id);
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-brain"></i> Consultar Vulnerabilidades IA';
    }
}

async function completarVulnerabilidad(id) {
    try {
        const response = await fetch(`${API_URL}/vulnerabilidades/${id}/completar`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Error al completar vulnerabilidad');
        }
        
        mostrarNotificacion('Vulnerabilidad completada', 'success');
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al completar vulnerabilidad', 'error');
    }
}

async function desmarcarVulnerabilidad(id) {
    try {
        const response = await fetch(`${API_URL}/vulnerabilidades/${id}/desmarcar`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Error al desmarcar vulnerabilidad');
        }
        
        mostrarNotificacion('Vulnerabilidad desmarcada', 'warning');
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al desmarcar vulnerabilidad', 'error');
    }
}

async function eliminarVulnerabilidad(id) {
    try {
        const response = await fetch(`${API_URL}/vulnerabilidades/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Error al eliminar vulnerabilidad');
        }
        
        mostrarNotificacion('Vulnerabilidad eliminada', 'success');
        cargarDashboard();
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al eliminar vulnerabilidad', 'error');
    }
}

async function mostrarPendientes() {
    try {
        const response = await fetch(`${API_URL}/vulnerabilidades/pendientes`);
        const vulnerabilidades = await response.json();
        
        const container = document.getElementById('pendientesContainer');
        container.innerHTML = '';
        
        if (vulnerabilidades.length === 0) {
            container.innerHTML = '<p class="text-muted"><i class="fas fa-check-circle" style="color: var(--success);"></i> No hay vulnerabilidades pendientes.</p>';
            return;
        }
        
        vulnerabilidades.forEach(vuln => {
            const div = document.createElement('div');
            div.className = 'vulnerabilidad-item pendiente';
            div.dataset.id = vuln.id;
            
            let codigo = vuln.codigo || '';
            let criticidad = vuln.criticidad || '';
            let tiempoEstimado = vuln.tiempo_estimado || '';
            let descripcion = vuln.descripcion || '';
            let estadoRemediacion = vuln.estado_remediacion || 'Pendiente';
            let equipoInfo = vuln.equipo_info || {};
            
            let criticidadClass = '';
            let criticidadDisplay = '';
            if (criticidad) {
                const criticidadMap = {'Alta': 'danger', 'Media': 'warning', 'Baja': 'success'};
                criticidadClass = criticidadMap[criticidad] || 'info';
                criticidadDisplay = criticidad;
            }
            
            const estadoClass = estadoRemediacion === 'Completada' ? 'completada' :
                               estadoRemediacion === 'En proceso' ? 'en-proceso' : 'pendiente';
            
            let html = `<div class="texto">`;
            
            html += `<div class="vuln-header" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px;">`;
            if (codigo) {
                html += `<span class="badge info"><i class="fas fa-search"></i> ${escapeHtml(codigo)}</span>`;
            }
            if (criticidadDisplay) {
                html += `<span class="badge ${criticidadClass}"><i class="fas fa-exclamation-triangle"></i> ${escapeHtml(criticidadDisplay)}</span>`;
            }
            if (tiempoEstimado) {
                html += `<span class="badge tiempo"><i class="fas fa-clock"></i> ${escapeHtml(tiempoEstimado)}</span>`;
            }
            html += `<span class="badge ${estadoClass}"><i class="fas fa-tag"></i> ${escapeHtml(estadoRemediacion)}</span>`;
            html += `</div>`;
            
            if (equipoInfo && equipoInfo.tipo) {
                html += `<div style="margin-bottom: 8px;">`;
                html += `<span class="badge equipo-id"><i class="fas fa-desktop"></i> ${escapeHtml(equipoInfo.tipo)} ${escapeHtml(equipoInfo.caracteristica || '')}</span>`;
                html += `</div>`;
            }
            
            html += `<div class="vuln-descripcion" style="font-size: 0.9em;">${escapeHtml(descripcion.substring(0, 150))}${descripcion.length > 150 ? '...' : ''}</div>`;
            html += `</div>`;
            
            html += `<div class="acciones">`;
            html += `
                <button class="btn btn-sm warning ver-detalle-pendiente" data-id="${vuln.id}" title="Ver detalle">
                    <i class="fas fa-eye"></i> Ver
                </button>
                <!-- <button class="btn btn-sm success completar-vuln-pendiente" data-id="${vuln.id}" title="Marcar como completada">-->
                    <!-- <i class="fas fa-check"></i>-->
                </button>
                <button class="btn btn-sm danger eliminar-vuln-pendiente" data-id="${vuln.id}" title="Eliminar vulnerabilidad">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            html += `</div>`;
            
            div.innerHTML = html;
            container.appendChild(div);
        });
        
        document.querySelectorAll('.ver-detalle-pendiente').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                await mostrarDetallePendiente(id);
            });
        });
        
        document.querySelectorAll('.completar-vuln-pendiente').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                await completarVulnerabilidad(id);
                await mostrarPendientes();
                cargarEquipos();
            });
        });
        
        document.querySelectorAll('.eliminar-vuln-pendiente').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                if (confirm('¿Eliminar esta vulnerabilidad?')) {
                    await eliminarVulnerabilidad(id);
                    await mostrarPendientes();
                    cargarEquipos();
                }
            });
        });
        
        document.getElementById('pendientesModal').style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar vulnerabilidades pendientes', 'error');
    }
}

async function mostrarDetallePendiente(id) {
    try {
        const modal = document.getElementById('detallePendienteModal');
        if (!modal) {
            mostrarNotificacion('Error: Modal no encontrado', 'error');
            return;
        }
        
        const response = await fetch(`${API_URL}/vulnerabilidades/${id}`);
        
        if (!response.ok) {
            throw new Error('Error al obtener la vulnerabilidad');
        }
        
        const vuln = await response.json();
        
        if (!vuln) {
            mostrarNotificacion('No se encontró la vulnerabilidad', 'error');
            return;
        }
        
        vulnerabilidadActual = vuln;
        const container = document.getElementById('detallePendienteContainer');
        
        if (!container) {
            mostrarNotificacion('Error: Contenedor no encontrado', 'error');
            return;
        }
        
        // Determinar colores según criticidad
        const criticidadColors = {
            'Alta': { bg: '#fef2f2', border: '#dc2626', text: '#dc2626' },
            'Media': { bg: '#fffbeb', border: '#f59e0b', text: '#f59e0b' },
            'Baja': { bg: '#f0fdf4', border: '#16a34a', text: '#16a34a' }
        };
        const criticidadColor = criticidadColors[vuln.criticidad] || { bg: '#f3f4f6', border: '#6b7280', text: '#6b7280' };
        
        // Determinar color del estado
        const estadoColors = {
            'Pendiente': { bg: '#fffbeb', color: '#f59e0b', icon: '<i class="fas fa-hourglass-half"></i>' },
            'En proceso': { bg: '#eff6ff', color: '#3b82f6', icon: '<i class="fas fa-arrows-rotate"></i>' },
            'Completada': { bg: '#f0fdf4', color: '#16a34a', icon: '<i class="fas fa-check-circle"></i>' }
        };
        const estadoColor = estadoColors[vuln.estado_remediacion] || estadoColors['Pendiente'];
        
        // Calcular avance con 2 decimales
        let avanceDisplay = '0%';
        let avanceNumero = 0;
        if (vuln.porcentaje_avance !== null && vuln.porcentaje_avance !== undefined) {
            avanceNumero = vuln.porcentaje_avance;
            avanceDisplay = avanceNumero.toFixed(2) + '%';
        }
        const colorAvance = avanceNumero < 30 ? '#dc2626' : avanceNumero < 70 ? '#f59e0b' : '#16a34a';
        
        let html = `
            <!-- Tarjeta de cabecera con criticidad y botón -->
            <div style="background: ${criticidadColor.bg}; border-left: 4px solid ${criticidadColor.border}; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <!-- Fila 1: Badges + Botón -->
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <h3 style="margin: 0; color: ${criticidadColor.text}; font-size: 1.1rem;">
                            <i class="fas fa-search"></i> ${vuln.codigo || 'Sin código'}
                        </h3>
                        <span style="font-size: 0.85rem; color: ${criticidadColor.text}; font-weight: 500; background: ${criticidadColor.bg}; padding: 2px 10px; border-radius: 12px; border: 1px solid ${criticidadColor.border};">
                            <i class="fas fa-exclamation-triangle"></i> ${vuln.criticidad || 'N/A'}
                        </span>
                        <span style="background: ${estadoColor.bg}; color: ${estadoColor.color}; padding: 2px 12px; border-radius: 12px; font-weight: 500; font-size: 0.85rem; border: 1px solid ${estadoColor.color};">
                            ${estadoColor.icon} ${vuln.estado_remediacion || 'Pendiente'}
                        </span>
                    </div>
                    <!-- Botón Gestionar remediación -->
                    <button onclick="document.getElementById('detallePendienteModal').style.display='none'; abrirModalRemediacion(${vuln.id})" 
                            class="btn warning" 
                            style="background: #f59e0b; color: #1a1a2e; padding: 6px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 6px; font-size: 0.9rem;">
                        <i class="fas fa-tools"></i> Gestionar remediación
                    </button>
                </div>
                
                <!-- Fila 2: Información compacta de remediación -->
                <div style="display: flex; flex-wrap: wrap; gap: 15px 25px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.06);">
        `;
        
        // Responsable
        if (vuln.responsable) {
            html += `
                <div style="display: flex; align-items: center; gap: 5px; font-size: 0.85rem;">
                    <span style="font-weight: 600;"><i class="fas fa-user"></i></span>
                    <span>${escapeHtml(vuln.responsable)}</span>
                </div>
            `;
        }
        
        // Fecha objetivo
        if (vuln.fecha_objetivo) {
            html += `
                <div style="display: flex; align-items: center; gap: 5px; font-size: 0.85rem;">
                    <span style="font-weight: 600;"><i class="fas fa-calendar-alt"></i></span>
                    <span>${escapeHtml(vuln.fecha_objetivo)}</span>
                </div>
            `;
        }
        
        // % Avance con barra pequeña y 2 decimales
        html += `
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.85rem;">
                <span style="font-weight: 600;"><i class="fas fa-chart-line"></i></span>
                <span style="font-weight: 500;">${avanceDisplay}</span>
                <div style="background: #e5e7eb; height: 5px; width: 60px; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: ${avanceNumero}%; background: ${colorAvance}; border-radius: 3px;"></div>
                </div>
            </div>
        `;
        
        // Prioridad
        if (vuln.prioridad_remediacion) {
            html += `
                <div style="display: flex; align-items: center; gap: 5px; font-size: 0.85rem;">
                    <span style="font-weight: 600;"><i class="fas fa-bullseye"></i></span>
                    <span>${escapeHtml(vuln.prioridad_remediacion)}</span>
                </div>
            `;
        }
        
        // Riesgo residual
        if (vuln.riesgo_residual) {
            const riesgoColors = {
                'Alto': '#dc2626',
                'Medio': '#f59e0b',
                'Bajo': '#16a34a',
                'Ninguno': '#6b7280'
            };
            const riesgoColor = riesgoColors[vuln.riesgo_residual] || '#6b7280';
            html += `
                <div style="display: flex; align-items: center; gap: 5px; font-size: 0.85rem;">
                    <span style="font-weight: 600;"><i class="fas fa-exclamation-triangle"></i></span>
                    <span style="color: ${riesgoColor}; font-weight: 500;">${escapeHtml(vuln.riesgo_residual)}</span>
                </div>
            `;
        }
        
        // Tiempo estimado
        if (vuln.tiempo_estimado) {
            html += `
                <div style="display: flex; align-items: center; gap: 5px; font-size: 0.85rem;">
                    <span style="font-weight: 600;"><i class="fas fa-clock"></i></span>
                    <span>${escapeHtml(vuln.tiempo_estimado)}</span>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
            
            <!-- Equipo -->
            <div style="margin-bottom: 15px; padding: 8px 0; border-bottom: 1px solid var(--border-color);">
                <span style="font-weight: 600; color: var(--text-muted);"><i class="fas fa-desktop"></i> Equipo:</span>
                <span style="font-weight: 500;">${vuln.equipo_info ? escapeHtml(vuln.equipo_info.tipo) + ' ' + escapeHtml(vuln.equipo_info.caracteristica || '') : 'N/A'}</span>
            </div>
            
            <!-- Descripción -->
            <div style="margin-bottom: 15px;">
                <div style="font-weight: 600; color: var(--text-muted); margin-bottom: 5px;"><i class="fas fa-align-left"></i> Descripción</div>
                <div style="background: var(--bg); padding: 12px; border-radius: 8px; line-height: 1.6;">
                    ${escapeHtml(vuln.descripcion)}
                </div>
            </div>
        `;
        
        // Impacto
        if (vuln.impacto) {
            html += `
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: 600; color: var(--text-muted); margin-bottom: 5px;"><i class="fas fa-bolt"></i> Impacto</div>
                    <div style="background: var(--bg); padding: 12px; border-radius: 8px; line-height: 1.6;">
                        ${escapeHtml(vuln.impacto)}
                    </div>
                </div>
            `;
        }
        
        // Plan de remediación
        if (vuln.plan_remediacion) {
            html += `
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: 600; color: var(--text-muted); margin-bottom: 5px;"><i class="fas fa-wrench"></i> Plan de remediación</div>
                    <div style="background: var(--bg); padding: 12px; border-radius: 8px; line-height: 1.6;">
                        ${escapeHtml(vuln.plan_remediacion)}
                    </div>
                </div>
            `;
        }
        
        // Observaciones
        if (vuln.observaciones) {
            html += `
                <div style="margin-bottom: 10px;">
                    <div style="font-weight: 600; color: var(--text-muted); margin-bottom: 5px;"><i class="fas fa-comment-alt"></i> Observaciones</div>
                    <div style="background: var(--bg); padding: 12px; border-radius: 8px; line-height: 1.6; font-size: 0.95rem;">
                        ${escapeHtml(vuln.observaciones)}
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        modal.style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar detalle: ' + error.message, 'error');
    }
}

async function mostrarCompletadas() {
    try {
        const response = await fetch(`${API_URL}/vulnerabilidades/completadas`);
        const vulnerabilidades = await response.json();
        
        const container = document.getElementById('completadasContainer');
        container.innerHTML = '';
        
        if (vulnerabilidades.length === 0) {
            container.innerHTML = '<p class="text-muted">No hay vulnerabilidades completadas.</p>';
            return;
        }
        
        vulnerabilidades.forEach(vuln => {
            const div = document.createElement('div');
            div.className = 'vulnerabilidad-item completada';
            div.dataset.id = vuln.id;
            
            let codigo = vuln.codigo || '';
            let criticidad = vuln.criticidad || '';
            let descripcion = vuln.descripcion || '';
            let equipoInfo = vuln.equipo_info || {};
            
            let criticidadClass = '';
            let criticidadDisplay = '';
            if (criticidad) {
                const criticidadMap = {'Alta': 'danger', 'Media': 'warning', 'Baja': 'success'};
                criticidadClass = criticidadMap[criticidad] || 'info';
                criticidadDisplay = criticidad;
            }
            
            let html = `<div class="texto">`;
            
            html += `<div class="vuln-header" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px;">`;
            if (codigo) {
                html += `<span class="badge info"><i class="fas fa-search"></i> ${escapeHtml(codigo)}</span>`;
            }
            if (criticidadDisplay) {
                html += `<span class="badge ${criticidadClass}"><i class="fas fa-exclamation-triangle"></i> ${escapeHtml(criticidadDisplay)}</span>`;
            }
            html += `<span class="badge completada"><i class="fas fa-check-circle"></i> Completada</span>`;
            if (vuln.fecha_completada) {
                html += `<span class="badge fecha"><i class="fas fa-calendar-alt"></i> ${escapeHtml(vuln.fecha_completada)}</span>`;
            }
            html += `</div>`;
            
            if (equipoInfo && equipoInfo.tipo) {
                html += `<div style="margin-bottom: 8px;">`;
                html += `<span class="badge equipo-id"><i class="fas fa-desktop"></i> ${escapeHtml(equipoInfo.tipo)} ${escapeHtml(equipoInfo.caracteristica || '')}</span>`;
                html += `</div>`;
            }
            
            html += `<div class="vuln-descripcion" style="font-size: 0.9em;">${escapeHtml(descripcion.substring(0, 150))}${descripcion.length > 150 ? '...' : ''}</div>`;
            html += `</div>`;
            
            html += `<div class="acciones">`;
            html += `
                <button class="btn btn-sm warning desmarcar-vuln-completada" data-id="${vuln.id}" title="Reabrir vulnerabilidad">
                    <i class="fas fa-undo"></i>
                </button>
                <button class="btn btn-sm danger eliminar-vuln-completada" data-id="${vuln.id}" title="Eliminar vulnerabilidad">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            html += `</div>`;
            
            div.innerHTML = html;
            container.appendChild(div);
        });
        
        document.querySelectorAll('.desmarcar-vuln-completada').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                await desmarcarVulnerabilidad(id);
                await mostrarCompletadas();
                cargarEquipos();
            });
        });
        
        document.querySelectorAll('.eliminar-vuln-completada').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = parseInt(btn.dataset.id);
                if (confirm('¿Eliminar esta vulnerabilidad?')) {
                    await eliminarVulnerabilidad(id);
                    await mostrarCompletadas();
                    cargarEquipos();
                }
            });
        });
        
        document.getElementById('completadasModal').style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al cargar vulnerabilidades completadas', 'error');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function mostrarNotificacion(mensaje, tipo = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const colors = {
        success: '#16a34a',
        error: '#dc2626',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${colors[tipo] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 99999;
        max-width: 400px;
        animation: slideDown 0.3s ease;
        font-weight: 500;
    `;
    notification.textContent = mensaje;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}


// Función para minimizar/maximizar el formulario de agregar equipo
function toggleForm() {
    const content = document.getElementById('formContent');
    const btn = document.getElementById('toggleFormBtn');
    
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        btn.innerHTML = '<i class="fas fa-chevron-down"></i>';
        btn.style.transform = 'rotate(0deg)';
    } else {
        content.style.display = 'none';
        btn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        btn.style.transform = 'rotate(0deg)';
    }
}

/**
 * Variable global para almacenar el contexto del reporte a exportar
 */
let exportContextoActual = null;

/**
 * Abre el diálogo de exportación contextual según el módulo que lo invocó
 */
function abrirModalExportacion(modulo) {
    const modal = document.getElementById('modalExportarReporte');
    if (!modal) return;

    const tituloEl = document.getElementById('exportModalTitulo');
    const iconEl = document.getElementById('exportModalIcon');
    const nombreEl = document.getElementById('exportModalNombreReporte');
    const descEl = document.getElementById('exportModalDescripcion');
    const detalleRegistrosEl = document.getElementById('exportModalDetalleRegistros');
    const filtrosContainer = document.getElementById('exportModalFiltrosContainer');
    
    filtrosContainer.style.display = 'none';

    if (modulo === 'equipos') {
        exportContextoActual = {
            urlBase: '/api/reportes/equipos/pdf',
            nombreArchivo: 'Inventario_Activos_IT.pdf',
            tipo: 'equipos'
        };
        tituloEl.innerHTML = '<i class="fas fa-server"></i> Exportar Inventario de Activos';
        iconEl.innerHTML = '<i class="fas fa-server"></i>';
        iconEl.style.background = '#f0fdf4';
        iconEl.style.color = '#16a34a';
        nombreEl.textContent = 'Inventario General de Activos IT';
        descEl.textContent = 'Genera un documento PDF formal con la infraestructura completa de servidores, switches, firewalls, direccionamiento IP y criticidad asignada.';
        detalleRegistrosEl.innerHTML = '<i class="fas fa-layer-group"></i> Alcance: <strong>Inventario Completo</strong>';
    } 
    else if (modulo === 'ejecutivo') {
        exportContextoActual = {
            urlBase: '/api/reportes/ejecutivo/pdf',
            nombreArchivo: 'Informe_Ejecutivo_Seguridad.pdf',
            tipo: 'ejecutivo'
        };
        tituloEl.innerHTML = '<i class="fas fa-chart-pie"></i> Exportar Informe Ejecutivo';
        iconEl.innerHTML = '<i class="fas fa-chart-pie"></i>';
        iconEl.style.background = '#eff6ff';
        iconEl.style.color = '#2563eb';
        nombreEl.textContent = 'Informe Ejecutivo de Ciberseguridad';
        descEl.textContent = 'Resumen consolidado para comités y gerencia con el cálculo del Índice de Riesgo, métricas de efectividad en remediación y los activos con mayor nivel de exposición.';
        detalleRegistrosEl.innerHTML = '<i class="fas fa-layer-group"></i> Alcance: <strong>Métricas & Dashboard</strong>';
    }
    else if (modulo === 'equipo_especifico') {
        if (!equipoActual || !equipoActual.id) {
            mostrarNotificacion('Seleccione un equipo para exportar su reporte', 'warning');
            return;
        }
        const tipoNombre = `${equipoActual.tipo || 'Equipo'} ${equipoActual.caracteristica || ''}`.trim();
        exportContextoActual = {
            urlBase: `/api/reportes/vulnerabilidades/pdf?equipo_id=${equipoActual.id}`,
            nombreArchivo: `Reporte_Vulns_${(equipoActual.tipo || 'Equipo').replace(/\s+/g, '_')}_${equipoActual.id}.pdf`,
            tipo: 'equipo_especifico'
        };
        tituloEl.innerHTML = '<i class="fas fa-shield-alt"></i> Exportar Vulnerabilidades del Activo';
        iconEl.innerHTML = '<i class="fas fa-shield-alt"></i>';
        iconEl.style.background = '#fef2f2';
        iconEl.style.color = '#dc2626';
        nombreEl.textContent = `Reporte de Vulnerabilidades: ${tipoNombre}`;
        descEl.textContent = `Lista de vulnerabilidades identificadas exclusivamente para este activo, sus responsables asignados, avance de mitigación y planes de remediación.`;
        detalleRegistrosEl.innerHTML = `<i class="fas fa-layer-group"></i> Activo: <strong>${tipoNombre}</strong>`;
    }
    else if (modulo === 'pendientes') {
        exportContextoActual = {
            urlBase: '/api/reportes/vulnerabilidades/pdf?estado=pendientes',
            nombreArchivo: 'Reporte_Vulnerabilidades_Pendientes.pdf',
            tipo: 'pendientes'
        };
        tituloEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Exportar Vulnerabilidades Pendientes';
        iconEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        iconEl.style.background = '#fffbeb';
        iconEl.style.color = '#d97706';
        nombreEl.textContent = 'Vulnerabilidades Pendientes de Atención';
        descEl.textContent = 'Auditoría de hallazgos activos que requieren asignación de responsable, fecha objetivo o ejecución del plan de remediación.';
        detalleRegistrosEl.innerHTML = '<i class="fas fa-layer-group"></i> Alcance: <strong>Solo Pendientes</strong>';
    }
    else if (modulo === 'completadas') {
        exportContextoActual = {
            urlBase: '/api/reportes/vulnerabilidades/pdf?estado=completadas',
            nombreArchivo: 'Reporte_Vulnerabilidades_Completadas.pdf',
            tipo: 'completadas'
        };
        tituloEl.innerHTML = '<i class="fas fa-check-circle"></i> Exportar Vulnerabilidades Completadas';
        iconEl.innerHTML = '<i class="fas fa-check-circle"></i>';
        iconEl.style.background = '#f0fdf4';
        iconEl.style.color = '#16a34a';
        nombreEl.textContent = 'Vulnerabilidades Remediadas y Cerradas';
        descEl.textContent = 'Histórico de vulnerabilidades mitigadas, verificadas y resueltas satisfactoriamente con sus fechas de cierre.';
        detalleRegistrosEl.innerHTML = '<i class="fas fa-layer-group"></i> Alcance: <strong>Solo Completadas</strong>';
    }
    else if (modulo === 'nist') {
        exportContextoActual = {
            urlBase: '/api/reportes/nist/pdf',
            nombreArchivo: 'Evaluacion_NIST_CSF.pdf',
            tipo: 'nist'
        };
        tituloEl.innerHTML = '<i class="fas fa-certificate"></i> Exportar Evaluación NIST CSF';
        iconEl.innerHTML = '<i class="fas fa-certificate"></i>';
        iconEl.style.background = '#eef2ff';
        iconEl.style.color = '#6366f1';
        nombreEl.textContent = 'Informe Oficial de Ciberseguridad NIST CSF 2.0';
        descEl.textContent = 'Auditoría de madurez y cumplimiento según las 6 funciones: Gobernar, Identificar, Proteger, Detectar, Responder y Recuperar, con plan de acción prioritario.';
        detalleRegistrosEl.innerHTML = '<i class="fas fa-layer-group"></i> Alcance: <strong>Marco NIST CSF 2.0</strong>';
    }

    modal.style.display = 'block';
}

/**
 * Descarga o visualiza reportes PDF de manera fluida y asíncrona
 * sin parpadeos de pestañas en blanco y con feedback visual al usuario.
 */
async function descargarReportePDF(url, nombreSugerido, btnElement = null, abrirPestana = false) {
    let originalHtml = '';
    if (btnElement) {
        originalHtml = btnElement.innerHTML;
        btnElement.disabled = true;
        btnElement.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Procesando...';
    } else {
        mostrarNotificacion('Procesando reporte PDF...', 'info');
    }

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Respuesta del servidor no válida (${response.status})`);
        }
        
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        
        if (abrirPestana) {
            window.open(blobUrl, '_blank');
            mostrarNotificacion('Reporte abierto en visor PDF', 'success');
        } else {
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = blobUrl;
            a.download = nombreSugerido || 'Reporte_Seguridad_IT.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            mostrarNotificacion('✓ Reporte PDF descargado con éxito', 'success');
        }
        
        // Cerrar el modal de exportación si está abierto
        const exportModal = document.getElementById('modalExportarReporte');
        if (exportModal) exportModal.style.display = 'none';

        // Liberar memoria del blob después de 30 segundos
        setTimeout(() => window.URL.revokeObjectURL(blobUrl), 30000);
    } catch (error) {
        console.error('Error al generar PDF:', error);
        mostrarNotificacion('Error al procesar el reporte PDF: ' + error.message, 'error');
    } finally {
        if (btnElement) {
            btnElement.disabled = false;
            btnElement.innerHTML = originalHtml;
        }
    }
}

/**
 * Carga y renderiza la evaluación de ciberseguridad NIST CSF 2.0
 */
async function cargarEvaluacionNIST() {
    try {
        const response = await fetch('/api/nist/evaluacion');
        if (!response.ok) throw new Error('Error al obtener datos NIST');
        const data = await response.json();

        // 1. Resumen superior
        const tierTitulo = document.getElementById('nistTierTitulo');
        const tierDesc = document.getElementById('nistTierDesc');
        const scoreGlobal = document.getElementById('nistScoreGlobal');
        const barraGlobal = document.getElementById('nistBarraGlobal');
        const totalEquipos = document.getElementById('nistTotalEquipos');
        const totalVulns = document.getElementById('nistTotalVulns');
        const nivelLabel = document.getElementById('nistNivelLabel');

        if (tierTitulo) tierTitulo.textContent = data.tier || 'Tier 1';
        if (tierDesc) tierDesc.textContent = data.tier_desc || '';
        if (scoreGlobal) scoreGlobal.textContent = `${data.score_global}%`;
        if (barraGlobal) barraGlobal.style.width = `${Math.min(100, data.score_global)}%`;
        if (totalEquipos) totalEquipos.textContent = data.total_equipos || 0;
        if (totalVulns) totalVulns.textContent = data.total_vulnerabilidades || 0;
        if (nivelLabel) nivelLabel.textContent = `Nivel ${data.tier_nivel || 1} de 4 (Tiers NIST)`;

        // Colores de madurez global
        if (scoreGlobal) {
            if (data.score_global >= 80) scoreGlobal.style.color = '#16a34a';
            else if (data.score_global >= 60) scoreGlobal.style.color = '#2563eb';
            else if (data.score_global >= 40) scoreGlobal.style.color = '#f59e0b';
            else scoreGlobal.style.color = '#dc2626';
        }

        // 2. Renderizar las 6 Funciones con paleta corporativa armonizada
        const funcContainer = document.getElementById('nistFuncionesContainer');
        if (funcContainer && data.funciones) {
            funcContainer.innerHTML = '';
            data.funciones.forEach(f => {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.cssText = 'margin: 0; padding: 20px; border: 1px solid var(--card-border); background: var(--panel); display: flex; flex-direction: column; justify-content: space-between; box-shadow: var(--shadow-sm);';
                
                const score = f.score || 0;
                let estadoLabel = 'Inicial';
                let badgeBg = '#fef2f2';
                let badgeColor = '#dc2626';
                let barColor = '#dc2626';

                if (score >= 75) {
                    estadoLabel = 'Optimizado';
                    badgeBg = '#f0fdf4';
                    badgeColor = '#16a34a';
                    barColor = '#16a34a';
                } else if (score >= 50) {
                    estadoLabel = 'Gestionado';
                    badgeBg = '#eff6ff';
                    badgeColor = '#2563eb';
                    barColor = '#2563eb';
                } else if (score >= 30) {
                    estadoLabel = 'En Desarrollo';
                    badgeBg = '#fffbeb';
                    badgeColor = '#d97706';
                    barColor = '#d97706';
                }

                const iconoValido = f.icono || 'fas fa-shield-alt';

                card.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <div style="width: 42px; height: 42px; border-radius: 8px; background: var(--bg); border: 1px solid var(--card-border); color: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
                                    <i class="${iconoValido}"></i>
                                </div>
                                <div>
                                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: var(--text);">${f.nombre}</h3>
                                    <span style="font-size: 0.75rem; color: var(--muted); font-weight: 600; text-transform: uppercase;">Función ${f.codigo}</span>
                                </div>
                            </div>
                            <span style="font-size: 0.75rem; font-weight: 700; background: ${badgeBg}; color: ${badgeColor}; padding: 4px 10px; border-radius: 12px;">
                                ● ${estadoLabel}
                            </span>
                        </div>
                        <p style="font-size: 0.85rem; color: var(--muted); line-height: 1.45; margin-bottom: 16px;">
                            ${f.descripcion}
                        </p>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 0.85rem;">
                            <span style="color: var(--muted); font-weight: 500;">Nivel de Cumplimiento</span>
                            <strong style="color: var(--text); font-size: 1rem;">${score}%</strong>
                        </div>
                        <div style="background: var(--bg); border: 1px solid var(--card-border); height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="height: 100%; width: ${Math.min(100, score)}%; background: ${barColor}; border-radius: 4px; transition: width 0.6s ease;"></div>
                        </div>
                    </div>
                `;
                funcContainer.appendChild(card);
            });
        }

        // 3. Renderizar Recomendaciones
        const recomContainer = document.getElementById('nistRecomendacionesContainer');
        if (recomContainer && data.recomendaciones) {
            recomContainer.innerHTML = '';
            data.recomendaciones.forEach(r => {
                const item = document.createElement('div');
                item.style.cssText = 'display: flex; align-items: flex-start; gap: 14px; padding: 14px; border-radius: 8px; background: var(--bg); border: 1px solid var(--card-border); margin-bottom: 10px;';
                
                let pBg = '#fef2f2', pColor = '#dc2626';
                if (r.prioridad === 'Media') { pBg = '#fffbeb'; pColor = '#d97706'; }
                else if (r.prioridad === 'Baja') { pBg = '#f0fdf4'; pColor = '#16a34a'; }

                item.innerHTML = `
                    <div style="width: 36px; height: 36px; border-radius: 6px; background: ${pBg}; color: ${pColor}; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0;">
                        <i class="${r.icono}"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; flex-wrap: wrap; gap: 6px;">
                            <h4 style="margin: 0; font-size: 0.95rem; color: var(--text);">${r.titulo}</h4>
                            <span style="font-size: 0.75rem; font-weight: 700; background: ${pBg}; color: ${pColor}; padding: 2px 8px; border-radius: 10px;">
                                Prioridad ${r.prioridad} • ${r.funcion}
                            </span>
                        </div>
                        <p style="margin: 0; font-size: 0.85rem; color: var(--muted); line-height: 1.4;">
                            ${r.detalle}
                        </p>
                    </div>
                `;
                recomContainer.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error al cargar evaluación NIST:', error);
        mostrarNotificacion('No se pudo cargar la evaluación NIST: ' + error.message, 'error');
    }
}