# Maintenance Reporting Platform

Plataforma web para la gestión de mantenimiento de climatización (chillers y torres de enfriamiento): informes técnicos en PDF y Word, hojas de servicio con firma digital, monitoreo de equipos vía PLC y un asistente de IA que redacta borradores de informe usando el historial real del cliente como contexto.

## Sobre este repositorio

Este repo es un **extracto representativo** del proyecto real (en producción, uso interno), no el código de negocio completo. La carpeta [`examples/`](examples/) tiene 10 archivos, uno por patrón de diseño real — reescritos con nombres genéricos, sin datos ni lógica de negocio de ningún cliente — pensados para leerse de forma aislada:

- [`multi_client_report_config.py`](examples/multi_client_report_config.py) — el informe de cada cliente se arma desde una config data-driven, no desde condicionales dispersos por el código.
- [`dual_renderer_context_builder.py`](examples/dual_renderer_context_builder.py) — un único "context builder" alimenta dos renderers (HTML→PDF y Word) para que nunca diverjan, incluyendo manipulación real de OOXML para controlar formato que python-docx no expone.
- [`ai_draft_history_context.py`](examples/ai_draft_history_context.py) — borrador de IA anclado al historial real del cliente (RAG casero con texto plano), con normalización de campos entre 4 variantes de formulario.
- [`lazy_loaded_embedding_matcher.py`](examples/lazy_loaded_embedding_matcher.py) — modelo de ML pesado (CLIP) con carga perezosa y cache, para no pagar el costo de carga si nadie usa la función esa sesión.
- [`role_based_access_sets.py`](examples/role_based_access_sets.py) — permisos como sets de roles y funciones puras, inyectados a las plantillas vía context processor.
- [`long_lived_pwa_session.py`](examples/long_lived_pwa_session.py) — duración de sesión de 7 días, decisión tomada por una falla real de Android matando el proceso de la PWA a mitad de un flujo de firma.
- [`twin_documents_signature_flow.py`](examples/twin_documents_signature_flow.py) — flujo de firma digital multi-parte con folio correlativo y documentos gemelos vinculados por folio compartido.
- [`modbus_dual_transport_reader.py`](examples/modbus_dual_transport_reader.py) — la misma lectura de PLC funciona sobre dos transportes (Modbus TCP y serie RTU) inyectando el transporte como dependencia.
- [`safe_legacy_migration.py`](examples/safe_legacy_migration.py) — migración idempotente de JSON a SQLite que preserva la forma de datos que el código consumidor ya espera.
- [`normalize_before_grouping.py`](examples/normalize_before_grouping.py) — normalizar texto libre antes de agrupar/contar, para que variantes de formato de la misma persona no cuenten como entidades distintas.

## Qué hace el sistema real

- **Informes técnicos multi-cliente**: PDF (WeasyPrint) y Word (python-docx) generados desde una plantilla común por tipo de instalación (edificio, mall, centro de datos), con secciones y campos que varían según configuración por cliente.
- **Hojas de servicio digitales**: firma en terreno desde un solo dispositivo (técnico, cliente y opcionalmente supervisor), con folio correlativo y PDF generado al cierre.
- **Registro de horas trabajadas**: documento gemelo de cada hoja de servicio, vinculado por folio compartido, con export a Excel.
- **Monitoreo de equipos vía PLC**: lectura de mediciones reales (presión, temperatura) por Modbus, tanto por red (TCP) como por puerto serie (RTU) según el equipo.
- **Asistente de IA embebido**: redacta borradores de observaciones e informes usando el historial real de informes anteriores del cliente como contexto, y responde consultas de uso de la propia app.
- **Reconocimiento de imágenes**: empareja fotos subidas por el técnico con imágenes de referencia usando un modelo de embeddings (CLIP), para completar automáticamente registros visuales cuando corresponde.
- **Control de acceso por rol**: 3 roles (gerencia, administrador, técnico) que acotan qué módulos y acciones de gestión interna están disponibles.
- **Progressive Web App**: instalable en celular, con visor de PDF propio, funcionamiento offline parcial y sesión ajustada al ciclo de vida real de una PWA en Android.

## Arquitectura

```
Navegador / PWA instalada en celular
        │
        ▼
Flask (rutas por módulo: informes, equipos, usuarios, hojas de servicio, PLC, asistente IA)
        │
        ├── Generación de documentos ── WeasyPrint (PDF) + python-docx (Word), desde un context builder único
        ├── Asistente de IA ────────── historial del cliente (texto plano) + LLM, con fallback entre proveedores
        ├── Reconocimiento de imágenes ── modelo de embeddings (CLIP), carga perezosa
        └── Monitoreo de equipos ────── Modbus TCP (red) / RTU (puerto serie)
        │
        ▼
SQLite (usuarios, equipos, hojas de servicio, historial de informes)
```

## Stack técnico

Python · Flask · SQLite · WeasyPrint · python-docx (con manipulación directa de OOXML) · Modbus (`pymodbus` / `minimalmodbus`) · modelo de embeddings CLIP (`sentence-transformers`) · APIs de LLM compatibles con OpenAI, con fallback entre proveedores.

## Estado

El sistema real está en producción, en uso diario por el equipo técnico de la empresa (no es un prototipo de demostración). Los reportes se generan y firman en terreno, en celulares instalados como PWA, y alimentan un dashboard interno de seguimiento por cliente y técnico.

## Cómo correr los ejemplos

Cada archivo en `examples/` es autocontenido y corre solo, sin necesitar el resto del proyecto:

```bash
python examples/multi_client_report_config.py
python examples/role_based_access_sets.py
python examples/long_lived_pwa_session.py
python examples/twin_documents_signature_flow.py
python examples/modbus_dual_transport_reader.py
python examples/safe_legacy_migration.py
python examples/normalize_before_grouping.py
python examples/ai_draft_history_context.py
python examples/lazy_loaded_embedding_matcher.py
```

`dual_renderer_context_builder.py` es el único que necesita una dependencia externa para correr de verdad (`pip install python-docx`), porque genera un `.docx` real como parte de la demostración:

```bash
pip install python-docx
python examples/dual_renderer_context_builder.py
```
