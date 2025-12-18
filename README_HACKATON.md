# NovaMind - Sistema Inteligente de Bienestar Laboral con Agente Autónomo


** Proyecto para Hackatón - Extensión con Agente Autónomo**


---

## Resumen Ejecutivo

**NovaMind** es un sistema de análisis de clima organizacional basado en IA que combina:

1. **Sistema base (YA implementado):** Análisis NLP avanzado de comentarios de empleados con detección de emociones, estrés y categorización automática.

2. **Extensión para Hackatón (NUEVO):** Agente Autónomo de Bienestar Laboral que **NO es un chatbot genérico**, sino un sistema de detección de bloqueos organizacionales que revela información única a través de conversaciones guiadas.

---

##  Problema que Resuelve

### Problema Principal
Las empresas enfrentan problemas de clima laboral, estrés y rotación de personal, pero **carecen de herramientas para entender las causas raíz**:

- Cajas de sugerencias tradicionales: comentarios estáticos sin contexto
-  Encuestas de clima: respuestas superficiales por miedo
- Chatbots genéricos: consejos de autoayuda que no resuelven problemas organizacionales
-  Reuniones 1:1: sesgadas por presencia de liderazgo

### Solución NovaMind
 -Análisis automático de sentimiento y estrés con IA
 -Confidencialidad y anonimato total
 -**Agente autónomo que detecta bloqueos organizacionales a través de conversaciones profundas**
 -Insights accionables únicos para RRHH

---

##  Funcionalidades Pre-Existentes

>  **IMPORTANTE:** Las siguientes funcionalidades **YA ESTABAN IMPLEMENTADAS** antes de la hackatón.
> Representan la base sólida sobre la cual se construyó el Agente Autónomo.

### 1. Análisis NLP Avanzado (Sistema Base)

**Modelos de IA Utilizados:**

| Función | Modelo | Descripción |
|---------|--------|-------------|
| **Sentimiento** | `pysentimiento/robertuito-sentiment-analysis` | Detecta sentimiento positivo/negativo/neutral |
| **Emociones** | `finiteautomata/beto-emotion-analysis` | Identifica 6 emociones: alegría, tristeza, enojo, miedo, asco, sorpresa |
| **Categorización** | `Recognai/bert-base-spanish-wwm-cased-xnli` | Clasifica en 14 categorías sin entrenamiento previo (zero-shot) |
| **Resumen** | `mrm8488/bert2bert_shared-spanish-finetuned-summarization` | Genera resúmenes automáticos de comentarios |

**Categorías de Análisis (14):**
- Sobrecarga laboral
- Liderazgo
- Comunicación
- Reconocimiento
- Remuneración
- Equilibrio vida-trabajo
- Ambiente laboral
- Procesos
- Tecnología/herramientas
- Conflictos internos
- Recursos insuficientes
- Formación/capacitación
- Satisfacción general
- Motivación

### 2. Sistema de Sugerencias Inteligentes

Para cada comentario, el sistema genera sugerencias personalizadas considerando:
- Nivel de estrés (alto/medio/bajo)
- Emoción detectada
- Categorías identificadas
- Palabras clave específicas (jefe, salario, herramientas, conflicto, tiempo, etc.)

**Ejemplos de sugerencias:**

| Caso | Sugerencia |
|------|------------|
| Estrés alto + sobrecarga | "Reunión inmediata para revisar carga laboral y redistribuir tareas" |
| Problema con liderazgo | "Reunión con supervisor para revisar expectativas y comunicación" |
| Falta de recursos | "Revisar disponibilidad de herramientas. Evaluar apoyo temporal" |
| Conflicto interno | "Intervención de RRHH para resolver conflictos" |

### 3. Dashboard de RRHH

**KPIs principales:**
- Total de comentarios analizados
- Porcentaje de estrés alto
- Porcentaje de sentimiento positivo
- Categoría principal

**Visualizaciones:**
- Distribución de niveles de estrés (gráfico circular)
- Emociones detectadas (gráfico de barras)
- Top 5 categorías más frecuentes
- Comentarios y estrés por departamento
- Tendencias temporales (últimos 30 días)
- WordClouds de palabras frecuentes
- Tabla de comentarios recientes

