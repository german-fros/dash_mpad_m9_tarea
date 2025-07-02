# Dashboard Deportivo - Análisis de Rendimiento y Gestión de Contratos

## Descripción del Proyecto

Dashboard interactivo desarrollado con **Dash/Flask** para análisis de rendimiento deportivo y gestión administrativa de contratos de jugadores de fútbol uruguayo. Proporciona visualizaciones interactivas, reportes PDF y métricas avanzadas de performance.

### Objetivos Principales

- **Análisis de Performance**: Visualización de estadísticas de jugadores (goles, asistencias, eficiencia)
- **Gestión Administrativa**: Control de contratos, salarios y vencimientos
- **Reportes Profesionales**: Exportación de análisis a PDF
- **Interactividad Avanzada**: Filtros dinámicos y visualizaciones reactivas

## Arquitectura del Sistema

### Stack Tecnológico
- **Backend**: Flask + Flask-Login (autenticación)
- **Frontend**: Dash + Plotly (visualizaciones)
- **Styling**: Bootstrap (Dash Bootstrap Components)
- **Data Processing**: Pandas + NumPy
- **PDF Generation**: ReportLab
- **Caching**: functools.lru_cache

### Estructura de Archivos
```
dash_mpad_m9_tarea/
├── app.py                 # Aplicación principal y routing
├── login_manager.py       # Sistema de autenticación
├── requirements.txt       # Dependencias del proyecto
├── 
├── assets/
│   └── style.css         # Estilos personalizados
├── 
├── components/
│   └── navbar.py         # Navegación con sistema de fallback
├── 
├── pages/
│   ├── login.py          # Página de autenticación
│   ├── home.py           # Dashboard principal
│   ├── performance.py    # Análisis de rendimiento
│   └── adm.py           # Panel administrativo
├── 
└── data/
    ├── raw/
    │   └── contratos_uruguay.csv    # Datos de contratos
    └── processed/
        └── data_uruguay_full.csv    # Datos de performance
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes)

### 1. Clonar el Repositorio
```bash
git clone <https://github.com/german-fros/dash_mpad_m9_tarea.git>
cd dash_mpad_m9_tarea
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Preparar Datos
Asegúrese de que los siguientes archivos CSV estén presentes:

**data/raw/contratos_uruguay.csv** - Datos de contratos con columnas:
- Jugador, Equipo, Posicion, Fecha_inicio, Fecha_fin, Salario_mensual_usd, Cláusula_rescisión_usd

**data/processed/data_uruguay_full.csv** - Datos de performance con columnas:
- Player, Team, Position, Age, Goals, Assists, Minutes played, Shots, Temporada

### 5. Ejecutar la Aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:8050`

## Sistema de Autenticación

### Credenciales por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin`

### Seguridad Implementada
- Autenticación con Flask-Login
- Protección de rutas administrativas
- Gestión de sesiones segura
- Logging de intentos de acceso

## Funcionalidades Principales

### 1. Dashboard Principal (`/`)
- Resumen general del sistema
- Métricas clave de rendimiento
- Navegación rápida a secciones especializadas

### 2. Análisis de Performance (`/performance`)

#### Características:
- **Filtros Interactivos**: Por temporada y equipo
- **Visualizaciones Avanzadas**:
  - Scatter plot: Goles vs Disparos (con línea de eficiencia promedio)
  - Bar chart: Top 10 jugadores en contribución ofensiva
- **Tabla Dinámica**: Ranking personalizable por goles, asistencias o minutos
- **Exportación PDF**: Reportes profesionales con gráficos incluidos

#### Métricas Analizadas:
- Goles y asistencias totales
- Expected Goals (xG) y Expected Assists (xA)
- Eficiencia de disparos
- Minutos jugados y participación

### 3. Panel Administrativo (`/admn`)

#### Características:
- **Gestión de Contratos**: Visualización completa de contratos activos
- **Análisis Salarial**: Distribución de salarios por posición
- **Timeline de Vencimientos**: Contratos que expiran por semestre
- **Filtros Avanzados**:
  - Por club específico
  - Por posición de juego
  - Por rango salarial (slider interactivo)

#### Funcionalidades de Tabla:
- Ordenamiento por fecha de fin, posición o salario
- Mostrar todos los contratos (sin límite de filas)
- Información detallada: fechas, salarios, cláusulas de rescisión

## Optimizaciones de Performance

### Sistema de Cache Implementado
- **@lru_cache** en carga de datos CSV
- **Cache de datasets filtrados** (32 combinaciones más frecuentes)
- **Mejora 10x** en tiempo de respuesta de callbacks repetitivos

### Estados de Carga
- **Spinners visuales** en todas las visualizaciones
- **Feedback inmediato** durante operaciones pesadas
- **Transiciones suaves** con animaciones CSS

### Manejo Robusto de Errores
- **Sistema de fallback** multi-nivel
- **Logging comprehensivo** para debugging
- **Datos sintéticos** como respaldo en caso de fallo

## Datos y Procesamiento

### Fuentes de Datos
1. **Contratos**: `data/raw/contratos_uruguay.csv`
   - Información contractual de jugadores
   - Salarios y fechas de vencimiento
   - Cláusulas de rescisión

2. **Performance**: `data/processed/data_uruguay_full.csv`
   - Estadísticas de rendimiento por temporada
   - Métricas avanzadas (xG, xA)
   - Datos de minutos y participación

## Troubleshooting

### Problemas Comunes

**Error: Archivo CSV no encontrado**
```
Solución: Verificar que los archivos estén en las rutas correctas
- data/raw/contratos_uruguay.csv
- data/processed/data_uruguay_full.csv
```

**Error: Dependencias faltantes**
```bash
pip install --upgrade -r requirements.txt
```

**Problemas de autenticación**
```
Verificar credenciales: admin/password
Revisar logs en app.log para detalles
```

**Performance lenta**
```
Cache está funcionando: verificar hits en logs
Considerar reducir maxsize si memoria limitada
```

## Logs y Monitoreo

### Logging Implementado
- **Archivo**: `app.log` (persistencia)
- **Consola**: Output en tiempo real
- **Niveles**: INFO, WARNING, ERROR, CRITICAL

### Métricas Monitoreadas
- Intentos de login (exitosos/fallidos)
- Navegación entre páginas
- Errores de carga de datos
- Performance de cache

## Licencia

Proyecto desarrollado para fines educativos y de análisis deportivo.

## Soporte

Para soporte técnico o consultas:
- Revisar logs en `app.log`
- Verificar dependencias en `requirements.txt`
- Consultar documentación en código fuente