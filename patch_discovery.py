#!/usr/bin/env python3
"""
Script para reparar Ubiquiti Device Discovery Tool (ubnt-discovery-v2.5.1.jar)
para que sea compatible con Java 9, 11, 17, 21, 27+ y distribuciones Linux modernas.

Causas de los problemas originales:
1. JVMS 4.2.2 (Java 9+):
   El JAR fue ofuscado antiguamente con yGuard 2.0.3, el cual generaba nombres
   de identificadores ilegales con puntos (ej: "this.super", "int.Object", "private.super")
   en campos y metodos. Las versiones antiguas de Java (Java 8 y anteriores) lo toleraban,
   pero las versiones modernas de la JVM verifican estrictamente la especificacion JVMS 4.2.2,
   arrojando `java.lang.ClassFormatError: Illegal field name ...`.

2. Lanzamiento del Navegador Web en Linux ("Failed launching WEB browser"):
   En Linux, el JAR original invoca directamente el comando Debian-especifico `sensible-browser`.
   En distribuciones como Arch Linux, Fedora, RHEL, openSUSE, Alpine, etc., este binario no
   existe por defecto, provocando el error `Failed launching WEB browser. Please, open http://... manually`.
   Este script sustituye la referencia a `sensible-browser` por el estandar universal freedesktop `xdg-open`.
"""

import sys
import zipfile
import struct

def patch_class(data: bytes) -> bytes:
    if len(data) < 10 or data[:4] != b"\xca\xfe\xba\xbe":
        return data

    # Parche de navegador web: reemplazar sensible-browser (Debian) por xdg-open (estandar Linux)
    if b"\x01\x00\x10sensible-browser" in data:
        data = data.replace(b"\x01\x00\x10sensible-browser", b"\x01\x00\x08xdg-open")

    minor, major, cp_count = struct.unpack(">HHH", data[4:10])
    idx = 10
    cp = [None] * cp_count
    cp_offsets = [None] * cp_count
    i = 1
    while i < cp_count:
        cp_offsets[i] = idx
        tag = data[idx]
        idx += 1
        if tag == 1: # Utf8
            length = struct.unpack(">H", data[idx:idx+2])[0]
            idx += 2
            val = data[idx:idx+length]
            idx += length
            cp[i] = (tag, val, cp_offsets[i] + 3, length)
        elif tag in (3, 4): # Integer, Float
            idx += 4
            cp[i] = (tag,)
        elif tag in (5, 6): # Long, Double (takes 2 entries)
            idx += 8
            cp[i] = (tag,)
            i += 1
        elif tag in (7, 8): # Class, String
            val = struct.unpack(">H", data[idx:idx+2])[0]
            idx += 2
            cp[i] = (tag, val)
        elif tag in (9, 10, 11, 12): # Fieldref, Methodref, InterfaceMethodref, NameAndType
            v1, v2 = struct.unpack(">HH", data[idx:idx+4])
            idx += 4
            cp[i] = (tag, v1, v2)
        elif tag in (15,): # MethodHandle
            idx += 3
            cp[i] = (tag,)
        elif tag in (16, 19, 20): # MethodType, Module, Package
            idx += 2
            cp[i] = (tag,)
        elif tag in (18,): # InvokeDynamic
            idx += 4
            cp[i] = (tag,)
        else:
            return data
        i += 1

    access_flags, this_class, super_class, interfaces_count = struct.unpack(">HHHH", data[idx:idx+8])
    idx += 8 + interfaces_count * 2

    # Campos
    fields_count = struct.unpack(">H", data[idx:idx+2])[0]
    idx += 2
    target_indices = set()
    for _ in range(fields_count):
        fa, fn, fd, ac = struct.unpack(">HHHH", data[idx:idx+8])
        idx += 8
        target_indices.add(fn)
        for _ in range(ac):
            attr_name_idx, attr_len = struct.unpack(">HI", data[idx:idx+6])
            idx += 6 + attr_len

    # Metodos
    methods_count = struct.unpack(">H", data[idx:idx+2])[0]
    idx += 2
    for _ in range(methods_count):
        ma, mn, md, ac = struct.unpack(">HHHH", data[idx:idx+8])
        idx += 8
        target_indices.add(mn)
        for _ in range(ac):
            attr_name_idx, attr_len = struct.unpack(">HI", data[idx:idx+6])
            idx += 6 + attr_len

    # Referencias NameAndType
    for item in cp:
        if item and item[0] == 12: # NameAndType
            target_indices.add(item[1])

    bdata = bytearray(data)
    for tidx in target_indices:
        entry = cp[tidx]
        if entry and entry[0] == 1:
            val = entry[1]
            if b"." in val:
                new_val = val.replace(b".", b"_")
                val_offset = entry[2]
                val_len = entry[3]
                bdata[val_offset:val_offset+val_len] = new_val

    return bytes(bdata)

def patch_jar(input_jar: str, output_jar: str):
    print(f"Reparando {input_jar} -> {output_jar}...")
    with zipfile.ZipFile(input_jar, "r") as zin:
        with zipfile.ZipFile(output_jar, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                content = zin.read(item.filename)
                if item.filename.endswith(".class"):
                    content = patch_class(content)
                zout.writestr(item, content)
    print("Reparacion completada con exito.")

if __name__ == "__main__":
    in_jar = sys.argv[1] if len(sys.argv) > 1 else "ubnt-discovery-v2.5.1.jar"
    out_jar = sys.argv[2] if len(sys.argv) > 2 else "ubnt-discovery-v2.5.1-fixed.jar"
    patch_jar(in_jar, out_jar)
