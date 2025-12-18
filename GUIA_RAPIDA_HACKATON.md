# 🚀 Guía Rápida - NovaMind con Agente Autónomo

## ⚡ Inicio Rápido (5 minutos)

### Paso 1: Configurar Base de Datos

```bash
# Entrar a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE novamind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Ejecutar scripts SQL en orden
cd database
mysql -u root -p novamind < schema.sql
mysql -u root -p novamind < schema_agente.sql
mysql -u root -p novamind < usuarios.sql
mysql -u root -p novamind < datos_prueba.sql  # Opcional: datos de ejemplo
```

### Paso 2: Instalar Dependencias

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### Paso 3: Iniciar Servicios (3 terminales)

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

### Paso 4: Acceder a las Aplicaciones

| App | URL | Login |
|-----|-----|-------|
| **App Pública** | http://localhost:8501 | No requiere |
| **Panel RRHH** | http://localhost:8502 | `admin` / `admin123` |
| **API Docs** | http://localhost:8000/docs | - |

---

## 🎯 Pruebas del Agente Autónomo

### Prueba 1: Comentario Positivo (Sin Seguimiento)

1. Ir a http://localhost:8501
2. Seleccionar tab "💬 Conversación con el agente"
3. Escribir: **"Me gusta mucho el ambiente de trabajo"**
4. Departamento: Ventas
5. Enviar

**Resultado esperado:**
- El agente NO profundiza (estrés bajo, sentimiento positivo)
- Muestra confirmación y cierra
- No genera insight adicional

---

### Prueba 2: Bloqueo de Liderazgo (Conversación Profunda)

1. Ir a http://localhost:8501
2. Seleccionar tab "💬 Conversación con el agente"
3. Escribir: **"Me siento muy estresado con la carga de trabajo"**
4. Departamento: Ventas
5. Enviar

**Conversación esperada:**
```
Agente: "¿Ya intentaste hablar con tu supervisor sobre esta carga de trabajo?"
Tú: "Sí, pero nunca tiene tiempo para reunirse"

Agente: "¿Cuánto tiempo llevas intentando reunirte sin éxito?"
Tú: "Llevo 2 meses intentando"

Agente: [Cierra conversación]
```

**Resultado esperado:**
- El agente profundiza (estrés alto detectado)
- Hace 2-3 preguntas guiadas
- Detecta BLOQUEO DE LIDERAZGO
- Genera INSIGHT para RRHH con:
  - Tipo: bloqueo_organizacional
  - Severidad: alta
  - Evidencias de la conversación
  - Recomendación específica

6. **Ir al Panel RRHH:**
   - Login: `admin` / `admin123`
   - Ir a **"Insights del Agente"**
   - Ver dashboard con insights generados
   - Ver detalle del insight crítico
   - Ver conversación completa

---

### Prueba 3: Acción Fallida de RRHH

1. App Pública → Chat del Agente
2. Escribir: **"Solicité nuevas herramientas hace 3 meses y nunca llegaron"**
3. Departamento: IT

**Conversación esperada:**
```
Agente: "¿A quién reportaste esta necesidad?"
Tú: "A RRHH por email"

Agente: "¿Recibiste alguna respuesta o seguimiento?"
Tú: "Dijeron que lo revisarían pero nunca más supe nada"
```

**Resultado esperado:**
- Tipo: accion_fallida
- Severidad: media
- Detecta que RRHH no dio seguimiento
- Genera recomendación para mejorar proceso

---

### Prueba 4: Problema Persistente

1. App Pública → Chat del Agente
2. Escribir: **"Sigo sin poder acceder al sistema de reportes"**
3. Departamento: Operaciones

**Conversación esperada:**
```
Agente: "¿Ya solicitaste estos recursos o herramientas?"
Tú: "Sí, hace 4 meses"

Agente: "¿Cuánto tiempo llevas esperando?"
Tú: "4 meses y sigue sin funcionar"
```

