# Arquitectura del Agente Autónomo de Bienestar Laboral

## 1. VISIÓN GENERAL

El Agente Autónomo de Bienestar Laboral es una **extensión inteligente** del sistema NovaMind que transforma el análisis estático de comentarios en un **sistema conversacional proactivo** que:

- **NO es un chatbot genérico** de consejos de autoayuda
- **NO reemplaza** el sistema de análisis existente
- **SÍ genera insights únicos** sobre por qué los problemas persisten
- **SÍ detecta bloqueos organizacionales** que un comentario estático no revela
- **SÍ mantiene anonimato total** del empleado

---

## 2. COMPONENTES PRINCIPALES

### 2.1 Backend - Módulo de IA del Agente

**Archivo:** `backend/ia/iaAgent.py`

**Responsabilidad:** Lógica de decisión autónoma del agente

**Características:**

1. **Sistema de Decisión Contextual**
   - Analiza respuesta del empleado
   - Decide si profundizar o cambiar estrategia
   - Ajusta nivel de riesgo dinámicamente

2. **Generación de Preguntas Guiadas**
   - NO preguntas genéricas de chatbot
   - Preguntas específicas basadas en:
     - Análisis NLP del mensaje inicial
     - Categorías detectadas (ej. "sobrecarga laboral")
     - Respuestas previas del empleado
     - Nivel de estrés y emoción

3. **Detección de Bloqueos**
   - Identifica cuando una recomendación no funcionó
   - Detecta barreras organizacionales:
     - Supervisor no responde
     - Recursos prometidos no llegaron
     - Problema reportado previamente sin solución
     - Falta de seguimiento de RRHH

4. **Generación de Insights**
   - **Insight Tipo 1:** Problema persistente
     - Empleado ya intentó resolver sin éxito
     - Reportado >2 veces sin cambio

   - **Insight Tipo 2:** Acción fallida
     - Recomendación de RRHH no funcionó
     - Recursos/herramientas no ayudaron

   - **Insight Tipo 3:** Bloqueo organizacional
     - Liderazgo no responde
     - Procesos burocráticos impiden solución
     - Cultura organizacional perpetúa problema

**Clases principales:**

```python
class AgenteAutonomo:
    """
    Agente autónomo que decide cómo continuar la conversación
    basándose en el análisis NLP y contexto acumulado.
    """

    def __init__(self, nlp_analyzer: NLPAnalyzer):
        """Inicializa con acceso al analizador NLP existente"""

    def iniciar_conversacion(self, mensaje_inicial: str, meta: dict) -> dict:
        """
        Analiza mensaje inicial y decide si activar conversación profunda

        Returns:
            {
                "requiere_seguimiento": bool,
                "analisis_nlp": dict,  # Del sistema existente
                "pregunta_agente": str | None,
                "razon_seguimiento": str,
                "nivel_riesgo": str  # bajo, medio, alto, critico
            }
        """

    def procesar_respuesta(self,
                          conversacion_id: int,
                          respuesta_empleado: str) -> dict:
        """
        Procesa respuesta del empleado y decide siguiente acción

        Returns:
            {
                "accion": str,  # "profundizar", "cerrar", "escalar"
                "pregunta": str | None,
                "analisis": dict,
                "insight_generado": dict | None,
                "nivel_riesgo_actualizado": str
            }
        """

    def detectar_bloqueo(self,
                        respuesta: str,
                        contexto_previo: list) -> dict:
        """
        Detecta si el empleado menciona bloqueos organizacionales

        Returns:
            {
                "hay_bloqueo": bool,
                "tipo": str,  # "liderazgo", "recursos", "proceso", "cultural"
                "descripcion": str,
                "severidad": str
            }
        """

    def generar_insight(self,
                       conversacion_completa: dict,
                       bloqueo: dict) -> dict:
        """
        Genera insight para RRHH basado en la conversación completa

        Returns:
            {
                "tipo": str,  # "problema_persistente", "accion_fallida", "bloqueo"
                "categoria": str,
                "descripcion": str,
                "contexto": str,
                "recomendacion_rrhh": str,
                "severidad": str,
                "departamento": str,
                "equipo": str
            }
        """
```

---

### 2.2 Backend - API del Agente

**Archivo:** `backend/api/agente.py`

**Endpoints:**

#### POST /agente/iniciar/

**Propósito:** Inicia conversación con el agente

**Request:**
```json
{
  "mensaje": "Me siento muy estresado con la carga de trabajo",
  "meta": {
    "departamento": "Ventas",
    "equipo": "Turno A"
  }
}
```