### 4. Sistema de Alertas Automáticas

**Detección de patrones críticos:**

| Patrón | Condición | Acción Recomendada |
|--------|-----------|---------------------|
| Estrés crítico | >30% comentarios con estrés alto | Intervención inmediata requerida |
| Tendencia creciente | 15+ alertas en últimos 20 comentarios | Análisis profundo de causas |
| Departamento crítico | >50% de estrés alto en un departamento | Reunión urgente con liderazgo |
| Clima negativo | >40% de emociones negativas | Sesión de feedback con equipo |

### 5. Análisis Masivo (CSV)

- Carga de múltiples comentarios desde archivo CSV
- Procesamiento batch con barra de progreso
- Validación automática de formato
- Descarga de plantilla CSV de ejemplo

### 6. Análisis por Departamento y Equipo

- Filtrado avanzado por departamento, equipo, fecha
- Comparativas entre áreas
- Identificación de departamentos críticos
- Top 3 categorías por departamento

---

##  Nueva Extensión: Agente Autónomo (Hackatón)

>  **NUEVA IMPLEMENTACIÓN PARA LA HACKATÓN**
>
> Esta es la extensión que agrega valor diferencial al sistema existente.

### ¿Qué es el Agente Autónomo?

**NO es:**
-  Un chatbot de consejos genéricos ("intenta respirar profundo", "toma un descanso")
-  Un reemplazo del sistema de análisis existente
-  Un sistema de tickets o soporte técnico

**SÍ es:**
-  **Sistema de detección de bloqueos organizacionales**
-  **Generador de insights únicos** que NO se obtienen de comentarios estáticos
-  **Herramienta de diagnóstico organizacional** que revela por qué los problemas NO se resuelven
-  **Sistema de escalamiento inteligente** que prioriza casos críticos automáticamente

### Funcionamiento del Agente

#### 1. Análisis Inicial y Decisión Autónoma

El agente analiza el comentario inicial usando el **sistema NLP existente** y decide autónomamente si profundizar:

**Profundiza SI:**
- Estrés alto (>70% sentimiento negativo)
- Emoción muy negativa (score >0.75)
- Categorías críticas detectadas: sobrecarga, liderazgo, conflictos
- Palabras clave de bloqueo: "nunca", "siempre", "meses", "nadie responde"
- Palabras de persistencia: "otra vez", "de nuevo", "sigue", "todavía"

**NO profundiza SI:**
- Estrés bajo + sentimiento positivo
- Comentario muy breve (<50 caracteres)
- Sin categorías críticas

#### 2. Conversación Guiada (NO Genérica)

Las preguntas del agente son **específicas según el contexto**:

**Ejemplo - Sobrecarga laboral:**
1. "¿Ya intentaste hablar con tu supervisor sobre esta carga de trabajo?"
2. "¿Cuánto tiempo llevas con esta sobrecarga?"
3. "¿Qué tareas específicas te generan más presión?"
4. "¿Te han asignado recursos o apoyo adicional?"
5. "¿Has recibido alguna respuesta de RRHH previamente sobre esto?"

**Ejemplo - Liderazgo:**
1. "¿Has intentado comunicarte con tu supervisor sobre esto?"
2. "¿Con qué frecuencia recibes retroalimentación de tu líder?"
3. "¿Cuánto tiempo llevas con esta situación?"
4. "¿Tu líder está al tanto de cómo te sientes?"
5. "¿Has escalado esto a RRHH antes?"

#### 3. Detección de Bloqueos Organizacionales

El agente identifica **4 tipos de bloqueos**:

| Tipo de Bloqueo | Indicadores | Ejemplo |
|-----------------|-------------|---------|
| **Liderazgo** | "no responde", "nunca tiene tiempo", "ignora" | Supervisor inaccesible por 2 meses |
| **Recursos** | "nunca llegó", "prometieron pero", "no cumplieron" | Herramientas solicitadas hace 3 meses sin entrega |
| **Proceso** | "mucha burocracia", "nadie se hace cargo" | Solicitud rebota entre departamentos |
| **Cultural** | "así es aquí", "siempre ha sido así", "todo el equipo" | Problema sistémico generalizado |

