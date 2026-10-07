"""
Prepara los datos institucionales (carpeta Datos/) en el formato que lee TRAYECTA.

Uso, desde la raíz del proyecto:
    .venv\\Scripts\\python.exe trayecta\\preparar_datos_reales.py

Escribe trayecta/datos_locales/materias.csv e ingreso.csv solo con Ingeniería de
Sistemas y SIN nombres ni datos personales (solo el código estudiantil). La carpeta
datos_locales/ está excluida de git: los archivos nunca salen del equipo.
Al abrir la aplicación aparece la opción «Cohortes reales» en la barra lateral.
"""
import os
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'Datos')
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datos_locales')
PROGRAMA = 'INGENIERIA DE SISTEMAS'


def main():
    os.makedirs(SALIDA, exist_ok=True)
    mat = pd.read_excel(os.path.join(DATOS, 'detalle_materias_recod.xlsx'))
    mat = mat[mat['PROGRAMA'].astype(str).str.upper().str.strip() == PROGRAMA]
    mat = mat[['CODIGO_INST', 'COHORTE', 'PERIODO_INSCRIPCION', 'CODIGO_MATERIA', 'MATERIA',
               'CREDITOS', 'DEFINITIVA', 'OBSERVACION']]
    car = pd.read_excel(os.path.join(DATOS, 'caracterización.xlsx'))
    car = car[car['PROGRAMA'].astype(str).str.upper().str.strip() == PROGRAMA]
    ing = car[['CODIGO_ESTUDIANTIL', 'PERIODO_INGRESO', 'PMATN', 'PCRIN', 'PNATN', 'PINGN', 'PCIUN']] \
        .rename(columns={'CODIGO_ESTUDIANTIL': 'CODIGO_INST', 'PERIODO_INGRESO': 'COHORTE'})
    mat.to_csv(os.path.join(SALIDA, 'materias.csv'), index=False, encoding='utf-8-sig')
    ing.to_csv(os.path.join(SALIDA, 'ingreso.csv'), index=False, encoding='utf-8-sig')
    print(f'Listo: {mat["CODIGO_INST"].nunique()} estudiantes con notas, {len(mat)} registros, '
          f'{len(ing)} con datos de ingreso -> {SALIDA}')


if __name__ == '__main__':
    main()
