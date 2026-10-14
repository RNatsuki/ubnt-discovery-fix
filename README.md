# Ubiquiti Device Discovery Tool (Modern Suite)

Este repositorio contiene las soluciones completas y actualizadas para descubrir y administrar dispositivos Ubiquiti (antenas airMAX, equipos UniFi, routers EdgeMAX, airFiber, etc.) tanto en **Java Moderno** como en **Google Chrome**.

---

## 🚀 1. Extensión para Google Chrome / Chromium (Recomendada)
Revive la experiencia de la clásica extensión de Chrome con una interfaz moderna y soporte completo para Manifest V3.

### Instalación en 1 solo paso:
Ejecuta el script instalador en tu terminal:
```bash
./install.sh
```
El instalador se encarga automáticamente de:
1. Registrar el conector nativo UDP (puerto 10001) en Chrome, Chromium, Brave, Edge y Vivaldi.
2. Comprobar la conexión en tiempo real con los dispositivos de tu red.

### Activar la extensión en Chrome (solo la primera vez):
1. Abre tu navegador y dirígete a `chrome://extensions`.
2. Activa el interruptor **Modo de desarrollador** (esquina superior derecha).
3. Haz clic en **Cargar descomprimida** (*Load unpacked*).
4. Selecciona la carpeta `chrome-extension` de este repositorio.

¡Listo! Tendrás el icono oficial de Ubiquiti Discovery en tu barra de herramientas.

---

## ☕ 2. Versión de Escritorio JAR (Java 9, 11, 17, 21, 27+)
Corrige el error histórico de `ClassFormatError: Illegal field name "this.super"` provocado por ofuscadores antiguos (yGuard 2.0.3) al validar la especificación JVMS §4.2.2 en versiones modernas de Java.

### Ejecución:
```bash
./run.sh
```
O directamente:
```bash
java -jar ubnt-discovery-v2.5.1.jar
```

---

## 📁 Estructura del Proyecto
* [chrome-extension/](file:///home/ibarra/Desktop/discovery-to-java-new/chrome-extension/): Extensión completa Manifest V3 con interfaz moderna y soporte Native Messaging.
  * `ubnt_host.py`: Conector nativo UDP que escanea en el puerto 10001 por broadcast L2.
  * `popup.html`, `popup.css`, `popup.js`: Interfaz de usuario con tema oscuro tipo UniFi, búsqueda en tiempo real, detalles y exportación.
  * `manifest.json`: Manifiesto V3 con clave determinista permanente.
* [install.sh](file:///home/ibarra/Desktop/discovery-to-java-new/install.sh): Script de instalación automática del conector de Chrome.
* [ubnt-discovery-v2.5.1.jar](file:///home/ibarra/Desktop/discovery-to-java-new/ubnt-discovery-v2.5.1.jar): JAR de escritorio ya reparado y funcional.
* [ubnt-discovery-v2.5.1.jar.original](file:///home/ibarra/Desktop/discovery-to-java-new/ubnt-discovery-v2.5.1.jar.original): Respaldo original sin modificar.
* [patch_discovery.py](file:///home/ibarra/Desktop/discovery-to-java-new/patch_discovery.py): Script de parcheo de bytecode en Python.
* [run.sh](file:///home/ibarra/Desktop/discovery-to-java-new/run.sh): Lanzador para la versión JAR.