#### 4. Generación de Insights Únicos

El agente genera **3 tipos de insights** que NO se obtienen de comentarios estáticos:

##### A. Problema Persistente
```
Tipo: problema_persistente
Descripción: Empleado reporta problema que persiste >3 meses sin resolución
Contexto: Ha intentado hablar con supervisor 5 veces sin éxito
Recomendación: Seguimiento inmediato + asignar responsable con fecha límite
```

##### B. Acción Fallida
```
Tipo: accion_fallida
Descripción: RRHH prometió seguimiento hace 2 meses que nunca ocurrió
Contexto: Empleado solicitó cambio de equipo, nunca recibió respuesta
Recomendación: Revisar proceso de seguimiento + dar respuesta inmediata
```

##### C. Bloqueo Organizacional
```
Tipo: bloqueo_organizacional
Descripción: Supervisor no responde a solicitudes de reunión desde hace 2 meses
Contexto: Empleado de Ventas con sobrecarga, 5 intentos fallidos de contacto
Recomendación: Intervención inmediata de RRHH + reunión con supervisor del área
```

### Flujo Completo de Ejemplo

**Escenario Real:**

```
1. EMPLEADO (chat):
   "Me siento muy estresado con la carga de trabajo"

2. SISTEMA:
   - Análisis NLP: estrés=alto, emoción=tristeza (0.85), categoría=sobrecarga
   - Agente decide: requiere_seguimiento=TRUE
   - Nivel de riesgo: ALTO

3. AGENTE:
   "¿Ya intentaste hablar con tu supervisor sobre esto?"

4. EMPLEADO:
   "Sí, pero nunca tiene tiempo para reunirse"

5. SISTEMA:
   - Análisis: detecta bloqueo de LIDERAZGO
   - Nivel de riesgo: aumenta a CRÍTICO
   - Estrategia: profundizar en el bloqueo

6. AGENTE:
   "¿Cuánto tiempo llevas intentando reunirte sin éxito?"

7. EMPLEADO:
   "Llevo 2 meses intentando"

8. SISTEMA:
   - Detecta: PROBLEMA PERSISTENTE + BLOQUEO ORGANIZACIONAL
   - Genera INSIGHT para RRHH:
     * Tipo: bloqueo_organizacional
     * Severidad: ALTA
     * Título: "Supervisor inaccesible por 2 meses"
     * Descripción: "Empleado de Ventas sin acceso a supervisor"
     * Recomendación: "Intervención inmediata de RRHH con supervisor"
     * Evidencias: ["Sí, pero nunca tiene tiempo", "Llevo 2 meses intentando"]

9. AGENTE:
   "Gracias por compartir. Tu situación será revisada de forma confidencial."

10. RRHH (Panel privado):
    - Ve insight crítico nuevo
    - Tiene contexto completo de conversación
    - Puede tomar acción específica basada en evidencia
    - Insight NO visible para el empleado
```

---

##  Valor Diferencial

### Comparación: Sistema Tradicional vs. NovaMind con Agente

| Aspecto | Caja de Sugerencias Tradicional | Chatbot Genérico | **NovaMind + Agente Autónomo** |
|---------|--------------------------------|------------------|-------------------------------|
| **Análisis de texto** | Manual por RRHH | Básico (keywords) |  NLP avanzado con Transformers |
| **Detección de emociones** | No | No |  6 emociones con scores |
| **Nivel de estrés** | Subjetivo | No |  Automático basado en sentimiento |
| **Categorización** | Manual | Reglas fijas |  Zero-shot learning (14 categorías) |
| **Conversaciones profundas** | No | Sí (genéricas) |  Sí (guiadas por contexto NLP) |
| **Detección de bloqueos** | No | No |  **4 tipos de bloqueos organizacionales** |
| **Insights únicos** | No | No |  **Problema persistente, acción fallida, bloqueo** |
| **Seguimiento de casos** | Manual | No |  Automático con evidencias |
| **Escalamiento inteligente** | Manual | No |  Automático según nivel de riesgo |
| **Anonimato** | Sí | Variable |  Total (sin login, sin tracking) |

