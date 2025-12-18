# core/coreModels.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from backend.config.database import Base


class AnalisisComentario(Base):
    __tablename__ = "analisis_comentarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comentario: Mapped[str] = mapped_column(Text, nullable=False)

    emotion_label: Mapped[str] = mapped_column(String(64))
    emotion_score: Mapped[float] = mapped_column(Float)

    stress_level: Mapped[str] = mapped_column(String(32))
    sent_pos: Mapped[float] = mapped_column(Float, default=0.0)
    sent_neu: Mapped[float] = mapped_column(Float, default=0.0)
    sent_neg: Mapped[float] = mapped_column(Float, default=0.0)

    categories: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str] = mapped_column(Text)

    departamento: Mapped[str] = mapped_column(String(80), default="")
    equipo: Mapped[str] = mapped_column(String(80), default="")
    fecha: Mapped[str] = mapped_column(String(20), default="")

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UsuarioRRHH(Base):
    __tablename__ = "usuarios_rrhh"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Integer, default=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True)


# ============================================================
# MODELOS DEL AGENTE AUTÓNOMO
# ============================================================

class ConversacionAgente(Base):
    """Modelo para conversaciones del agente autónomo"""
    __tablename__ = "conversaciones_agente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mensaje_inicial: Mapped[str] = mapped_column(Text, nullable=False)
    analisis_inicial: Mapped[dict] = mapped_column(JSON, nullable=False)

    departamento: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    equipo: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    categoria_principal: Mapped[str] = mapped_column(String(100), nullable=True, index=True)

    nivel_riesgo_inicial: Mapped[str] = mapped_column(String(32), nullable=False, default="medio")
    nivel_riesgo_actual: Mapped[str] = mapped_column(String(32), nullable=False, default="medio", index=True)

    estado: Mapped[str] = mapped_column(String(32), nullable=False, default="activa", index=True)
    razon_seguimiento: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True
    )


class MensajeAgente(Base):
    """Modelo para mensajes individuales de conversaciones del agente"""
    __tablename__ = "mensajes_agente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversacion_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    rol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # 'empleado' o 'agente'
    contenido: Mapped[str] = mapped_column(Text, nullable=False)

    analisis: Mapped[dict] = mapped_column(JSON, nullable=True)  # Solo para mensajes de empleado
    meta_info: Mapped[dict] = mapped_column(JSON, nullable=True)  # Información adicional del mensaje

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class InsightAgente(Base):
    """Modelo para insights generados por el agente para RRHH"""
    __tablename__ = "insights_agente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversacion_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    tipo: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    contexto_completo: Mapped[str] = mapped_column(Text, nullable=False)
    recomendacion_rrhh: Mapped[str] = mapped_column(Text, nullable=False)

    evidencias: Mapped[dict] = mapped_column(JSON, nullable=True)

    severidad: Mapped[str] = mapped_column(String(32), nullable=False, default="media", index=True)

    departamento: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    equipo: Mapped[str] = mapped_column(String(80), nullable=True, index=True)

    estado: Mapped[str] = mapped_column(String(32), nullable=False, default="nuevo", index=True)
    revisado_por: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    fecha_revision: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    notas_rrhh: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True
    )
