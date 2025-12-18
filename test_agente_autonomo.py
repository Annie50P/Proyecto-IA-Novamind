"""
Script de prueba del Agente Autónomo de Bienestar Laboral

Este script prueba la lógica del agente SIN necesidad de:
- Base de datos MySQL
- Servidor FastAPI corriendo
- Frontend Streamlit

Simplemente ejecuta: python test_agente_autonomo.py
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Agregar path del backend
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("🧪 TEST DEL AGENTE AUTÓNOMO DE BIENESTAR LABORAL")
print("=" * 70)
print()


# ============================================================
# MOCK DEL NLPAnalyzer (para no cargar modelos de IA)
# ============================================================

class MockNLPAnalyzer:
    """Mock del analizador NLP para testing sin cargar modelos pesados"""

    def analyze_comment(self, text: str, meta: dict = None) -> Dict[str, Any]:
        """Simula análisis NLP basado en palabras clave"""
        text_lower = text.lower()

        # Detectar estrés basado en palabras clave
        stress_keywords = ["estresado", "agotado", "presión", "burnout", "sobrecarga"]
        stress_level = "alto" if any(kw in text_lower for kw in stress_keywords) else "medio"

        # Detectar emoción
        if any(w in text_lower for w in ["feliz", "contento", "alegre", "gusta"]):
            emotion = ("alegría", 0.85)
            sent_dist = {"positive": 0.8, "neutral": 0.15, "negative": 0.05}
        elif any(w in text_lower for w in ["triste", "mal", "deprimido"]):
            emotion = ("tristeza", 0.85)
            sent_dist = {"positive": 0.1, "neutral": 0.2, "negative": 0.7}
        elif any(w in text_lower for w in ["enojado", "furioso", "molesto"]):
            emotion = ("enojo", 0.85)
            sent_dist = {"positive": 0.1, "neutral": 0.2, "negative": 0.7}
        else:
            emotion = ("tristeza", 0.75)
            sent_dist = {"positive": 0.2, "neutral": 0.3, "negative": 0.5}

        # Detectar categorías
        categories = []
        if any(w in text_lower for w in ["trabajo", "carga", "tareas", "proyecto"]):
            categories.append(("sobrecarga laboral", 0.92))
        if any(w in text_lower for w in ["jefe", "supervisor", "líder", "manager"]):
            categories.append(("liderazgo", 0.88))
        if any(w in text_lower for w in ["recursos", "herramientas", "equipo", "sistema"]):
            categories.append(("recursos insuficientes", 0.85))
        if any(w in text_lower for w in ["comunicación", "hablar", "decir"]):
            categories.append(("comunicación", 0.80))

        if not categories:
            categories.append(("satisfacción general", 0.60))

        return {
            "emotion": {"label": emotion[0], "score": emotion[1]},
            "stress": {"level": stress_level, "sentiment_dist": sent_dist},
            "categories": [{"label": c, "score": s} for c, s in categories],
            "summary": text[:100] + "..." if len(text) > 100 else text,
            "suggestion": "Sugerencia mock del sistema base",
            "meta": meta or {}
        }


# ============================================================
# PRUEBAS DEL AGENTE
# ============================================================

def test_importacion():
    """Test 1: Verificar que el módulo se importe correctamente"""
    print("📦 Test 1: Importación del módulo iaAgent")
    try:
        from ia.iaAgent import AgenteAutonomo, DetectorBloqueos, GeneradorInsights
        print("   ✅ Módulo importado correctamente")
        print(f"   - AgenteAutonomo: {AgenteAutonomo}")
        print(f"   - DetectorBloqueos: {DetectorBloqueos}")
        print(f"   - GeneradorInsights: {GeneradorInsights}")
        return True
    except Exception as e:
        print(f"   ❌ Error al importar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_inicializacion():
    """Test 2: Verificar que el agente se inicialice correctamente"""
    print("\n🔧 Test 2: Inicialización del agente")
    try:
        from ia.iaAgent import AgenteAutonomo

        mock_nlp = MockNLPAnalyzer()
        agente = AgenteAutonomo(mock_nlp)

        print("   ✅ Agente inicializado correctamente")
        print(f"   - Configuración: {agente.cfg}")
        print(f"   - NLP Analyzer: {type(agente.nlp)}")
        return True, agente
    except Exception as e:
        print(f"   ❌ Error al inicializar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_caso_positivo(agente):
    """Test 3: Comentario positivo (NO debe profundizar)"""
    print("\n😊 Test 3: Comentario positivo (sin seguimiento)")

    mensaje = "Me gusta mucho el ambiente de trabajo en mi equipo"
    meta = {"departamento": "IT", "equipo": "Backend"}

    print(f"   📝 Mensaje: \"{mensaje}\"")

    try:
        resultado = agente.iniciar_conversacion(mensaje, meta)

        print(f"   🤖 Decisión del agente:")
        print(f"      - Requiere seguimiento: {resultado['requiere_seguimiento']}")
        print(f"      - Nivel de riesgo: {resultado['nivel_riesgo']}")
        print(f"      - Razón: {resultado['razon_seguimiento']}")

        if resultado['requiere_seguimiento']:
            print(f"      - Pregunta: {resultado['pregunta_agente']}")

        # Verificar que NO profundice
        if not resultado['requiere_seguimiento']:
            print("   ✅ CORRECTO: El agente NO profundiza en comentario positivo")
            return True
        else:
            print("   ⚠️  ADVERTENCIA: El agente profundizó en comentario positivo")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_caso_estres_alto(agente):
    """Test 4: Estrés alto (SÍ debe profundizar)"""
    print("\n😰 Test 4: Estrés alto (con seguimiento)")

    mensaje = "Me siento muy estresado con la carga de trabajo actual"
    meta = {"departamento": "Ventas", "equipo": "Turno A"}

    print(f"   📝 Mensaje: \"{mensaje}\"")

    try:
        resultado = agente.iniciar_conversacion(mensaje, meta)

        print(f"   🤖 Decisión del agente:")
        print(f"      - Requiere seguimiento: {resultado['requiere_seguimiento']}")
        print(f"      - Nivel de riesgo: {resultado['nivel_riesgo']}")
        print(f"      - Razón: {resultado['razon_seguimiento']}")
        print(f"      - Categoría principal: {resultado['categoria_principal']}")

        if resultado['requiere_seguimiento']:
            print(f"      - Pregunta: {resultado['pregunta_agente']}")

        # Verificar que SÍ profundice
        if resultado['requiere_seguimiento'] and resultado['pregunta_agente']:
            print("   ✅ CORRECTO: El agente profundiza en comentario con estrés alto")
            return True, resultado
        else:
            print("   ❌ ERROR: El agente NO profundizó cuando debía hacerlo")
            return False, None

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_deteccion_bloqueo_liderazgo(agente):
    """Test 5: Detección de bloqueo de liderazgo"""
    print("\n🚧 Test 5: Detección de bloqueo de liderazgo")

    from ia.iaAgent import DetectorBloqueos
    detector = DetectorBloqueos()

    respuestas_test = [
        ("Sí, pero mi jefe nunca responde", "liderazgo"),
        ("Nunca tiene tiempo para reunirse", "liderazgo"),
        ("Me ignora completamente", "liderazgo"),
        ("Prometieron recursos pero nunca llegaron", "recursos"),
        ("Hay mucha burocracia aquí", "proceso"),
        ("Así es siempre en esta empresa", "cultural"),
    ]

    correctos = 0
    total = len(respuestas_test)

    for respuesta, tipo_esperado in respuestas_test:
        print(f"\n   📝 Respuesta: \"{respuesta}\"")

        bloqueo = detector.detectar(respuesta, [])

        print(f"      - Bloqueo detectado: {bloqueo['hay_bloqueo']}")
        if bloqueo['hay_bloqueo']:
            print(f"      - Tipo: {bloqueo['tipo']}")
            print(f"      - Severidad: {bloqueo['severidad']}")
            print(f"      - Descripción: {bloqueo['descripcion']}")

            if bloqueo['tipo'] == tipo_esperado:
                print(f"      ✅ Tipo correcto detectado")
                correctos += 1
            else:
                print(f"      ⚠️  Esperado: {tipo_esperado}, Detectado: {bloqueo['tipo']}")
        else:
            print(f"      ❌ No se detectó bloqueo (esperado: {tipo_esperado})")

    print(f"\n   📊 Resultado: {correctos}/{total} bloqueos detectados correctamente")

    if correctos >= total * 0.7:  # 70% o más
        print("   ✅ Test de detección de bloqueos APROBADO")
        return True
    else:
        print("   ⚠️  Test de detección de bloqueos necesita mejora")
        return False


def test_generacion_insight(agente):
    """Test 6: Generación de insight"""
    print("\n💡 Test 6: Generación de insight")

    from ia.iaAgent import GeneradorInsights

    # Simular conversación completa
    conversacion = {
        "conversacion_id": 1,
        "departamento": "Ventas",
        "equipo": "Turno A"
    }

    analisis_inicial = {
        "emotion": {"label": "tristeza", "score": 0.85},
        "stress": {"level": "alto"},
        "categories": [{"label": "sobrecarga laboral", "score": 0.92}]
    }

    mensajes = [
        {"rol": "empleado", "contenido": "Me siento muy estresado con la carga de trabajo"},
        {"rol": "agente", "contenido": "¿Ya intentaste hablar con tu supervisor sobre esto?"},
        {"rol": "empleado", "contenido": "Sí, pero nunca tiene tiempo para reunirse"},
        {"rol": "agente", "contenido": "¿Cuánto tiempo llevas intentando reunirte?"},
        {"rol": "empleado", "contenido": "Llevo 2 meses intentando"}
    ]

    bloqueos = [{
        "hay_bloqueo": True,
        "tipo": "liderazgo",
        "descripcion": "Supervisor no accesible",
        "severidad": "alta",
        "evidencia": "nunca tiene tiempo para reunirse"
    }]

    try:
        insight = GeneradorInsights.generar(
            conversacion,
            analisis_inicial,
            mensajes,
            bloqueos
        )

        if insight:
            print("   ✅ Insight generado correctamente")
            print(f"      - Tipo: {insight['tipo']}")
            print(f"      - Categoría: {insight['categoria']}")
            print(f"      - Título: {insight['titulo']}")
            print(f"      - Severidad: {insight['severidad']}")
            print(f"      - Descripción: {insight['descripcion'][:100]}...")
            print(f"      - Recomendación: {insight['recomendacion_rrhh'][:100]}...")
            print(f"      - Evidencias: {len(insight.get('evidencias', []))} encontradas")
            return True
        else:
            print("   ⚠️  No se generó insight")
            return False

    except Exception as e:
        print(f"   ❌ Error al generar insight: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_flujo_completo(agente):
    """Test 7: Flujo completo de conversación"""
    print("\n🔄 Test 7: Flujo completo de conversación")

    # Mensaje inicial
    mensaje_inicial = "Me siento muy estresado con mi jefe"
    meta = {"departamento": "Operaciones"}

    print(f"   1️⃣ Mensaje inicial: \"{mensaje_inicial}\"")

    try:
        # Iniciar conversación
        resultado_inicial = agente.iniciar_conversacion(mensaje_inicial, meta)

        if not resultado_inicial['requiere_seguimiento']:
            print("   ⚠️  Agente no requiere seguimiento (debería requerirlo)")
            return False

        print(f"      ✅ Conversación iniciada")
        print(f"      - Pregunta 1: {resultado_inicial['pregunta_agente']}")

        # Simular respuestas
        respuestas = [
            "Sí, pero nunca me hace caso",
            "Llevo 3 meses intentando hablar con él",
            "No, gracias"
        ]

        contexto = {
            "conversacion_id": 1,
            "nivel_riesgo": resultado_inicial['nivel_riesgo'],
            "categoria_principal": resultado_inicial['categoria_principal'],
            "departamento": meta.get("departamento"),
            "equipo": meta.get("equipo"),
            "analisis_inicial": resultado_inicial['analisis_nlp']
        }

        mensajes_previos = [
            {"rol": "empleado", "contenido": mensaje_inicial},
            {"rol": "agente", "contenido": resultado_inicial['pregunta_agente']}
        ]

        for i, respuesta in enumerate(respuestas, 2):
            print(f"\n   {i}️⃣ Respuesta del empleado: \"{respuesta}\"")

            resultado = agente.procesar_respuesta(
                respuesta,
                contexto,
                mensajes_previos
            )

            print(f"      - Acción: {resultado['accion']}")
            print(f"      - Nivel de riesgo: {resultado['nivel_riesgo_actualizado']}")

            if resultado.get('bloqueo_detectado') and resultado['bloqueo_detectado']['hay_bloqueo']:
                print(f"      🚧 Bloqueo detectado: {resultado['bloqueo_detectado']['tipo']}")

            if resultado['accion'] == 'profundizar' and resultado.get('pregunta'):
                print(f"      - Siguiente pregunta: {resultado['pregunta']}")
                mensajes_previos.append({"rol": "empleado", "contenido": respuesta})
                mensajes_previos.append({"rol": "agente", "contenido": resultado['pregunta']})

            elif resultado['accion'] == 'cerrar':
                print(f"      ✅ Conversación cerrada")

                if resultado.get('insight'):
                    print(f"      💡 Insight generado:")
                    print(f"         - Tipo: {resultado['insight']['tipo']}")
                    print(f"         - Severidad: {resultado['insight']['severidad']}")
                break

            contexto['nivel_riesgo'] = resultado['nivel_riesgo_actualizado']

        print("\n   ✅ Flujo completo ejecutado sin errores")
        return True

    except Exception as e:
        print(f"\n   ❌ Error en flujo completo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# EJECUTAR TODOS LOS TESTS
# ============================================================

def ejecutar_tests():
    """Ejecuta todos los tests en secuencia"""

    resultados = {}

    # Test 1: Importación
    resultados['importacion'] = test_importacion()

    if not resultados['importacion']:
        print("\n❌ No se puede continuar sin importar el módulo correctamente")
        return resultados

    # Test 2: Inicialización
    ok, agente = test_inicializacion()
    resultados['inicializacion'] = ok

    if not ok:
        print("\n❌ No se puede continuar sin inicializar el agente")
        return resultados

    # Test 3: Caso positivo
    resultados['caso_positivo'] = test_caso_positivo(agente)

    # Test 4: Caso estrés alto
    ok, _ = test_caso_estres_alto(agente)
    resultados['caso_estres_alto'] = ok

    # Test 5: Detección de bloqueos
    resultados['deteccion_bloqueos'] = test_deteccion_bloqueo_liderazgo(agente)

    # Test 6: Generación de insights
    resultados['generacion_insights'] = test_generacion_insight(agente)

    # Test 7: Flujo completo
    resultados['flujo_completo'] = test_flujo_completo(agente)

    return resultados


def mostrar_resumen(resultados):
    """Muestra resumen final de tests"""
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)

    total = len(resultados)
    aprobados = sum(1 for v in resultados.values() if v)

    for nombre, resultado in resultados.items():
        status = "✅ APROBADO" if resultado else "❌ FALLIDO"
        print(f"{status} - {nombre.replace('_', ' ').title()}")

    print("=" * 70)
    print(f"Resultado final: {aprobados}/{total} tests aprobados ({aprobados/total*100:.1f}%)")
    print("=" * 70)

    if aprobados == total:
        print("\n🎉 ¡TODOS LOS TESTS APROBADOS!")
        print("✅ El agente autónomo está listo para integrarse al sistema completo")
    elif aprobados >= total * 0.7:
        print("\n⚠️  La mayoría de tests aprobados, pero hay algunos problemas")
        print("🔧 Revisa los tests fallidos antes de continuar")
    else:
        print("\n❌ Muchos tests fallidos")
        print("🔧 Revisa la implementación del agente antes de continuar")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        resultados = ejecutar_tests()
        mostrar_resumen(resultados)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal durante los tests: {str(e)}")
        import traceback
        traceback.print_exc()
