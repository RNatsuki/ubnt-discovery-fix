# Ubiquiti Device Discovery Tool (Modern Java Compatibility Patch)

Versión reparada y adaptada de **Ubiquiti Device Discovery Tool v2.5.1** para ser compatible con versiones modernas de Java (Java 9, 11, 17, 21, 27+).

## Causa del problema
El archivo original `ubnt-discovery-v2.5.1.jar` fue ofuscado con **yGuard 2.0.3**, el cual renombraba variables y métodos con nombres que contenían puntos (ej. `this.super`, `int.Object`, etc.). Las versiones clásicas de Java (Java 8 y anteriores) lo permitían, pero a partir de **Java 9** la JVM valida estrictamente la especificación **JVMS §4.2.2**, arrojando el error:

```text
Exception in thread "main" java.lang.ClassFormatError: Illegal field name "this.super" in class com/OoOO/super/A/o0oO
```

## Solución implementada
El script `patch_discovery.py` lee el *Constant Pool* de todas las clases dentro del JAR y reemplaza los puntos en nombres de campos, métodos y descriptores `NameAndType` por guiones bajos (`_`), preservando la estructura y el tamaño del bytecode sin requerir recompilación ni código fuente original.

## Requisitos
- Java JRE/JDK 8, 11, 17, 21, 27 o superior.
- Python 3 (únicamente si se desea volver a ejecutar el parcheador).

## Ejecución
Puede ejecutarse mediante el script:
```bash
./run.sh
```

O directamente con Java:
```bash
java -jar ubnt-discovery-v2.5.1.jar
```

## Estructura de archivos
- `ubnt-discovery-v2.5.1.jar`: Archivo JAR ya parcheado y funcional.
- `ubnt-discovery-v2.5.1.jar.original`: Respaldo del archivo JAR original sin modificar.
- `patch_discovery.py`: Script en Python utilizado para corregir el bytecode en el constant pool.
- `run.sh`: Script ejecutable para lanzar la herramienta.
