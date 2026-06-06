# 📚 Book Translator

App web para gestionar la traducción de libros en inglés.
Sube fotos de páginas (desde celular o PC), traduce manualmente y exporta a Word.

---

## Estructura del proyecto

```
book-translator/
├── app/
│   ├── __init__.py          # App factory + extensiones
│   ├── models.py            # Modelos Book y Page (PostgreSQL)
│   ├── routes/
│   │   ├── books.py         # CRUD de libros
│   │   ├── pages.py         # Subida de imágenes + guardado
│   │   └── export.py        # Exportar a Word (.docx)
│   ├── templates/
│   │   ├── index.html       # Lista de libros
│   │   └── translate.html   # Espacio de trabajo de traducción
│   └── static/
│       └── uploads/         # Imágenes subidas (no versionar)
├── migrations/              # Flask-Migrate
├── run.py                   # Entry point
├── requirements.txt
├── .env.example
├── .env                     # ← tú lo creas (no se versiona)
└── .gitignore
```

---

## Configuración inicial

### 1. Clonar / crear directorio y entrar

```bash
cd book-translator
```

### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

py -3.12 -m venv .venv

# Activar en Linux / macOS
source venv/bin/activate

# Activar en Windows (CMD)
venv\Scripts\activate.bat

# Activar en Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear base de datos en PostgreSQL

```bash
# Entrar a psql
psql -U postgres

# Dentro de psql:
CREATE DATABASE book_translator;
\q
```

### 5. Configurar variables de entorno

```bash
# Copiar el ejemplo
cp .env.example .env

# Editar .env con tus credenciales reales
nano .env   # o abre con tu editor favorito
```

Ejemplo de `.env`:
```
SECRET_KEY=mi-clave-super-secreta-123
DATABASE_URL=postgresql://postgres:MiPassword@localhost:5432/book_translator
FLASK_ENV=development
FLASK_DEBUG=1
```

### 6. Inicializar migraciones y crear tablas

```bash
# Solo la primera vez
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

> Si ya tienes la base creada y solo quieres las tablas sin migraciones:
> ```bash
> python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
> ```

---

## Ejecutar la app

```bash
python run.py
```

Abre en el navegador: **http://localhost:5000**

Desde tu **celular** (misma red WiFi):
```
http://<IP-de-tu-PC>:5000
```
Para encontrar tu IP:
- Linux/macOS: `ip addr` o `ifconfig`
- Windows: `ipconfig`

---

## Uso básico

1. **Crear un libro** → botón "Nuevo libro", llena título, autor e idiomas.
2. **Subir páginas** → desde la vista de traducción, clic en el ícono 📷 del sidebar.
   - En celular puedes tomar foto directamente con la cámara.
   - En PC seleccionas los archivos desde tu disco.
3. **Traducir** → selecciona una página, escribe el texto original y tu traducción.
   - `Ctrl + S` guarda rápidamente.
4. **Exportar** → botón "⬇️ Exportar Word" genera un `.docx` con imagen + traducción por página.

---

## Nombrado automático de imágenes

Las imágenes se guardan con el formato:
```
<slug_del_libro>_p<numero_pagina_4_digitos>.<ext>
```
Ejemplo: `english_grammar_in_use_p0001.jpg`, `english_grammar_in_use_p0002.jpg`

---

## Comandos útiles

```bash
# Activar entorno virtual (siempre antes de trabajar)
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate.bat       # Windows CMD

# Instalar nuevas dependencias
pip install <paquete>
pip freeze > requirements.txt   # actualizar el archivo

# Aplicar migraciones después de cambiar modelos
flask db migrate -m "descripcion del cambio"
flask db upgrade

# Desactivar entorno virtual
deactivate
```

---

## Variables de entorno (`.env`)

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Flask (cámbiala en producción) |
| `DATABASE_URL` | URL completa de PostgreSQL |
| `FLASK_ENV` | `development` o `production` |
| `FLASK_DEBUG` | `1` para activar debug, `0` para producción |