**Resultado esperado:**
- Tipo: problema_persistente
- Detecta que el problema lleva >3 meses
- Genera recomendación de seguimiento urgente

---

## 📊 Verificar Funcionalidad Completa

### En el Panel de RRHH (http://localhost:8502)

#### 1. Dashboard General (Original)
- ✅ KPIs: Total comentarios, % estrés alto, % sentimiento positivo
- ✅ Gráficos: distribución de estrés, emociones, categorías
- ✅ WordCloud de palabras frecuentes
- ✅ Tendencias temporales

#### 2. Insights del Agente (NUEVO ⭐)
- ✅ Dashboard de insights con KPIs:
  - Total insights
  - Nuevos sin revisar
  - Críticos
  - Bloqueos organizacionales
- ✅ Gráficos:
  - Distribución por tipo
  - Distribución por severidad
  - Insights por departamento
- ✅ Lista filtrable de insights:
  - Filtrar por tipo, severidad, estado, departamento
  - Ver detalle completo de cada insight
  - Ver conversación completa
  - Evidencias extraídas
  - Recomendación para RRHH
- ✅ Actualización de insights:
  - Cambiar estado (nuevo → revisado → en_acción → resuelto)
  - Agregar notas internas
  - Marcar como revisado por usuario RRHH

#### 3. Conversaciones del Agente (NUEVO ⭐)
- ✅ Lista de conversaciones con filtros
- ✅ Ver detalles completos de conversación
- ✅ Nivel de riesgo visual (🔴🟠🟡🟢)

---

## 🔍 Verificar Endpoints API

Ir a: http://localhost:8000/docs

### Endpoints Nuevos del Agente (⭐):

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/agente/iniciar/` | Inicia conversación con agente |
| POST | `/agente/responder/` | Procesa respuesta del empleado |
| GET | `/agente/conversacion/{id}/` | Obtiene historial de conversación |
| GET | `/agente/insights/` | Lista insights con filtros |
| GET | `/agente/insights/estadisticas/` | Estadísticas de insights |
| PATCH | `/agente/insights/{id}/` | Actualiza estado de insight |
| GET | `/agente/conversaciones/` | Lista conversaciones |

### Probar desde Swagger UI:

#### Test 1: Iniciar Conversación
```json
POST /agente/iniciar/
{
  "mensaje": "Me siento muy estresado con mi jefe",
  "meta": {
    "departamento": "Ventas",
    "equipo": "Equipo A"
  }
}
```

**Response esperado:**
```json
{
  "conversacion_id": 1,
  "requiere_seguimiento": true,
  "pregunta": "¿Has intentado comunicarte con tu supervisor sobre esto?",
  "nivel_riesgo": "alto",
  "razon_seguimiento": "Estrés alto detectado - requiere seguimiento"
}
```

#### Test 2: Obtener Insights
```json
GET /agente/insights/?severidad=alta&limite=10
```

---

## 📁 Estructura de Archivos Nuevos (Agente)

```
backend/
├── ia/
│   └── iaAgent.py ⭐ NUEVO - Lógica del agente autónomo
├── api/
│   └── agente.py ⭐ NUEVO - Endpoints del agente
└── core/
    └── coreModels.py (MODIFICADO - +3 modelos ORM)

frontend/
├── pages/
│   ├── chatAgente.py ⭐ NUEVO - Interfaz chat pública
│   └── insightsAgente.py ⭐ NUEVO - Panel insights RRHH
├── utils/
│   └── callBackend.py (MODIFICADO - +funciones agente)
├── app_publica.py (MODIFICADO - +navegación tabs)
└── app_rrhh.py (MODIFICADO - +página insights)

database/
└── schema_agente.sql ⭐ NUEVO - Tablas del agente

Documentación:
├── README_HACKATON.md ⭐ NUEVO - README completo
├── ARQUITECTURA_AGENTE_AUTONOMO.md ⭐ NUEVO - Documentación técnica
└── GUIA_RAPIDA_HACKATON.md ⭐ NUEVO - Esta guía
```

---

## 🐛 Troubleshooting

### Error: "No se puede conectar con el backend"

**Solución:**
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/
# Debería responder: {"name":"NovaMind API","status":"running"}
```