### ¿Por qué NO es un Chatbot Genérico?

**Chatbot Genérico:**
```
Empleado: "Estoy estresado"
Bot: "Intenta respirar profundo y tomar descansos"
```
 Consejo de autoayuda sin valor organizacional

**Agente Autónomo de NovaMind:**
```
Empleado: "Estoy estresado con la carga de trabajo"
Agente: [Análisis NLP] → estrés=alto, categoría=sobrecarga
Agente: "¿Ya intentaste hablar con tu supervisor sobre esto?"
Empleado: "Sí, pero nunca responde"
Agente: [Detecta bloqueo de liderazgo] → Genera insight crítico para RRHH
```
 Detecta que el problema NO es el estrés del empleado, sino un **supervisor inaccesible** (bloqueo organizacional)

### ¿Qué Información Única Genera el Agente?

| Lo que un comentario estático revela | Lo que el agente descubre |
|--------------------------------------|---------------------------|
| "Estoy estresado" | **Por qué** está estresado (carga, liderazgo, recursos) |
| "Tengo mucho trabajo" | **Cuánto tiempo** lleva así + si **intentó resolverlo** |
| "Mi jefe no me apoya" | Si el jefe **no responde** o **no tiene tiempo** → Bloqueo |
| "Necesito herramientas" | Si **ya las pidió**, a **quién**, si **prometieron** entregarlas |
| "Hay un problema" | Si el problema **persiste** + **por qué NO se resuelve** |

---

##  Arquitectura Técnica

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Streamlit)                    │
├──────────────────────────────┬──────────────────────────────┤
│   APP PÚBLICA (Puerto 8501)  │  APP RRHH (Puerto 8502)      │
│   ┌────────────────────────┐ │  ┌──────────────────────────┐│
│   │ Formulario Tradicional │ │  │ Dashboard General        ││
│   │ (comentarios estáticos)│ │  │ Análisis Individual      ││
│   └────────────────────────┘ │  │ Insights del Agente    ││
│   ┌────────────────────────┐ │  │ Análisis CSV             ││
│   │ Chat del Agente      │ │  │ Alertas y Patrones       ││
│   │ (conversación guiada)  │ │  │ Configuración            ││
│   └────────────────────────┘ │  └──────────────────────────┘│
└──────────────────────────────┴──────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                     │
│                      Puerto 8000                             │
├─────────────────────────────────────────────────────────────┤
│  ENDPOINTS EXISTENTES        │  ENDPOINTS NUEVOS           │
│  ├─ /analizar-comentario/    │  ├─ /agente/iniciar/         │
│  ├─ /analizar-lote/          │  ├─ /agente/responder/       │
│  ├─ /historicos/             │  ├─ /agente/conversacion/:id/│
│  ├─ /alertas/                │  ├─ /agente/insights/        │
│  ├─ /estadisticas/           │  ├─ /agente/insights/estadist│
│  └─ /login/                  │  └─ /agente/insights/:id/    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE INTELIGENCIA ARTIFICIAL            │
├─────────────────────────────────────────────────────────────┤
│  MÓDULOS EXISTENTES          │  MÓDULO NUEVO             │
│  ├─ iaCore.py (NLPAnalyzer)  │  ├─ iaAgent.py               │
│  │  ├─ Análisis de emoción   │  │  ├─ AgenteAutonomo        │
│  │  ├─ Análisis de estrés    │  │  ├─ DetectorBloqueos      │
│  │  ├─ Categorización        │  │  ├─ GeneradorInsights     │
│  │  ├─ Resumen automático    │  │  └─ EstrategiasPreguntas  │
│  │  └─ Sugerencias           │  │                            │
│  ├─ configIA.py              │  │  (Usa NLPAnalyzer          │
│  └─ preProcesamiento.py      │  │   existente)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   BASE DE DATOS (MySQL)                      │
├─────────────────────────────────────────────────────────────┤
│  TABLAS EXISTENTES           │  TABLAS NUEVAS             │
│  ├─ analisis_comentarios     │  ├─ conversaciones_agente    │
│  └─ usuarios_rrhh            │  ├─ mensajes_agente          │
│                              │  └─ insights_agente           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               MODELOS DE IA (HuggingFace Transformers)       │
├─────────────────────────────────────────────────────────────┤
│   pysentimiento/robertuito-sentiment-analysis              │
│   finiteautomata/beto-emotion-analysis                     │
│   Recognai/bert-base-spanish-wwm-cased-xnli                │
│   mrm8488/bert2bert_shared-spanish-finetuned-summarization │
└─────────────────────────────────────────────────────────────┘
```

### Modelos ORM (SQLAlchemy)

**Tablas Existentes:**
- `AnalisisComentario`: Almacena comentarios analizados con NLP
- `UsuarioRRHH`: Usuarios con acceso al panel de RRHH

**Tablas Nuevas (Agente):**
- `ConversacionAgente`: Registro de cada conversación con el agente
- `MensajeAgente`: Cada mensaje individual (empleado + agente)
- `InsightAgente`: Insights generados para RRHH

### Flujo de Datos Completo

```
1. EMPLEADO → Elige entre:
   ├─ Comentario rápido (formulario tradicional)
   └─ Conversación con agente (chat)

