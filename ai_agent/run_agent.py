import argparse
from ai_agent.test_generator import TestGenerator


def main():
    parser = argparse.ArgumentParser(
        description="🤖 AI Agent - Generador Inteligente de Pruebas Automatizadas"
    )

    parser.add_argument(
        "--app",
        type=str,
        help="Nombre de la app a procesar (por ejemplo: quotations, sales, products)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Modo rápido: procesa solo los primeros 3 archivos.",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Exporta el archivo generado a /app/outputs/features/",
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Si no se encuentra la app, analiza todo el proyecto.",
    )

    parser.add_argument(
        "--convert", 
        action="store_true", 
        help="Convierte archivos .feature en archivos steps de pytest-bdd")


    args = parser.parse_args()

    print("\n🧠 Iniciando el agente con modo debug...\n")

    try:
        generator = TestGenerator(
            fast_mode=args.fast,
            app_name=args.app,
            export=args.export,
            fallback=args.fallback,
        )
        if args.convert:
            print("🔁 Modo conversión de .feature → steps activado...")
            generator.convert_to_steps(prefix=args.app or "")
        else:
            generator.generate_tests()
         
    except KeyboardInterrupt:
        print("\n⛔ Ejecución interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución del agente: {e}")


if __name__ == "__main__":
    main()
     

