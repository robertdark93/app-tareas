# Mejoras propuestas para Gestor de Tareas

Revisión de código — 16/06/2026 · Actualizado tras implementar mejoras críticas y de impacto medio

---

## ✅ Realizadas

| # | Área | Mejora | Detalle |
|---|------|--------|---------|
| 🐛 | Bug | **workload.html** | Creado el template faltante + URL añadida + link en admin dashboard |
| 2 | Escalabilidad | **Redis + channels-redis** | Nuevo contenedor `tareas_redis` en docker-compose, `CHANNEL_LAYERS` configurado con `RedisChannelLayer` |
| 3 | Seguridad | **CSRF en JS inline** | Migrados 6 templates (`task_list`, `task_detail`, `task_form`, `kanban`, `base`) de `'{{ csrf_token }}'` a función `getCSRFToken()` que lee desde cookie |
| 4 | UX | **Toast notifications** | Contenedor `#toast-container` en `base.html`, estilos toast en `style.css`, errores visibles en kanban drag & drop y status-select |
| 5 | Estabilidad | **Scheduler con `select_for_update`** | `BackupConfig.objects.select_for_update().first()` dentro de `transaction.atomic()` para evitar backups concurrentes entre workers |
| 1 | Seguridad | **psycopg2-binary** | Se evaluó y se **mantuvo** `psycopg2-binary`: en entorno Docker con imagen fija es seguro y evita instalar `libpq-dev` + compilar desde fuente |
| 6 | Frontend | **Modularizar CSS** | Separado `style.css` (1267 líneas) en 7 archivos: `variables.css`, `base.css`, `layout.css`, `components.css`, `admin.css`, `responsive.css`, `toast.css` |
| 7 | Frontend | **Extraer JS a archivos** | Creados 6 archivos JS: `base.js`, `kanban.js`, `task_list.js`, `task_detail.js`, `task_form.js`, `charts.js`. Inline JS reemplazado en 7 templates |
| 8 | Frontend | **Input de horas** | Reemplazado el hack hh:mm + `Math.round()` por `NumberInput(step='0.25')` nativo de Django |
| 9 | Backend | **select_related/prefetch_related** | Agregado `select_related('usuario', 'creado_por', 'departamento')` en `tareas_visibles()` y en todas las vistas CBV |
| 10 | UX | **Calendario: vista agenda** | Agregada lista de tareas del mes ordenadas por fecha debajo del calendario mensual |
| 11 | Backend | **Tests** | Escritos 67 tests (modelos, vistas, URLs, comandos) — todos pasando |
| 12 | DevOps | **Healthcheck HTTP** | Endpoint `/health/` + healthcheck en docker-compose que consulta Daphne directamente |
| 13 | UX | **Recordarme** | Checkbox en login que setea sesión por 7 días (`SESSION_COOKIE_AGE=604800`) vía `CustomLoginView` |
| 15 | Frontend | **PWA / Service Worker** | `manifest.json`, `sw.js` con cache de static, registro en `base.html` |
| 14 | Backend | **Rate limiting en login** | `django-ratelimit==4.1.0` con Redis, 10 POST/min por IP + lockout 5 intentos/2 min |

---

## 🔴 Críticos / Alto impacto (pendientes)

| # | Área | Problema | Recomendación |
|---|------|----------|---------------|
| — | — | *(ninguno — todos los críticos fueron implementados)* | — |

---

---

## 🟢 Bajo impacto / Nice to have

| # | Área | Sugerencia |
|---|------|-----------|
| 16 | UX | **Drag & drop reordenar tareas** en vista de lista (no solo subtareas) |
| 17 | UX | **Feed de actividad** tipo timeline (TaskLog ya existe, solo falta template) |
| 18 | UX | **Búsqueda full-text** con PostgreSQL `SearchVector` / `SearchQuery` |
| 19 | UX | **Atajos de teclado**: `C` → crear tarea, `1-4` → cambiar estado, `/` → buscar |
| 20 | UX | **Modo focus/zen**: ocultar navbar al trabajar en una tarea |
| 21 | Frontend | **Transiciones suaves** en kanban drag & drop (actualmente instantáneo) |
| 22 | Backend | Agregar `created_at`/`updated_at` a **todos** los modelos |
| 23 | DevOps | **CI/CD**: test stage antes de deploy en `.gitlab-ci.yml` |
| 24 | Backend | **Export PDF** con más opciones (rango de fechas, filtros, orientación) |
| 25 | UX | **Notificaciones por email** además de in-app (WebSocket offline no entrega nada) |

---

## Prioridad sugerida (próximos pasos)

1. ✉️ Notificaciones por email
2. 🔍 Búsqueda full-text con PostgreSQL SearchVector
3. ⌨️ Atajos de teclado
4. 🖼️ Feed de actividad (timeline con TaskLog)
5. 📄 Export PDF con más opciones