2. SISTEMA → Análisis NLP (SIEMPRE)
   ├─ Detección de emoción
   ├─ Análisis de estrés
   ├─ Categorización (14 categorías)
   └─ Generación de sugerencia base

3. AGENTE → Decisión autónoma
   ├─ Si NO profundiza: guarda como comentario tradicional
   └─ Si profundiza: inicia conversación guiada

4. CONVERSACIÓN → (si se activó)
   ├─ Pregunta contextual según categoría
   ├─ Análisis de cada respuesta
   ├─ Detección de bloqueos
   ├─ Actualización de nivel de riesgo
   └─ Cierre + generación de insight

5. INSIGHT → (generado por agente)
   ├─ Tipo: bloqueo, persistente, acción_fallida
   ├─ Evidencias de la conversación
   ├─ Recomendación específica para RRHH
   └─ Estado: nuevo, revisado, en_acción, resuelto

6. RRHH → Panel de insights
   ├─ Dashboard con estadísticas
   ├─ Lista filtrable de insights
   ├─ Detalle de cada insight con conversación completa
   ├─ Actualización de estado
   └─ Notas internas
```

---

##  Instalación y Uso

### Prerrequisitos

- Python 3.9+
- MySQL 5.7+
- 4GB RAM mínimo (para modelos de IA)
- Navegador web moderno

### Instalación Paso a Paso

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/novamind.git
cd novamind
```

#### 2. Crear Entorno Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

#### 4. Configurar Base de Datos

```bash
# Crear base de datos
mysql -u root -p
CREATE DATABASE novamind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Ejecutar scripts SQL
mysql -u root -p novamind < database/schema.sql
mysql -u root -p novamind < database/schema_agente.sql
mysql -u root -p novamind < database/usuarios.sql
mysql -u root -p novamind < database/datos_prueba.sql  # (opcional)
```

#### 5. Configurar Variables de Entorno

Crear archivo `backend/config/.env`:

```env
# Base de datos
DATABASE_URL=mysql+pymysql://root:password@localhost/novamind

# Configuración de la app
APP_NAME=NovaMind API
CORS_ORIGINS=["http://localhost:8501","http://localhost:8502"]
```

#### 6. Iniciar los Servicios

**Terminal 1 - Backend API:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - App Pública:**
```bash
cd frontend
streamlit run app_publica.py --server.port 8501
```

**Terminal 3 - Panel RRHH:**
```bash
cd frontend
streamlit run app_rrhh.py --server.port 8502
```

### Acceso a las Aplicaciones

| Aplicación | URL | Credenciales |
|------------|-----|--------------|
| **App Pública** | http://localhost:8501 | No requiere login |
| **Panel RRHH** | http://localhost:8502 | Usuario: `admin` / Password: `admin123` |
| **API Docs** | http://localhost:8000/docs | - |

