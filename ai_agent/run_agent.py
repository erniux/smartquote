import argparse
from ai_agent.test_generator import ApiTestGenerator
from ai_agent.feature_generator import FeatureGenerator


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

    args = parser.parse_args()

    print("\n🧠 Iniciando el agente con modo debug...\n")

    try:
        generator = ApiTestGenerator(
            fast_mode=args.fast,
            app_name=args.app,
            export=args.export,
            fallback=args.fallback,
        )
        generator.generate_tests()
    except KeyboardInterrupt:
        print("\n⛔ Ejecución interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución del agente: {e}")


if __name__ == "__main__":
    print("\n🧠 Iniciando el agente con modo debug...\n")

    try:
        generator = ApiTestGenerator(
            fast_mode=False,
            app_name=None,
            export=True,
            fallback=True,
        )
        generator.generate_tests()

        # 🔧 Generar features desde el código real del backend
        feature_gen = FeatureGenerator(
            source_path="/workspace/backend",
            output_dir="/workspace/ai_agent/features"
        )
        #feature_gen.generate_feature_files()

    except KeyboardInterrupt:
        print("\n⛔ Ejecución interrumpida por el usuario.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ Error crítico en la ejecución del agente: {e}")


