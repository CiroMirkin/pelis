# Build --onedir sin consola. Se arma con tools\build_win.bat o tools/build_linux.sh.
import os
import re

raiz = os.path.dirname(SPECPATH)

a = Analysis(
    [os.path.join(SPECPATH, "pelis_entrada.py")],
    pathex=[os.path.join(raiz, "src")],
    # __main__.py carga Path(__file__).parent / "qml": en el build es _internal\pelis\qml
    datas=[(os.path.join(raiz, "src", "pelis", "qml"), "pelis/qml")],
    hiddenimports=[],
    excludes=["tkinter", "PySide6.QtWidgets", "PySide6.QtMultimediaWidgets"],
)

# Los hooks de PySide6 juntan todos los módulos QML y sus DLL. La app usa QtQuick,
# QtQuick.Controls (Material), QtQuick.Layouts y QtMultimedia: se saca el resto.
QML_FUERA = (
    "Qt3D Qt5Compat QtCharts QtDataVisualization QtGraphs QtLocation QtPositioning "
    "QtQuick3D QtRemoteObjects QtScxml QtSensors QtTest QtTextToSpeech QtWebChannel "
    "QtWebEngine QtWebSockets QtWebView QtQuick/Dialogs QtQuick/LocalStorage "
    "QtQuick/NativeStyle QtQuick/Particles QtQuick/Pdf QtQuick/Scene2D QtQuick/Scene3D "
    "QtQuick/Timeline QtQuick/VectorImage QtQuick/VirtualKeyboard QtQuick/tooling "
    "QtQuick/Controls/FluentWinUI3 QtQuick/Controls/Fusion QtQuick/Controls/Imagine "
    "QtQuick/Controls/Native QtQuick/Controls/Universal QtQuick/Controls/Windows "
    "QtQuick/Controls/designer QtQuick/Shapes/DesignHelpers QtQml/DesignSupport "
    "QtQml/StateMachine QtQml/XmlListModel Qt/labs"
).split()
DLL_FUERA = re.compile(
    r"^(lib)?Qt6(3D|Quick3D|WebEngine|WebView|WebChannel|WebSockets|Charts|DataVisualization|Graphs"
    r"|Location|Positioning|Pdf|RemoteObjects|Scxml|Sensors|SpatialAudio|StateMachine"
    r"|TextToSpeech|VirtualKeyboard|QuickTimeline|QuickParticles|Test|QuickTest|QuickDialogs2"
    r"|Labs|QmlLocalStorage|QmlXmlListModel|Sql|QuickVectorImage|ShaderTools|MultimediaWidgets"
    r"|OpenGLWidgets|QmlDesignSupport|QuickShapesDesignHelpers"
    r"|QuickControls2(FluentWinUI3|Fusion|Imagine|Universal|Windows|Native))"
    r"|^opengl32sw\.dll$",
    re.IGNORECASE,
)
PLUGINS_FUERA = "qmltooling platforminputcontexts styles generic".split()


def se_queda(destino):
    d = destino.replace("\\", "/")
    if not d.startswith("PySide6/"):
        # En Linux las .so de Qt quedan en la raiz de _internal
        return not DLL_FUERA.search(os.path.basename(d))
    d = d[len("PySide6/"):]
    # En Linux Qt va bajo PySide6/Qt/ (qml, plugins, lib, translations)
    if d.startswith("Qt/"):
        d = d[len("Qt/"):]
    if d.startswith("translations/"):
        return False
    if d.startswith("qml/") and any(d[4:].startswith(m + "/") for m in QML_FUERA):
        return False
    if d.startswith("plugins/") and d.split("/")[1] in PLUGINS_FUERA:
        return False
    if d in ("plugins/imageformats/qpdf.dll", "plugins/imageformats/libqpdf.so"):
        return False
    return not DLL_FUERA.search(os.path.basename(d))


a.binaries = [x for x in a.binaries if se_queda(x[0])]
a.datas = [x for x in a.datas if se_queda(x[0])]

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pelis",
    console=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="pelis", upx=False)