---

## 📱 Casos de Uso

### Caso 1: Comentario Positivo (Sin Seguimiento)

```
Empleado: "Me gusta mucho el ambiente de trabajo"

Sistema:
- Análisis: estrés=bajo, emoción=alegría, sentimiento=positivo
- Agente: NO profundiza (no requiere seguimiento)
- Resultado: Comentario guardado en sistema tradicional

RRHH:
- Ve comentario positivo en dashboard general
- No genera insight adicional
```v

### Caso 2: Problema con Liderazgo (Conversación Profunda)

```
Empleado: "Mi jefe nunca me da retroalimentación"

Sistema:
- Análisis: estrés=alto, emoción=tristeza, categoría=liderazgo
- Agente: SÍ profundiza

Agente: "¿Has intentado solicitar reuniones 1:1?"
Empleado: "Sí, pero siempre las cancela"

Agente: "¿Cuánto tiempo llevas sin reunión con tu líder?"
Empleado: "3 meses"

Sistema:
- Detecta: BLOQUEO DE LIDERAZGO (supervisor inaccesible)
- Genera INSIGHT crítico para RRHH:
  * Tipo: bloqueo_organizacional
  * Severidad: alta
  * Título: "Líder cancela reuniones sistemáticamente"
  * Recomendación: "Intervención RRHH + reunión con líder directo"

RRHH:
- Ve insight crítico nuevo en panel
- Accede a conversación completa
- Toma acción específica
```

### Caso 3: Acción Fallida de RRHH

```
Empleado: "Solicité un cambio de equipo hace 4 meses y nadie me responde"

Agente: "¿A quién reportaste esta solicitud?"
Empleado: "A RRHH por email"

Agente: "¿Recibiste alguna respuesta inicial?"
Empleado: "Dijeron que lo revisarían, pero nunca más supe nada"

Sistema:
- Detecta: ACCIÓN FALLIDA (RRHH no dio seguimiento)
- Genera INSIGHT para RRHH:
  * Tipo: accion_fallida
  * Severidad: media
  * Título: "Solicitud de cambio sin seguimiento por 4 meses"
  * Recomendación: "Revisar proceso de solicitudes + dar respuesta inmediata"
  * Evidencias: ["Dijeron que lo revisarían pero nunca más supe nada"]

RRHH:
- Identifica fallo en proceso interno
- Toma acción correctiva
- Mejora sistema de seguimiento
```

---

## 🛠️ Tecnologías

### Backend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **FastAPI** | 0.115.5 | Framework API REST asíncrono |
| **SQLAlchemy** | 2.0.36 | ORM para base de datos |
| **Pydantic** | 2.9.2 | Validación de datos |
| **Transformers** | 4.45.2 | Modelos de IA (HuggingFace) |
| **PyTorch** | 2.2.0+ | Framework de deep learning |
| **PyMySQL** | 1.1.1 | Driver MySQL |
| **bcrypt** | 4.1.2 | Hashing de contraseñas |

### Frontend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Streamlit** | 1.38.0 | Framework web interactivo |
| **Pandas** | 2.2.2 | Manipulación de datos |
| **Plotly** | 5.24.0 | Visualizaciones interactivas |
| **Requests** | 2.32.3 | Cliente HTTP para API |

### Base de Datos

| Tecnología | Uso |
|------------|-----|
| **MySQL** | Base de datos relacional (5.7+) |
| **utf8mb4** | Soporte Unicode completo |
| **InnoDB** | Transacciones ACID |

### Modelos de IA (HuggingFace)

| Modelo | Tarea | Idioma |
|--------|-------|--------|
| `pysentimiento/robertuito-sentiment-analysis` | Análisis de sentimiento | Español |
| `finiteautomata/beto-emotion-analysis` | Detección de emociones | Español |
| `Recognai/bert-base-spanish-wwm-cased-xnli` | Clasificación zero-shot | Español |
| `mrm8488/bert2bert_shared-spanish-finetuned-summarization` | Resumen automático | Español |

