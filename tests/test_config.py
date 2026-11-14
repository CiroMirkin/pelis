import pytest
from PySide6.QtCore import QSettings

from pelis import config as cfg


def preferencias(app_dir):
    return QSettings(str(app_dir / "preferencias.ini"), QSettings.IniFormat)


def test_instalada_sin_toml_usa_los_valores_por_defecto(tmp_path):
    c = cfg.cargar(tmp_path, portable=False)
    assert c.biblioteca is None
    assert c.omdb_api_key == "" and c.idiomas_sinopsis == ["es-MX", "es-ES"]
    assert not c.portable


def test_portable_sin_toml_es_un_error(tmp_path):
    with pytest.raises(cfg.ErrorConfig):
        cfg.cargar(tmp_path)


def test_biblioteca_ya_no_es_obligatoria_en_el_toml(tmp_path):
    (tmp_path / "pelis.toml").write_text('omdb_api_key = "x"\n')
    c = cfg.cargar(tmp_path)
    assert c.biblioteca is None and c.omdb_api_key == "x"


def test_la_biblioteca_del_toml_es_relativa_a_app(tmp_path):
    (tmp_path / "pelis.toml").write_text('biblioteca = "../pelis-ajenas"\n')
    assert cfg.cargar(tmp_path).biblioteca == (tmp_path.parent / "pelis-ajenas").resolve()


def test_la_biblioteca_de_preferencias_gana_sobre_la_del_toml(tmp_path):
    (tmp_path / "pelis.toml").write_text('biblioteca = "toml"\n')
    c = cfg.cargar(tmp_path)
    prefs = preferencias(tmp_path)
    cfg.aplicar_preferencias(c, prefs)
    assert c.biblioteca == (tmp_path / "toml").resolve()
    prefs.setValue("biblioteca/ruta", "../otra")
    cfg.aplicar_preferencias(c, prefs)
    assert c.biblioteca == (tmp_path.parent / "otra").resolve()


def test_portable_guarda_la_ruta_relativa_a_app(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    (app / "pelis.toml").write_text("")
    c = cfg.cargar(app)
    assert cfg.texto_de_biblioteca(c, tmp_path / "Peliculas") == "../Peliculas"


def test_instalada_guarda_la_ruta_absoluta(tmp_path):
    c = cfg.cargar(tmp_path, portable=False)
    assert cfg.texto_de_biblioteca(c, tmp_path / "Peliculas") == str((tmp_path / "Peliculas").resolve())


def test_carpeta_de_datos_en_linux(monkeypatch, tmp_path):
    monkeypatch.setattr(cfg.sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert cfg.carpeta_de_datos() == tmp_path / ".local" / "share" / "pelis"


def test_carpeta_de_datos_en_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(cfg.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert cfg.carpeta_de_datos() == tmp_path / "Pelis"


def build_en(monkeypatch, tmp_path):
    ejecutable = tmp_path / "app" / "linux" / "pelis"
    ejecutable.parent.mkdir(parents=True)
    monkeypatch.setattr(cfg.sys, "frozen", True, raising=False)
    monkeypatch.setattr(cfg.sys, "executable", str(ejecutable))
    monkeypatch.setattr(cfg.sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "datos"))
    return tmp_path / "app"


def test_con_pelis_toml_junto_a_la_app_corre_portable(monkeypatch, tmp_path):
    app = build_en(monkeypatch, tmp_path)
    (app / "pelis.toml").write_text("")
    assert cfg.app_dir_por_defecto() == (app.resolve(), True)


def test_sin_pelis_toml_corre_instalada_y_crea_la_carpeta_de_datos(monkeypatch, tmp_path):
    build_en(monkeypatch, tmp_path)
    assert cfg.app_dir_por_defecto() == (tmp_path / "datos" / "pelis", False)
    assert (tmp_path / "datos" / "pelis").is_dir()
