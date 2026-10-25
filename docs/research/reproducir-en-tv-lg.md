# Reproducir una película de Pelis en el televisor LG «vector»

Investigado el 25/10/2026 desde la PC Linux (Mint, `wlp1s0`, 192.168.1.10).

## Respuesta corta

**Sí.** «vector» es el nombre que tiene el televisor en la red. El dispositivo se presenta como `[LG] vector` y es un **LG 32LM620BPSA** (32", HD, webOS 4.x, modelo 2019). Expone un **DLNA Digital Media Renderer** (UPnP `MediaRenderer:1` con `AVTransport`). Eso permite "empujar" una película desde la PC: la PC sirve el archivo por HTTP en la LAN y le dice al TV `SetAVTransportURI` + `Play`. El TV la decodifica él mismo, sin pasar por la pantalla de la PC. El renderer declara que acepta `video/x-matroska`, `video/mp4`, `video/avi` y `video/mp2t`, entre otros.

Tres caminos, de menor a mayor esfuerzo:

1. **Probar ya, sin código:** `go2tv` (Flatpak) con `-v pelicula.mkv -s pelicula.srt -t http://192.168.1.52:1067/`.
2. **Sin tocar la PC después de configurar:** `minidlna` sirviendo la carpeta `Peliculas/`. Se navega desde el TV con el control remoto, y el `.srt` con el mismo nombre que el video se ofrece como subtítulo.
3. **Integrado en Pelis:** un botón «Ver en el TV» en el Detalle. Usa `async_upnp_client` (Python, Apache-2.0) para AVTransport, más un pequeño servidor HTTP con soporte de `Range` dentro de la app.

**Recomendación:** primero el punto 1, para validar con 2 o 3 películas reales (códec y `.srt`). Si anda, pasar al punto 3, que reutiliza la biblioteca y el progreso de Pelis. Miracast y Chromecast no convienen o no aplican (ver la tabla).

**Sin verificar:** si este TV muestra el `.srt` externo cuando se le *empuja* el video (DLNA push). No lo probé porque mostraría algo en pantalla. Es lo primero a validar con go2tv.

---

## 1. Descubrimiento en la red (datos crudos)

Todo fue pasivo o de solo lectura: un M-SEARCH SSDP, la descarga de las descripciones XML, dos consultas SOAP de solo lectura (`GetProtocolInfo` y `GetTransportInfo`) y un `connect` TCP a cinco puertos. No hubo emparejamiento ni nada que se vea en el TV.

### SSDP (M-SEARCH `ssdp:all` a 239.255.255.250:1900)

Script: `ssdp.py` en el scratchpad de la sesión. Respondieron el router (192.168.1.1, IGD) y **192.168.1.52** (MAC `8c:19:b5:b5:0b:f2`, según `ip neigh`), con estos dispositivos raíz:

| LOCATION | SERVER | Tipo (ST/USN) |
|---|---|---|
| `http://192.168.1.52:1067/` | `Linux/i686 UPnP/1,0 DLNADOC/1.50 LGE WebOS TV/Version 0.9` | `urn:schemas-upnp-org:device:MediaRenderer:1` + servicios `AVTransport:1`, `ConnectionManager:1`, `RenderingControl:1` |
| `http://192.168.1.52:1171/` | `WebOS/1.5 UPnP/1.0 webOSTV/1.0` | `urn:dial-multiscreen-org:service:dial:1` (DIAL) |
| `http://192.168.1.52:1427/` | `WebOS/4.0.0 UPnP/1.0` | `urn:lge:device:tv:1` |
| `http://192.168.1.52:2043/` | `WebOS/4.1.0 UPnP/1.0` | `urn:lge-com:service:webos-second-screen:1` (`serviceId ...webos-second-screen-3000-3001`) |
| `http://192.168.1.52:9080` | `Linux/4.4.84-433, UPnP/1.0, Portable SDK for UPnP devices` | `urn:mdx-netflix-com:service:target:3` (`uuid:LGTV20194=...`, Netflix MDX) |

### Descripción del MediaRenderer (`curl http://192.168.1.52:1067/`)

```xml
<deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>
<friendlyName>[LG] vector</friendlyName>
<manufacturer>LG Electronics.</manufacturer>
<modelDescription>LG WebOSTV DMRplus</modelDescription>
<modelName>LG TV</modelName>
<dlna:X_DLNADOC>DMR-1.50</dlna:X_DLNADOC>
<serviceType>urn:schemas-upnp-org:service:AVTransport:1</serviceType>
<controlURL>/AVTransport/f39f6c8b-ef9e-383f-1011-a2810e819eb8/control.xml</controlURL>
```

### Modelo exacto (`curl http://192.168.1.52:1171/`, `:1427/` y `:2043/`)

```xml
<friendlyName>[LG] vector</friendlyName>
<modelName>32LM620BPSA</modelName>        <!-- :1171 (DIAL) y :1427 -->
<modelNumber>32LM620BPSA</modelNumber>    <!-- :2043 -->
<wifiMac>8C:19:B5:B5:0B:F2</wifiMac>  <wiredMac>B0:37:95:5B:04:4D</wiredMac>
```

Conclusión: «LG vector» no es un modelo. Es el nombre que el usuario le puso al TV, y webOS le antepone `[LG]`. El modelo es **32LM620BPSA**.

### Acciones de AVTransport (SCPD `/AVTransport/.../scpd.xml`)

`SetAVTransportURI`, `SetNextAVTransportURI`, `GetMediaInfo`, `GetTransportInfo`, `GetPositionInfo`, `GetDeviceCapabilities`, `GetTransportSettings`, `Stop`, `Play`, `Pause`, `Seek`, `Next`, `Previous` y `GetCurrentTransportActions`. Alcanza para reproducir, pausar, buscar (seek) y leer la posición, que es lo que necesita Pelis para guardar el progreso.

### Formatos que el renderer declara (`ConnectionManager#GetProtocolInfo`, campo `Sink`)

69 entradas. Tipos MIME de video: `video/avi`, `video/mp2t`, `video/mp2ts`, `video/mp4`, `video/mpeg`, `video/mts`, `video/vnd.dlna.mpeg-tts`, **`video/x-matroska`**, `video/x-ms-asf`, `video/x-ms-avi`, `video/x-ms-wmv` y `video/x-msvideo`. Audio: mp3, mp4/AAC, flac, wav, wma, ogg y LPCM. No declara ningún MIME de subtítulos (`text/srt`). Eso es normal: Sink lista los medios que reproduce, no los subtítulos.

`GetTransportInfo` → `CurrentTransportState=NO_MEDIA_PRESENT`, `CurrentTransportStatus=OK` (inactivo y listo).

### Otros chequeos

- Puertos TCP (solo `connect`): **3000 y 3001 abiertos** (webOS SSAP / second screen); 8008, 8009 (Chromecast) y 7250 (Miracast RTSP) cerrados.
- `avahi-browse -art` (mDNS/DNS-SD, 12 s, `avahi-daemon` activo): **sin ningún servicio** en la LAN. El TV no anuncia `_googlecast._tcp` ni `_airplay._tcp`.
- PC: VLC 3.0.20 instalado. Hay Flatpak. `minidlna`, `gerbera`, `rygel`, `gnome-network-displays` y `ffmpeg` no están instalados, pero están disponibles por apt (`apt-cache policy`). No hay `ffprobe` para revisar los códecs de cada película.
- Biblioteca de ejemplo: `Peliculas/Mikey And Nicky (1976)/Mikey And Nicky.mp4` + `Mikey And Nicky.srt`. Video y subtítulo tienen el mismo nombre base, como piden LG y minidlna (ver abajo).

## 2. Qué soporta el TV (fuentes de LG)

- **Plataforma:** la tabla oficial de LG asigna **webOS TV 4.x a los modelos 2018-2019** (https://webostv.developer.lge.com/develop/specifications/web-api-and-web-engine). Que el LM620 sea de 2019 con webOS 4.5 sale de fichas de comercios (fuente secundaria, p. ej. https://www.greentoe.com/product/LG_LM620B_32_Class_HDR_HD_Smart_LED_TV_32LM620BPUA). No encontré una ficha oficial de lg.com para el sufijo BPSA. Los headers SSDP dicen `WebOS/4.0.0` y `WebOS/4.1.0` según el servicio, lo que coincide con 4.x.
- **Contenedores y códecs** (LG, "AV Format on webOS TV 4.5": https://webostv.developer.lge.com/develop/specifications/video-audio-45; la de 4.0 es igual en estas filas: https://webostv.developer.lge.com/develop/specifications/video-audio-40):
  - `.mkv`: video MPEG-2, MPEG-4, **H.264/AVC**, VP8, VP9, **HEVC**. Audio Dolby Digital (AC-3), Dolby Digital Plus (E-AC-3), AAC, PCM, **DTS**, MP1/2/3.
  - `.mp4/.mov`: video H.264/AVC, MPEG-4, HEVC. Audio AC-3, E-AC-3, AAC, MP3 (**sin DTS**).
  - `.avi`: Xvid, H.264, MPEG-4. Audio MP3, AC-3, LPCM, DTS.
  - Límites Full HD ("All models"): `H.264 1920x1080@60P BP/MP/HP@L4.2 Maximum 40Mbps` y `HEVC 1920x1080@60P Main/Main10@L4.1 Maximum 40Mbps`. La fila de 4K es solo para "Ultra HD models", así que **un archivo 4K no se reproduce en este TV**, que es HD.
  - No soportados: AAC Main profile, y streams MPEG-4 con GMC o Qpel.
  - Sin AV1 (aparece recién en webOS 6.0: https://webostv.developer.lge.com/develop/specifications/video-audio-60).
- **Subtítulos** (LG Help Library, "Using subtitles on a connected USB device": https://www.lg.com/us/support/help-library/lg-tv-using-subtitles-on-a-connected-usb-device-CT10000018-20153220977838):
  - Externos: `smi, srt, sub, ass, ssa, txt, psb, dcs`. El video y el subtítulo deben compartir nombre. Si no se ven, LG recomienda guardarlo en **ANSI**. Ojo: muchos `.srt` de la biblioteca son UTF-8, porque `subtitulos.py` acepta UTF-8 o cp1252.
  - Embebidos: MKV con SSA/ASS/SRT; MP4 con Timed Text.
  - Sobre red, la página solo dice que **SMI** tiene "playback limitado en DLNA". No dice nada sobre `.srt` vía DLNA push.
  - Las páginas de developer solo listan WebVTT. Eso aplica a apps web, no al reproductor de USB/DLNA.

En la práctica: la mayoría de las películas H.264/HEVC 1080p en MKV o MP4 con AAC, AC-3 o DTS deberían reproducirse **sin transcodificar**. Necesitan transcodificación los 4K, los AV1, los H.264 por encima de L4.2 y los MP4 con audio DTS. Para saberlo por película hace falta `ffprobe` (paquete `ffmpeg`).

## 3. Opciones comparadas

| Vía | ¿Aplica a este TV? | Requisitos en la PC | Subtítulos `.srt` externos | Transcodifica | Integración en Pelis |
|---|---|---|---|---|---|
| **A. DLNA push (DMR / AVTransport)** | **Sí**, verificado: MediaRenderer en :1067 | Servidor HTTP con `Range` + control UPnP | Se pueden ofrecer, pero está **sin verificar** si este TV los muestra | No (el TV decodifica), salvo formatos fuera de la tabla | **Alta**: `async_upnp_client` + servidor HTTP propio |
| **B. Servidor DLNA (DMS) en la PC** (minidlna, Gerbera, Rygel) | Sí: el TV navega servidores DLNA desde su app de medios | `apt install minidlna` y configurar `media_dir` | minidlna sí, para LG: mismo nombre base `.srt` o `.smi` | No (minidlna) | Baja: es un servicio aparte y el progreso no vuelve a Pelis |
| **C. webOS SSAP (puertos 3000/3001)** | Sí, puertos abiertos | **Emparejamiento con aviso en el TV**, guardar la client key | No aporta nada sobre A | No | Media: sirve como control remoto (encender, cambiar de input), no para mandar el archivo |
| **D. Miracast / Screen Share** (`gnome-network-displays`) | El TV tiene Screen Share; el puerto 7250 está cerrado hasta activarlo | Wi-Fi P2P en la placa (rtw88_8822ce, sin verificar), paquete `gnome-network-displays` | Sí, porque refleja la pantalla con el reproductor de Pelis | **Sí**: codifica la pantalla en tiempo real | Ninguna: es duplicar la pantalla |
| **E. Chromecast / `catt`** | **No**: 8008/8009 cerrados, sin `_googlecast` en mDNS | — | — | — | — |
| **F. VLC renderer** | **No** con el VLC instalado: 3.0.20 solo trae `libstream_out_chromecast_plugin.so` como salida a renderer | — | — | — | — |

### A. DLNA push (recomendada)

- **Protocolo:** UPnP AV `AVTransport:1` (spec del UPnP Forum: https://upnp.org/specs/av/UPnP-av-AVTransport-v1-Service.pdf). `SetAVTransportURI(InstanceID=0, CurrentURI=<url http del archivo>, CurrentURIMetaData=<DIDL-Lite>)`, después `Play`. `Seek(Unit=REL_TIME)` y `GetPositionInfo` (`RelTime`) sirven para retomar y guardar el progreso. Las acciones están confirmadas en el SCPD del propio TV (sección 1).
- **Subtítulos:** go2tv, una herramienta que dice soportar TVs LG, mete el `.srt` en el DIDL de dos formas: un segundo `<res protocolInfo="http-get:*:text/srt:*">URL.srt</res>` y `<sec:CaptionInfo sec:type="srt">` / `<sec:CaptionInfoEx>` (estos son de Samsung). Ver `soapcalls/soapbuilders.go`, líneas ~510-522, en https://github.com/alexballas/go2tv. minidlna usa el mismo `<res ... text/srt>` para clientes LG (más abajo). **Hay que probar si este 32LM620 lo muestra en modo push**; no hay documentación de LG que lo afirme.
- **Herramienta para probar:** go2tv (MIT, activo: último push 21/10/2026, según https://api.github.com/repos/alexballas/go2tv). Instalación: `flatpak install flathub app.go2tv.go2tv` (trae FFmpeg). Uso: `go2tv -l` lista los renderers; `go2tv -v movie.mkv -s movie.srt -t <url>`; `-tc` transcodifica con FFmpeg (README: https://github.com/alexballas/go2tv). Según el README, "DLNA serves sidecars ... as SRT without transcoding".
- **Integración en Python:**
  - Control: `async_upnp_client` (Apache-2.0, https://github.com/StevenLooman/async_upnp_client). `profiles/dlna.py` tiene `class DmrDevice` con `async_set_transport_uri(media_url, media_title, meta_data)`, `async_play`, `async_pause`, `async_stop` y `async_seek_rel_time`. `meta_data` acepta un `str`, así que se le puede pasar un DIDL-Lite propio con el `<res>` del `.srt`. Es la biblioteca que usa Home Assistant para DLNA.
  - Servir el archivo: el TV pide el video por HTTP a la PC y necesita **Range requests** para buscar (seek). El `http.server` de la stdlib **no implementa Range**: `grep -i range /usr/lib/python3.12/http/server.py` no encuentra manejo de `Range`. Hace falta un handler propio (poco código) o un servidor que lo soporte. También hay que abrir el puerto en el firewall si lo hay, y usar la IP de la LAN (192.168.1.10) en la URL.
  - Encaja con la arquitectura actual: `puente.py` ya abre el video con el reproductor del sistema (`QDesktopServices.openUrl`, línea ~339). Un «Ver en el TV» iría al lado, como acción del Detalle. Leer `GetPositionInfo` cada pocos segundos alcanza para guardar el progreso en la base.

### B. Servidor DLNA en la PC

- minidlna (ReadyMedia). Config: `media_dir=V,/ruta/Peliculas`, `friendly_name`, e inotify para detectar archivos nuevos (`minidlna.conf`: https://sourceforge.net/p/minidlna/git/ci/master/tree/minidlna.conf).
- Subtítulos: `metadata.c::check_for_captions` busca `<mismo nombre>.srt` o `.smi` junto al video (https://sourceforge.net/p/minidlna/git/ci/master/tree/metadata.c). `clients.c` marca los clientes LG (User-Agent `LGE_DLNA_SDK`) con `FLAG_CAPTION_RES` (https://sourceforge.net/p/minidlna/git/ci/master/tree/clients.c). Con ese flag, `upnpsoap.c` agrega `<res protocolInfo="http-get:*:text/srt:*">http://.../Captions/<id>.srt</res>` (https://sourceforge.net/p/minidlna/git/ci/master/tree/upnpsoap.c, ~l.1177). Advertencia: el header de este TV dice `LGE WebOS TV/Version 0.9`, no `LGE_DLNA_SDK`. Hay que ver en el log de minidlna qué User-Agent manda el TV al navegar. Si no coincide, puede no recibir el `.srt`.
- Ventaja: cero código y funciona con el control remoto del TV. Desventaja: no se integra con el progreso ni la recomendación de Pelis, y queda un daemon corriendo. Las carpetas de la biblioteca (`Título (año)/Título.mp4`) ya cumplen la regla de "mismo nombre".
- Alternativas: Gerbera 2.0 y Rygel 0.42 están en apt. No las investigué a fondo; minidlna es la que tiene el caso LG documentado en su código.

### C. webOS SSAP (aiowebostv / pywebostv)

- El TV anuncia `webos-second-screen-3000-3001` (sección 1). `aiowebostv` (https://github.com/home-assistant-libs/aiowebostv) maneja un emparejamiento con `pairingType == "PROMPT"`: el TV muestra un aviso para aceptar y la `client_key` se guarda (`webos_client.py`). Endpoints útiles: `media.controls/play|pause|stop`, `system.launcher/launch` y `system.launcher/open` (`endpoints.py`).
- No sirve para mandar un archivo local mejor que DLNA. Sirve como complemento (prender o cambiar de app). No lo probé, por la regla de no emparejar.

### D. Miracast (Screen Share)

- LG documenta Screen Share por Miracast desde una PC: https://www.lg.com/us/support/help-library/pc-screen-sharing-using-miracast-webos-video-CT10000018-1441913330803. En Linux, `gnome-network-displays` "Supports the Miracast and Chromecast protocols" (https://gitlab.gnome.org/GNOME/gnome-network-displays).
- Duplica la pantalla: re-codifica en tiempo real, con más latencia y menos calidad, y depende de que la placa Wi-Fi soporte P2P. Lo uso solo como plan B, para ver el reproductor de Pelis tal cual (con sus subtítulos con estilo).

### E y F. Chromecast, catt, VLC

- No hay Chromecast built-in: 8008 y 8009 cerrados, sin anuncio mDNS. `catt` solo habla Chromecast, así que queda descartado.
- VLC 3.0.20 (el instalado) solo trae el módulo `stream_out_chromecast` como destino de "Renderizador" (`ls /usr/lib/x86_64-linux-gnu/vlc/plugins/stream_out`). Su `libupnp_plugin` es de *services discovery* (navegar servidores), no de renderers. Como fuente **secundaria**, hay usuarios que reportan que VLC 3.0.x no ve al LG webOS como renderer: https://forum.videolan.org/viewtopic.php?p=514188.

## 4. Siguientes pasos sugeridos

1. `flatpak install flathub app.go2tv.go2tv` y probar con `Mikey And Nicky.mp4` + `.srt`. Anotar si se ven los subtítulos, si anda el seek y si el `.srt` en UTF-8 sale bien o hay que pasarlo a cp1252/ANSI.
2. Si los subtítulos no salen en push, probar minidlna, que navega desde el TV. Como último recurso, transcodificar quemando subtítulos (`go2tv -tc`, más CPU).
3. Si (1) anda: abrir un issue en `.scratch/` para «Ver en el TV». Alcance: `async_upnp_client` + servidor HTTP con Range + DIDL con `<res text/srt>` + sondeo de `GetPositionInfo` para el progreso.
