-- ============================================================
-- ESQUEMA DE BASE DE DATOS PARA AGENTE AUTÓNOMO DE BIENESTAR
-- ============================================================
--
-- Este script crea las tablas necesarias para el Agente Autónomo
-- NO modifica las tablas existentes del sistema
--
-- Tablas nuevas:
-- 1. conversaciones_agente: Registro de conversaciones iniciadas
-- 2. mensajes_agente: Mensajes de cada conversación
-- 3. insights_agente: Insights generados para RRHH
--
-- ============================================================

USE novamind;

-- ============================================================
-- TABLA: conversaciones_agente
-- ============================================================
-- Registra cada conversación iniciada por el agente
-- Una conversación puede tener múltiples mensajes

CREATE TABLE IF NOT EXISTS conversaciones_agente (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Mensaje inicial del empleado
    mensaje_inicial TEXT NOT NULL,

    -- Resultado del análisis NLP del mensaje inicial (JSON)
    analisis_inicial JSON NOT NULL,

    -- Contexto opcional del empleado
    departamento VARCHAR(80) DEFAULT NULL,
    equipo VARCHAR(80) DEFAULT NULL,

    -- Categoría principal detectada
    categoria_principal VARCHAR(100) DEFAULT NULL,

    -- Nivel de riesgo (dinámico, se actualiza durante la conversación)
    nivel_riesgo_inicial VARCHAR(32) NOT NULL DEFAULT 'medio',
    nivel_riesgo_actual VARCHAR(32) NOT NULL DEFAULT 'medio',

    -- Estado de la conversación
    estado VARCHAR(32) NOT NULL DEFAULT 'activa',
    -- Estados posibles: 'activa', 'cerrada', 'escalada'

    -- Razón por la que se inició seguimiento
    razon_seguimiento TEXT DEFAULT NULL,

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Índices para búsquedas
    INDEX idx_departamento (departamento),
    INDEX idx_equipo (equipo),
    INDEX idx_estado (estado),
    INDEX idx_nivel_riesgo (nivel_riesgo_actual),
    INDEX idx_categoria (categoria_principal),
    INDEX idx_created (created_at),
    INDEX idx_updated (updated_at)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Conversaciones del agente autónomo con empleados';


-- ============================================================
-- TABLA: mensajes_agente
-- ============================================================
-- Almacena cada mensaje de la conversación (empleado y agente)

CREATE TABLE IF NOT EXISTS mensajes_agente (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Referencia a la conversación
    conversacion_id INT NOT NULL,

    -- Rol del autor del mensaje
    rol VARCHAR(32) NOT NULL,
    -- Valores posibles: 'empleado', 'agente'

    -- Contenido del mensaje
    contenido TEXT NOT NULL,

    -- Análisis NLP del mensaje (solo para mensajes de empleado) (JSON)
    analisis JSON DEFAULT NULL,

    -- Información adicional del mensaje (JSON)
    -- Ejemplo: {"tipo_pregunta": "bloqueo_liderazgo", "estrategia": "profundizar"}
    meta_info JSON DEFAULT NULL,

    -- Timestamp
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key hacia conversaciones_agente
    FOREIGN KEY (conversacion_id) REFERENCES conversaciones_agente(id) ON DELETE CASCADE,

    -- Índices
    INDEX idx_conversacion (conversacion_id),
    INDEX idx_rol (rol),
    INDEX idx_created (created_at)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Mensajes individuales de cada conversación del agente';


-- ============================================================
-- TABLA: insights_agente
-- ============================================================
-- Almacena insights generados por el agente para RRHH
-- Estos son descubrimientos valiosos que solo se revelan en conversación

CREATE TABLE IF NOT EXISTS insights_agente (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Referencia a la conversación que generó el insight
    conversacion_id INT NOT NULL,

    -- Tipo de insight
    tipo VARCHAR(64) NOT NULL,
    -- Valores posibles: 'problema_persistente', 'accion_fallida', 'bloqueo_organizacional'

    -- Categoría NLP asociada
    categoria VARCHAR(100) NOT NULL,

    -- Título descriptivo del insight
    titulo VARCHAR(255) NOT NULL,

    -- Descripción del insight
    descripcion TEXT NOT NULL,

    -- Resumen de la conversación completa
    contexto_completo TEXT NOT NULL,

    -- Recomendación específica para RRHH
    recomendacion_rrhh TEXT NOT NULL,

    -- Evidencias (JSON array de strings)
    evidencias JSON DEFAULT NULL,

    -- Severidad del insight
    severidad VARCHAR(32) NOT NULL DEFAULT 'media',
    -- Valores posibles: 'baja', 'media', 'alta', 'critica'

    -- Contexto del empleado
    departamento VARCHAR(80) DEFAULT NULL,
    equipo VARCHAR(80) DEFAULT NULL,

    -- Gestión del insight por RRHH
    estado VARCHAR(32) NOT NULL DEFAULT 'nuevo',
    -- Estados posibles: 'nuevo', 'revisado', 'en_accion', 'resuelto'

    revisado_por VARCHAR(50) DEFAULT NULL,
    -- Usuario RRHH que revisó el insight

    fecha_revision DATETIME DEFAULT NULL,

    notas_rrhh TEXT DEFAULT NULL,
    -- Notas internas que RRHH puede agregar

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign key hacia conversaciones_agente
    FOREIGN KEY (conversacion_id) REFERENCES conversaciones_agente(id) ON DELETE CASCADE,

    -- Índices para búsquedas y reportes
    INDEX idx_tipo (tipo),
    INDEX idx_categoria (categoria),
    INDEX idx_severidad (severidad),
    INDEX idx_estado (estado),
    INDEX idx_departamento (departamento),
    INDEX idx_equipo (equipo),
    INDEX idx_revisado_por (revisado_por),
    INDEX idx_created (created_at),
    INDEX idx_updated (updated_at),
    INDEX idx_fecha_revision (fecha_revision)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Insights generados por el agente para RRHH';


-- ============================================================
-- VISTA: resumen_insights_por_departamento
-- ============================================================
-- Vista útil para dashboard de RRHH

CREATE OR REPLACE VIEW resumen_insights_por_departamento AS
SELECT
    departamento,
    COUNT(*) AS total_insights,
    SUM(CASE WHEN estado = 'nuevo' THEN 1 ELSE 0 END) AS nuevos,
    SUM(CASE WHEN estado = 'revisado' THEN 1 ELSE 0 END) AS revisados,
    SUM(CASE WHEN estado = 'en_accion' THEN 1 ELSE 0 END) AS en_accion,
    SUM(CASE WHEN estado = 'resuelto' THEN 1 ELSE 0 END) AS resueltos,
    SUM(CASE WHEN severidad = 'critica' THEN 1 ELSE 0 END) AS criticos,
    SUM(CASE WHEN severidad = 'alta' THEN 1 ELSE 0 END) AS altos,
    SUM(CASE WHEN tipo = 'bloqueo_organizacional' THEN 1 ELSE 0 END) AS bloqueos,
    SUM(CASE WHEN tipo = 'problema_persistente' THEN 1 ELSE 0 END) AS persistentes,
    SUM(CASE WHEN tipo = 'accion_fallida' THEN 1 ELSE 0 END) AS acciones_fallidas
FROM insights_agente
WHERE departamento IS NOT NULL
GROUP BY departamento
ORDER BY total_insights DESC;


-- ============================================================
-- VISTA: insights_pendientes_revision
-- ============================================================
-- Insights que requieren atención inmediata de RRHH

CREATE OR REPLACE VIEW insights_pendientes_revision AS
SELECT
    i.id,
    i.tipo,
    i.titulo,
    i.severidad,
    i.departamento,
    i.equipo,
    i.categoria,
    i.created_at,
    c.nivel_riesgo_actual,
    DATEDIFF(NOW(), i.created_at) AS dias_sin_revisar
FROM insights_agente i
INNER JOIN conversaciones_agente c ON i.conversacion_id = c.id
WHERE i.estado = 'nuevo'
ORDER BY
    CASE i.severidad
        WHEN 'critica' THEN 1
        WHEN 'alta' THEN 2
        WHEN 'media' THEN 3
        ELSE 4
    END,
    i.created_at ASC;


-- ============================================================
-- VISTA: conversaciones_activas
-- ============================================================
-- Conversaciones que están en curso

CREATE OR REPLACE VIEW conversaciones_activas AS
SELECT
    c.id,
    c.categoria_principal,
    c.nivel_riesgo_actual,
    c.departamento,
    c.equipo,
    c.created_at,
    COUNT(m.id) AS num_mensajes,
    TIMESTAMPDIFF(MINUTE, c.updated_at, NOW()) AS minutos_inactiva
FROM conversaciones_agente c
LEFT JOIN mensajes_agente m ON c.id = m.conversacion_id
WHERE c.estado = 'activa'
GROUP BY c.id
ORDER BY c.updated_at DESC;


-- ============================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================================

-- Índice compuesto para búsquedas frecuentes de insights
CREATE INDEX idx_insights_estado_severidad
ON insights_agente(estado, severidad);

-- Índice compuesto para reportes por fecha
CREATE INDEX idx_insights_fecha_tipo
ON insights_agente(created_at, tipo);

-- Índice para búsquedas de conversaciones por riesgo y estado
CREATE INDEX idx_conv_riesgo_estado
ON conversaciones_agente(nivel_riesgo_actual, estado);



-- ============================================================
-- VERIFICACIÓN DE INSTALACIÓN
-- ============================================================

-- Query para verificar que las tablas se crearon correctamente
SELECT
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'novamind'
  AND TABLE_NAME IN ('conversaciones_agente', 'mensajes_agente', 'insights_agente')
ORDER BY TABLE_NAME;

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