**Response:**
```json
{
  "conversacion_id": 123,
  "requiere_seguimiento": true,
  "pregunta": "¿Ya intentaste hablar con tu supervisor sobre esto?",
  "analisis_inicial": {
    "emotion": {"label": "tristeza", "score": 0.85},
    "stress": {"level": "alto"},
    "categories": [{"label": "sobrecarga laboral", "score": 0.92}]
  },
  "nivel_riesgo": "alto"
}
```

#### POST /agente/responder/

**Propósito:** Procesa respuesta del empleado

**Request:**
```json
{
  "conversacion_id": 123,
  "respuesta": "Sí, pero mi jefe nunca tiene tiempo para reunirse"
}
```

**Response:**
```json
{
  "accion": "profundizar",
  "pregunta": "¿Cuánto tiempo llevas intentando reunirte sin éxito?",
  "insight_preliminar": {
    "tipo": "bloqueo_liderazgo",
    "severidad": "media"
  },
  "nivel_riesgo": "alto"
}
```

#### GET /agente/conversacion/{id}/

**Propósito:** Obtiene historial de conversación

---

### 2.3 Backend - Base de Datos

#### Tabla: `conversaciones_agente`

```sql
CREATE TABLE conversaciones_agente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mensaje_inicial TEXT NOT NULL,
    analisis_inicial JSON NOT NULL,  -- Resultado del análisis NLP
    departamento VARCHAR(80),
    equipo VARCHAR(80),
    nivel_riesgo_inicial VARCHAR(32) NOT NULL,
    nivel_riesgo_actual VARCHAR(32) NOT NULL,
    estado VARCHAR(32) NOT NULL,  -- 'activa', 'cerrada', 'escalada'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_departamento (departamento),
    INDEX idx_estado (estado),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Tabla: `mensajes_agente`

```sql
CREATE TABLE mensajes_agente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversacion_id INT NOT NULL,
    rol VARCHAR(32) NOT NULL,  -- 'empleado', 'agente'
    contenido TEXT NOT NULL,
    analisis JSON,  -- Análisis NLP del mensaje (solo para mensajes de empleado)
    metadata JSON,  -- Información adicional (tipo de pregunta, estrategia usada)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversacion_id) REFERENCES conversaciones_agente(id) ON DELETE CASCADE,
    INDEX idx_conversacion (conversacion_id),
    INDEX idx_rol (rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Tabla: `insights_agente`

```sql
CREATE TABLE insights_agente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversacion_id INT NOT NULL,
    tipo VARCHAR(64) NOT NULL,  -- 'problema_persistente', 'accion_fallida', 'bloqueo_organizacional'
    categoria VARCHAR(100) NOT NULL,  -- Categoría NLP (ej. "sobrecarga laboral")
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    contexto_completo TEXT NOT NULL,  -- Resumen de la conversación completa
    recomendacion_rrhh TEXT NOT NULL,
    severidad VARCHAR(32) NOT NULL,  -- 'baja', 'media', 'alta', 'critica'
    departamento VARCHAR(80),
    equipo VARCHAR(80),
    estado VARCHAR(32) DEFAULT 'nuevo',  -- 'nuevo', 'revisado', 'en_accion', 'resuelto'
    revisado_por VARCHAR(50),  -- Usuario RRHH que lo revisó
    notas_rrhh TEXT,  -- Notas internas de RRHH
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (conversacion_id) REFERENCES conversaciones_agente(id) ON DELETE CASCADE,
    INDEX idx_tipo (tipo),
    INDEX idx_severidad (severidad),
    INDEX idx_estado (estado),
    INDEX idx_departamento (departamento),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.4 Frontend - Interfaz de Chat Pública

**Archivo:** `frontend/pages/chatAgente.py`

**URL:** http://localhost:8501 (integrado en app_publica.py)

**Características:**

1. **Interfaz de Chat**
   - Historial de mensajes (empleado + agente)
   - Campo de texto para respuestas
   - Indicador visual de nivel de riesgo
   - Contador de mensajes (máximo 6-8 intercambios)

2. **Flujo de Conversación**
   ```
   1. Empleado escribe mensaje inicial
   2. Sistema analiza con NLP (usa sistema existente)
   3. Agente decide si profundizar
   4. Si NO profundiza:
      - Muestra solo análisis + sugerencia
      - Guarda en sistema tradicional
   5. Si profundiza:
      - Inicia conversación guiada
      - Máximo 6-8 preguntas
      - Genera insight al final
   ```

3. **Privacidad**
   - Sin registro de identidad
   - Contexto opcional (departamento/equipo)
   - Advertencia de confidencialidad
   - Sesión temporal (no persistente)

4. **Diseño UX**
   ```
   ┌─────────────────────────────────────┐
   │  💬 Agente de Bienestar Laboral    │
   │  Conversación confidencial          │
   ├─────────────────────────────────────┤
   │                                     │
   │  [Usuario] Me siento estresado...   │
   │                                     │
   │  [Agente] ¿Ya intentaste hablar     │
   │          con tu supervisor?         │
   │                                     │
   │  [Usuario] Sí, pero no responde...  │
   │                                     │
   │  [Agente] ¿Cuánto tiempo llevas     │
   │          esperando respuesta?       │
   │                                     │
   ├─────────────────────────────────────┤
   │  Tu respuesta:                      │
   │  [_____________________________]    │
   │               [Enviar] [Finalizar]  │
   └─────────────────────────────────────┘
   ```

---

### 2.5 Frontend - Panel de Insights para RRHH

**Archivo:** `frontend/pages/insightsAgente.py`

**URL:** http://localhost:8502 (Panel RRHH, requiere login)

**Características:**

1. **Dashboard de Insights**
   - Total de insights generados
   - Distribución por tipo
   - Distribución por severidad
   - Insights pendientes de revisión

2. **Filtros**
   - Por tipo de insight
   - Por severidad
   - Por departamento
   - Por estado (nuevo, revisado, en acción, resuelto)
   - Por fecha

3. **Vista Detallada de Insight**
   ```
   ┌──────────────────────────────────────────┐
   │ 🔴 INSIGHT CRÍTICO                       │
   │ Tipo: Bloqueo Organizacional             │
   │ Categoría: Liderazgo                     │
   ├──────────────────────────────────────────┤
   │ Título:                                  │
   │ Supervisor no responde a solicitudes     │
   │ de reunión desde hace 2 meses           │
   │                                          │
   │ Contexto:                                │
   │ Empleado de Ventas reporta sobrecarga   │
   │ de trabajo. Ha intentado reunirse con   │
   │ su supervisor 5 veces sin éxito...      │
   │                                          │
   │ Conversación completa:                   │
   │ [Ver transcript de 6 mensajes]          │
   │                                          │
   │ Recomendación:                           │
   │ - Intervención inmediata de RRHH        │
   │ - Reunión con supervisor del área       │
   │ - Evaluar carga de trabajo del equipo   │
   │                                          │
   │ Departamento: Ventas                     │
   │ Equipo: Turno A                          │
   │ Fecha: 2025-01-15 10:30                  │
   │                                          │
   │ [Marcar como Revisado]                   │
   │ [Agregar Notas]                          │
   │ [Cambiar Estado] [Ver Conversación]     │
   └──────────────────────────────────────────┘
   ```

4. **Acciones sobre Insights**
   - Marcar como revisado
   - Agregar notas internas
   - Cambiar estado
   - Exportar conversación completa
   - Vincular con comentarios relacionados

5. **Analítica de Insights**
   - Tendencias de bloqueos por departamento
   - Problemas más persistentes
   - Acciones fallidas más comunes
   - Tiempo promedio de resolución

---

## 3. FLUJO COMPLETO DE INTERACCIÓN

### 3.1 Escenario 1: Empleado con estrés alto - Conversación profunda

```
1. EMPLEADO (chat público):
   "Me siento muy estresado con la carga de trabajo"

2. SISTEMA:
   - Análisis NLP: estrés=alto, emoción=tristeza, categoría=sobrecarga
   - Agente decide: requiere_seguimiento=true

3. AGENTE:
   "¿Ya intentaste hablar con tu supervisor sobre esto?"

4. EMPLEADO:
   "Sí, pero nunca tiene tiempo para reunirse"

5. SISTEMA:
   - Análisis: detecta bloqueo de liderazgo
   - Nivel de riesgo: aumenta a "crítico"

6. AGENTE:
   "¿Cuánto tiempo llevas intentando reunirte sin éxito?"

7. EMPLEADO:
   "Llevo 2 meses intentando"

8. SISTEMA:
   - Detecta: problema persistente + bloqueo organizacional
   - Genera INSIGHT para RRHH:
     * Tipo: bloqueo_organizacional
     * Severidad: alta
     * Descripción: "Empleado de Ventas sin acceso a supervisor por 2 meses"
     * Recomendación: "Intervención inmediata de RRHH con supervisor del área"

9. AGENTE:
   "Gracias por compartir. Tu situación será revisada de forma confidencial
   por el equipo de RRHH. ¿Hay algo más que quieras agregar?"

10. EMPLEADO:
    "No, gracias"

11. SISTEMA:
    - Cierra conversación
    - Insight disponible en panel RRHH
    - Empleado no ve el insight generado
```

### 3.2 Escenario 2: Empleado con estrés bajo - Sin seguimiento

```
1. EMPLEADO (chat público):
   "Me gusta mucho el ambiente de trabajo"

2. SISTEMA:
   - Análisis NLP: estrés=bajo, emoción=alegría, sentimiento=positivo
   - Agente decide: requiere_seguimiento=false

3. RESPUESTA:
   "¡Gracias por tu comentario positivo! Tu opinión ha sido registrada."

4. SISTEMA:
   - Guarda en sistema tradicional (tabla analisis_comentarios)
   - NO inicia conversación
   - NO genera insight adicional
```

### 3.3 Escenario 3: Acción fallida detectada

```
1. EMPLEADO:
   "Pedí nuevas herramientas hace 3 meses y nunca llegaron"

2. SISTEMA:
   - Análisis: categoría=recursos insuficientes, estrés=alto

3. AGENTE:
   "¿A quién reportaste esta necesidad?"

4. EMPLEADO:
   "A RRHH y a mi jefe"

5. AGENTE:
   "¿Te dieron alguna respuesta o seguimiento?"

6. EMPLEADO:
   "Dijeron que lo revisarían pero nunca más supe nada"

7. SISTEMA:
   - Detecta: acción_fallida (RRHH prometió seguimiento, nunca ocurrió)
   - Genera INSIGHT:
     * Tipo: accion_fallida
     * Severidad: media
     * Descripción: "Solicitud de recursos sin seguimiento por 3 meses"
     * Recomendación: "Revisar proceso de solicitud de recursos y dar seguimiento"
```

---

## 4. VALOR DIFERENCIAL DEL AGENTE

### 4.1 Lo que NO es el agente

❌ NO es un chatbot de consejos genéricos tipo:
   - "Intenta respirar profundo"
   - "Toma un descanso"
   - "Habla con tu jefe"

❌ NO es un reemplazo del sistema de análisis existente

❌ NO es un sistema de tickets o soporte técnico

### 4.2 Lo que SÍ es el agente

✅ **Sistema de detección de bloqueos organizacionales**
   - Identifica por qué los problemas NO se resuelven
   - Detecta cuando las recomendaciones de RRHH fallan

✅ **Generador de insights únicos**
   - Información que NO se obtiene de un comentario estático
   - Contexto profundo de situaciones complejas

✅ **Herramienta de diagnóstico organizacional**
   - Revela patrones de comunicación fallidos
   - Identifica cuellos de botella en procesos
   - Detecta liderazgo inefectivo

✅ **Sistema de escalamiento inteligente**
   - Prioriza casos críticos automáticamente
   - Genera recomendaciones accionables para RRHH

---

## 5. DIFERENCIACIÓN TÉCNICA

### Sistema tradicional de comentarios:

```
Comentario → Análisis NLP → Dashboard
```

**Limitación:** Solo captura el estado en un momento específico

### Sistema con Agente Autónomo:

```
Comentario → Análisis NLP → Agente decide profundizar →
  ↓
Conversación guiada (2-8 mensajes) →
  ↓
Análisis contextual acumulativo →
  ↓
Detección de bloqueos/patrones →
  ↓
Insight único para RRHH
```

**Ventaja:** Captura el contexto completo, historia del problema, acciones intentadas y por qué fallaron

---

## 6. MÉTRICAS DE ÉXITO DEL AGENTE

1. **Insights generados por semana**
   - Meta: 10-20 insights únicos por semana

2. **Tasa de detección de bloqueos**
   - Meta: >60% de conversaciones profundas generan al menos 1 insight

3. **Tasa de conversaciones profundas**
   - Meta: 30-40% de comentarios iniciales activan conversación

4. **Tiempo promedio de conversación**
   - Meta: 4-6 intercambios promedio

5. **Insights accionados por RRHH**
   - Meta: >80% de insights críticos revisados en <48h

---

## 7. ESTRATEGIAS DE PREGUNTAS DEL AGENTE

### Categoría: Sobrecarga laboral

**Preguntas tipo:**
1. "¿Ya intentaste hablar con tu supervisor sobre esto?"
2. "¿Cuánto tiempo llevas con esta carga de trabajo?"
3. "¿Qué tareas específicas te generan más presión?"
4. "¿Te han asignado recursos adicionales?"
5. "¿Has recibido respuesta de RRHH previamente sobre esto?"

### Categoría: Liderazgo

**Preguntas tipo:**
1. "¿Has intentado comunicarte con tu supervisor sobre esto?"
2. "¿Recibes retroalimentación regular de tu líder?"
3. "¿Cuánto tiempo llevas con esta situación?"
4. "¿Has escalado esto a RRHH antes?"

### Categoría: Recursos insuficientes

**Preguntas tipo:**
1. "¿Ya solicitaste estos recursos?"
2. "¿A quién reportaste esta necesidad?"
3. "¿Recibiste alguna respuesta o seguimiento?"
4. "¿Cuánto tiempo llevas esperando?"

### Categoría: Conflictos internos

**Preguntas tipo:**
1. "¿Has intentado resolver esto directamente con la persona?"
2. "¿Tu supervisor está al tanto de esta situación?"
3. "¿Cuánto tiempo lleva ocurriendo esto?"
4. "¿Afecta tu trabajo diario?"

---

## 8. LÓGICA DE DECISIÓN DEL AGENTE

### ¿Cuándo profundizar?

**Profundizar SI:**
- Estrés alto O emoción muy negativa (score >0.7)
- Categorías críticas: sobrecarga, liderazgo, conflictos
- Palabras clave de bloqueo: "nunca", "siempre", "meses", "nadie responde"
- Sentimiento negativo >0.6

**NO profundizar SI:**
- Estrés bajo + sentimiento positivo
- Comentario muy breve (<50 caracteres)
- No categoría crítica detectada

### ¿Cuándo cerrar conversación?

**Cerrar SI:**
- Se alcanzó máximo de preguntas (6-8)
- Se generó insight completo
- Empleado indica que no tiene más que agregar
- Empleado deja de responder (timeout)

### ¿Cuándo escalar?

**Escalar (insight crítico) SI:**
- Riesgo de seguridad/salud mental
- Acoso o discriminación mencionados
- Situación ilegal o ética grave
- Problema persistente >6 meses sin solución

---

## 9. IMPLEMENTACIÓN TÉCNICA

### Stack tecnológico (usa el existente):

- **Backend:** FastAPI (ya instalado)
- **IA/NLP:** Usa `NLPAnalyzer` existente
- **Base de datos:** MySQL (agregar 3 tablas nuevas)
- **Frontend:** Streamlit (agregar 2 páginas nuevas)

### Dependencias nuevas: NINGUNA

Todo usa las librerías ya instaladas:
- `transformers` para NLP
- `sqlalchemy` para base de datos
- `streamlit` para interfaz
- `plotly` para visualizaciones de insights

---

## 10. PLAN DE IMPLEMENTACIÓN

### Fase 1: Backend (Día 1)
1. Crear módulo `ia/iaAgent.py`
2. Crear script SQL para 3 tablas nuevas
3. Crear modelos ORM en `core/coreModels.py`
4. Crear endpoint `api/agente.py`

### Fase 2: Frontend Público (Día 1-2)
1. Crear página `pages/chatAgente.py`
2. Integrar en `app_publica.py`
3. Testing de flujo de conversación

### Fase 3: Frontend RRHH (Día 2)
1. Crear página `pages/insightsAgente.py`
2. Integrar en `app_rrhh.py`
3. Dashboard de insights

### Fase 4: Testing y Ajustes (Día 2-3)
1. Probar escenarios completos
2. Ajustar estrategias de preguntas
3. Validar generación de insights

---

## 11. RESTRICCIONES RESPETADAS

✅ **No modifica código existente**
   - Solo AGREGA nuevos módulos
   - No cambia `iaCore.py`, `analizarComentario.py`, etc.

✅ **Usa análisis NLP existente**
   - Reutiliza `NLPAnalyzer` completamente
   - No entrena modelos nuevos

✅ **Mantiene anonimato**
   - Sin identificación de usuario
   - Solo contexto opcional (departamento/equipo)

✅ **No es chatbot genérico**
   - Preguntas específicas basadas en análisis
   - Enfocado en detectar bloqueos

✅ **Valor agregado claro**
   - Insights únicos que comentarios estáticos no generan
   - Información accionable para RRHH

---

Este documento define la arquitectura completa del Agente Autónomo de Bienestar Laboral, listo para implementación en el proyecto NovaMind.
