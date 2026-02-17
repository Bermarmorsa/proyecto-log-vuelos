from loguru import logger
from log_vuelos.utils.logger import inicializar_logger


def main():
    # 1. Configuramos antes de hacer cualquier otra cosa
    inicializar_logger()

    logger.info("Sistema de logs listo. ¡Arrancamos! 🚀")

    # Aquí llamaríamos a otras funciones de otros módulos...


if __name__ == "__main__":
    main()


