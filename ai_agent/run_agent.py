# ai_agent/run_agent.py
import argparse
import time
from ai_agent.test_generator import TestGenerator

def run_pipeline(app, export, fallback, source, full):
    """Ejecuta features (+ steps si full) para una fuente dada."""
    # Instancia el generador para la fuente solicitada
    try:
        generator = TestGenerator(
            fast_mode=False,
            app_name=app,
            export=export,
            fallback=fallback,
            source=source,             # TestGenerator debe aceptar 'source'
        )
    except TypeError:
        # Fallback si aún no has agregado 'source' en el __init__
        generator = TestGenerator(
            fast_mode=False,
            app_name=app,
            export=export,
            fallback=fallback,
        )

    print(f"\n🧪 [{source}] Generación de features")
    generator.generate_tests()

    if full:
        # pequeña pausa para evitar condiciones de escritura
        time.sleep(2)
        print(f"🔁 [{source}] Conversión a steps")
        generator.convert_to_steps(prefix=app or "")
        try:
            generator.save_log("/app/outputs/features", mode=f"E2E-{source.upper()}")
        except TypeError:
            generator.save_log("/app/outputs/features")
    else:
        try:
            generator.save_log("/app/outputs/features", mode=f"features-{source.upper()}")
        except TypeError:
            generator.save_log("/app/outputs/features")

def main():
    parser = argparse.ArgumentParser(description="🤖 AI Agent - Generador Inteligente de Pruebas")
    parser.add_argument("--app", type=str, help="Nombre de la app (ej: quotations)")
    parser.add_argument("--export", action="store_true", help="Exporta a /app/outputs/features/")
    parser.add_argument("--fallback", action="store_true", help="Analiza todo el proyecto si no hay app")
    parser.add_argument("--convert", action="store_true", help="Solo convertir features existentes a steps")
    parser.add_argument("--full", action="store_true", help="Ciclo completo: features → steps")
    parser.add_argument("--source", choices=["backend","frontend"], default="backend",
                        help="Fuente única: backend (Django) o frontend (React)")
    parser.add_argument("--both", action="store_true",
                        help="Procesa backend y frontend en la misma ejecución")

    args = parser.parse_args()
    print("\n🧠 Iniciando el agente con modo debug...\n")

    try:
        # SOLO conversión (usa los features ya existentes)
        if args.convert and not args.both:
            print("🔁 Modo conversión de .feature → steps")
            run_pipeline(args.app, args.export, args.fallback, args.source, full=True)
            return

        # AMBAS FUENTES
        if args.both:
            sources = ["backend", "frontend"]
            full = True if args.full or args.convert else args.full
            print("🧩 Modo BOTH activado (backend + frontend)")
            for src in sources:
                run_pipeline(args.app, args.export, args.fallback, src, full=full)
            print("\n🎯 BOTH finalizado.")
            return

        # UNA SOLA FUENTE
        if args.full:
            run_pipeline(args.app, args.export, args.fallback, args.source, full=True)
        else:
            run_pipeline(args.app, args.export, args.fallback, args.source, full=False)

    except KeyboardInterrupt:
        print("\n⛔ Interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución del agente: {e}")

if __name__ == "__main__":
    main()
