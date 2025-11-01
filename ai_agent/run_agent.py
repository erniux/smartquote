# ai_agent/run_agent.py
import argparse
import time
from ai_agent.test_generator import TestGenerator

def run_pipeline(app, export, fallback, source, full, fast):
    """Ejecuta features (+ log) para una fuente dada."""
    print(f"\n🧪 [{source}] Generación de features | fast_mode={'ON' if fast else 'OFF'}")
    try:
        generator = TestGenerator(
            fast_mode=fast,
            app_name=app,
            export=export,
            fallback=fallback,
            source=source,   # 'backend' o 'frontend'
        )
    except TypeError:
        # compatibilidad por si la firma del ctor cambia
        generator = TestGenerator(
            fast_mode=fast,
            app_name=app,
            export=export,
            fallback=fallback,
        )

    generator.generate_tests()

    # Pequeña pausa para asegurarnos de que el FS terminó de escribir
    time.sleep(1)

    # Guardar log/README (independiente de full/convert, ya no generamos steps aquí)
    mode_label = f"features-{source.upper()}" if not full else f"E2E-{source.upper()}"
    #try:
    #    generator.save_log("/app/bdd/tests/features", mode=mode_label)
    #except TypeError:
    #    generator.save_log("/app/bdd/tests/features")  # compat

def main():
    parser = argparse.ArgumentParser(description="🤖 AI Agent - Generador Inteligente de Pruebas")
    parser.add_argument("--app", type=str, help="Nombre de la app (ej: quotations)")
    parser.add_argument("--export", action="store_true", help="Exporta a /app/outputs/features/")
    parser.add_argument("--fallback", action="store_true", help="Analiza todo el proyecto si no hay app")
    parser.add_argument("--convert", action="store_true", help="(Legacy) Solo convertir features a steps")
    parser.add_argument("--full", action="store_true", help="Etiqueta de modo completo (no genera steps aquí)")
    parser.add_argument("--source", choices=["backend","frontend"], help="Fuente única. Si se omite, corre ambas.")
    parser.add_argument("--fast", action="store_true", help="Modo rápido (menos contexto y salida acotada)")

    args = parser.parse_args()
    print("\n🧠 Iniciando el agente con modo debug...\n")

    try:
        # Si no se especifica --source, corremos ambas fuentes
        sources = [args.source] if args.source else ["backend", "frontend"]
        if len(sources) == 2:
            print("🧩 Modo BOTH activado (backend + frontend)")

        # Ruta legacy de --convert: ya NO generamos steps aquí (usa behave_stepgen.py)
        if args.convert:
            for src in sources:
                run_pipeline(args.app, args.export, args.fallback, src, full=True, fast=args.fast)
            print("\n🎯 Conversión/listado completado (usa behave_stepgen.py para steps).")
            return

        # Generación normal
        for src in sources:
            run_pipeline(args.app, args.export, args.fallback, src, full=args.full, fast=args.fast)

        print("\n🎯 Ejecución finalizada.")
    except KeyboardInterrupt:
        print("\n⛔ Interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución del agente: {e}")

if __name__ == "__main__":
    main()