---

## 📊 Métricas de Éxito del Agente

### KPIs Implementados

1. **Tasa de Activación del Agente**
   - Meta: 30-40% de comentarios activan conversación profunda
   - Medida: conversaciones_activas / total_comentarios

2. **Insights Generados**
   - Meta: 10-20 insights únicos por semana
   - Tipos: bloqueo (60%), persistente (30%), acción_fallida (10%)

3. **Tasa de Detección de Bloqueos**
   - Meta: >60% de conversaciones profundas generan al menos 1 insight
   - Medida: conversaciones_con_insight / conversaciones_totales

4. **Tiempo Promedio de Conversación**
   - Meta: 4-6 intercambios (preguntas/respuestas)
   - Medida: promedio(num_mensajes_por_conversacion)

5. **Insights Accionados por RRHH**
   - Meta: >80% de insights críticos revisados en <48h
   - Estados: nuevo → revisado → en_acción → resuelto

---

## 🔐 Privacidad y Seguridad

### Anonimato Total

- ✅ No se solicita nombre, email o identificación del empleado
- ✅ No hay tracking de IP o cookies de identificación
- ✅ Contexto opcional (departamento/equipo) para análisis agregado
- ✅ Sesiones de conversación temporales (no persistentes en cliente)

### Acceso a Información

| Dato | Empleado | RRHH |
|------|----------|------|
| Comentario/conversación propia | ✅ Durante sesión | ❌ Sin identificación |
| Análisis NLP | ❌ No | ✅ Agregado + individual anónimo |
| Insights generados | ❌ No | ✅ Solo RRHH (con autenticación) |
| Conversación completa | ❌ No | ✅ Solo RRHH (anónima) |
| Dashboard y estadísticas | ❌ No | ✅ Solo RRHH |

### Seguridad del Panel RRHH

- Autenticación con usuario/contraseña
- Passwords hasheados con bcrypt
- Sesión con estado en servidor
- Logout seguro

---

## 🎓 Aprendizajes y Mejoras Futuras

### Lo que Aprendimos en la Hackatón

1. **IA Conversacional ≠ Chatbot Genérico**
   - La clave es usar el análisis NLP para guiar preguntas contextuales
   - Las conversaciones deben tener un propósito: detectar bloqueos

2. **Valor de los Insights Únicos**
   - Un comentario estático dice "hay un problema"
   - Una conversación guiada revela "por qué el problema NO se resuelve"

3. **Anonimato + Profundidad**
   - Es posible mantener anonimato total y obtener información valiosa
   - El agente no necesita saber quién eres para ayudarte

### Roadmap Futuro

1. **Análisis Predictivo**
   - Predecir rotación de personal basado en patrones de estrés
   - Alertas tempranas de burnout

2. **Recomendaciones Automáticas**
   - Sistema de tickets automático desde insights críticos
   - Asignación inteligente de casos a líderes

3. **Análisis de Sentimiento en Tiempo Real**
   - Dashboard en vivo de clima organizacional
   - Alertas push para RRHH

4. **Multilingüe**
   - Soporte para inglés, portugués, francés
   - Modelos multilingües de Transformers

5. **Integración con Slack/Teams**
   - Bot directo en plataformas corporativas
   - Notificaciones automáticas

---

## 👥 Equipo y Créditos

### Equipo de Desarrollo

- **Desarrollador Principal**: [Tu nombre]
- **Especialista en IA/NLP**: [Nombre]
- **Arquitecto de Software**: [Nombre]

### Agradecimientos

- HuggingFace por los modelos Transformer en español
- FastAPI y Streamlit por frameworks excepcionales
- Comunidad open-source de Python

### Licencia

Este proyecto está bajo licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto

- **Email**: tu-email@ejemplo.com
- **GitHub**: https://github.com/tu-usuario/novamind
- **LinkedIn**: https://linkedin.com/in/tu-perfil

---

<div align="center">

**🏆 Hecho con 💙 para la Hackatón**

⭐ Si te gustó este proyecto, dale una estrella en GitHub ⭐

</div>
