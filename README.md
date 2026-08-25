# Generador de calendario A4

Una utilidad pequeña de línea de comandos que crea un calendario mensual listo para imprimir en **A4 horizontal**. Usa un diseño blanco de trazos rectos, celdas imposibles tachadas y etiquetas cuadradas, más grandes y alineadas, para las fechas válidas.

## Requisito

Python 3.9 o posterior y [ReportLab](https://www.reportlab.com/opensource/):

```powershell
python -m pip install reportlab
```

## Uso

Desde esta carpeta:

```powershell
python calendar_generator.py 2026 8
```

Esto crea `calendario-2026-08.pdf` en la carpeta actual. Para elegir otro destino:

```powershell
python calendar_generator.py 2026 8 --output .\mi-calendario.pdf
```

Para crear los doce meses de un año en un solo PDF:

```powershell
python calendar_generator.py 2026
```

Esto crea `calendario-2026-01.pdf`; el sufijo indica el mes inicial del PDF.

Para crear desde el mes actual hasta diciembre del año actual:

```powershell
python calendar_generator.py --from-current-month
```

El archivo usa el año y mes de inicio, por ejemplo `calendario-2026-08.pdf`.

Al imprimir, seleccione **A4**, **orientación horizontal** y **tamaño real / 100 %**. El diseño llega hasta los bordes de la página; use impresión sin bordes si su impresora la admite.

## Argumentos

- `year`: año entre 1 y 9999. Sin `month`, genera el año completo.
- `month`: número de mes opcional de 1 (enero) a 12 (diciembre).
- `--from-current-month`: genera desde el mes actual hasta diciembre, sin indicar año ni mes.
- `-o`, `--output`: ruta opcional del PDF de salida.