### Error: "Table doesn't exist"

**Solución:**
```bash
# Ejecutar scripts SQL nuevamente
cd database
mysql -u root -p novamind < schema.sql
mysql -u root -p novamind < schema_agente.sql
```

### Error: Modelos de IA no se cargan

**Solución:**
```bash
# Verificar instalación de transformers
pip install transformers==4.45.2 torch sentencepiece

# Primera ejecución descarga modelos (puede tardar)
# Esperar a ver: "Cargando modelo de Sentiment..."
```

### Error: Login de RRHH no funciona

**Solución:**
```bash
# Verificar que usuarios existan
mysql -u root -p novamind
SELECT * FROM usuarios_rrhh;

# Si no existe, ejecutar:
source database/usuarios.sql
```

---

## 📊 Datos de Prueba

El archivo `database/datos_prueba.sql` contiene 20 comentarios pre-analizados para testing del sistema tradicional.

Para probar el agente, es mejor crear conversaciones en vivo desde la app pública.

---

## ✅ Checklist de Verificación

- [ ] Base de datos `novamind` creada con charset utf8mb4
- [ ] Tablas tradicionales creadas (`analisis_comentarios`, `usuarios_rrhh`)
- [ ] Tablas del agente creadas (`conversaciones_agente`, `mensajes_agente`, `insights_agente`)
- [ ] Dependencias instaladas (backend + frontend)
- [ ] Backend corriendo en puerto 8000
- [ ] App pública corriendo en puerto 8501
- [ ] Panel RRHH corriendo en puerto 8502
- [ ] Login RRHH funciona (admin / admin123)
- [ ] Tab "Conversación con el agente" visible en app pública
- [ ] Página "Insights del Agente" visible en panel RRHH
- [ ] Conversación de prueba genera insight correctamente
- [ ] Insight visible en panel de RRHH
- [ ] Se puede actualizar estado de insight

---

## 🎓 Para la Presentación de Hackatón

### Demo Flow Recomendado (5 minutos):

**1. Mostrar Sistema Tradicional (1 min)**
- Dashboard general con comentarios ya analizados
- Explicar: "Esto ya existía: análisis NLP automático"

**2. Introducir Problema (30 seg)**
- "Pero los comentarios estáticos NO revelan POR QUÉ los problemas persisten"

**3. Demo Agente en Vivo (2 min)**
- Abrir app pública
- Mostrar tab "Conversación con agente"
- Escribir comentario con estrés alto
- Mostrar cómo el agente profundiza automáticamente
- Demostrar detección de bloqueo organizacional

**4. Mostrar Insight Generado (1.5 min)**
- Ir a panel RRHH
- Mostrar insight nuevo en dashboard
- Ver detalle completo con conversación
- Explicar evidencias y recomendación

**5. Valor Diferencial (30 seg)**
- "NO es chatbot genérico"
- "DETECTA bloqueos organizacionales"
- "GENERA insights únicos para RRHH"

---

## 📝 Notas Importantes

### Lo que SÍ está implementado:

✅ Sistema completo de análisis NLP (4 modelos Transformer)
✅ Agente autónomo con decisión contextual
✅ Detección de 4 tipos de bloqueos organizacionales
✅ Generación de 3 tipos de insights únicos
✅ Chat público con conversación guiada
✅ Panel de insights para RRHH con estadísticas
✅ Base de datos completa con 3 tablas nuevas
✅ API REST con 7 endpoints nuevos
✅ Documentación completa

### Lo que NO está implementado (futuro):

❌ Análisis predictivo de rotación
❌ Sistema de tickets automático
❌ Integración con Slack/Teams
❌ Soporte multilingüe
❌ Notificaciones push

---

<div align="center">

**🏆 Sistema completamente funcional y listo para demostración**

¿Preguntas? Revisa el README_HACKATON.md completo

</div>
