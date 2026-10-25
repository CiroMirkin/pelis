# Pelis en Linux

Probado en **Linux Mint 22.3 (Zena)**, basado en Ubuntu 24.04, con sesión X11 y el Python 3.12 del sistema. Otras distros derivadas de Ubuntu o Debian deberían andar igual; los nombres de paquetes son los de `apt`.

## Paquetes del sistema

```bash
sudo apt install python3.12-venv libxcb-cursor0
```

- `python3.12-venv`: para crear el entorno virtual. Mint no lo trae instalado.
- `libxcb-cursor0`: Qt lo necesita para abrir ventanas en X11. Sin él, la app no arranca.
- El disco compartido es NTFS. Mint lo monta con `ntfs-3g`, que viene instalado, así que no hace falta ningún paquete extra.

## Entorno de desarrollo

El venv de Linux se llama `.venv-linux/` para no pisar el `.venv/` de Windows (que no sirve en Linux):

```bash
python3.12 -m venv .venv-linux
.venv-linux/bin/python -m pip install -e .[dev]
```

> [!NOTE]
> Si no podés instalar `python3.12-venv`, creá el venv con `python3.12 -m venv --without-pip .venv-linux` y después instalá pip con [`get-pip.py`](https://bootstrap.pypa.io/get-pip.py): `.venv-linux/bin/python get-pip.py`.

### Correr desde el código

Creá `dev/pelis.toml` a partir de [`tools/pelis.toml.ejemplo`](tools/pelis.toml.ejemplo), apuntá `biblioteca` a tu carpeta de películas y corré:

```bash
.venv-linux/bin/python -m pelis --app-dir dev
```

### Tests

```bash
.venv-linux/bin/python -m pytest
```

## Armar el ejecutable

```bash
tools/build_linux.sh
```

Usa el mismo [`pelis.spec`](tools/pelis.spec) que Windows y genera `dist/Pelis-linux/`:

```
dist/Pelis-linux/
├── pelis-app/app/
│   ├── linux/              pelis + _internal/
│   └── pelis.toml.ejemplo
└── pelis.sh                lanzador
```

Qt y FFmpeg van dentro del build. En la máquina donde se ejecuta solo hace falta `libxcb-cursor0`.

> [!NOTE]
> PyInstaller avisa que no encuentra `libxcb-cursor.so.0` si el paquete no está instalado. El build se completa igual, pero la app no abre ventana en esa máquina hasta instalarlo.

## Instalar en el disco

Copiá el contenido de `dist/Pelis-linux/` a la raíz del disco, junto a `Peliculas/`. Si el disco ya tiene el build de Windows, se suman `pelis-app/app/linux/` y `pelis.sh`; la base y `pelis.toml` son los mismos para los dos sistemas.

```bash
cp -a dist/Pelis-linux/. /media/$USER/<disco>/
```

Si es una instalación nueva, copiá `pelis-app/app/pelis.toml.ejemplo` como `pelis.toml` y completá las claves. Después:

```bash
/media/$USER/<disco>/pelis.sh
```

> [!TIP]
> Mint monta el disco NTFS con todos los archivos ejecutables, así que `pelis.sh` y el binario corren sin `chmod`. Si el lanzador no arranca, usá `bash pelis.sh`. Si el que falla es el binario, revisá que el disco no esté montado con `noexec`.
