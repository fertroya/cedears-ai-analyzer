#!/bin/bash
# Script de instalación automática de Ollama para macOS y Linux
# Este script verifica si Ollama está instalado y lo instala si es necesario

set -e

OLLAMA_VERSION="latest"
OLLAMA_URL_MACOS="https://ollama.com/download/Ollama-darwin"
OLLAMA_URL_LINUX="https://ollama.com/download/ollama-linux-amd64"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Verificación e Instalación de Ollama ===${NC}\n"

# Función para verificar si Ollama está instalado
check_ollama_installed() {
    if command -v ollama &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Función para verificar si Ollama está corriendo
check_ollama_running() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Función para instalar Ollama en macOS
install_ollama_macos() {
    echo -e "${YELLOW}Instalando Ollama en macOS...${NC}"
    
    if command -v brew &> /dev/null; then
        echo "Instalando con Homebrew..."
        brew install ollama
    else
        echo -e "${YELLOW}Homebrew no encontrado. Descargando instalador...${NC}"
        echo "Por favor, descarga e instala Ollama desde: https://ollama.com/download"
        echo "O instala Homebrew primero: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Función para instalar Ollama en Linux
install_ollama_linux() {
    echo -e "${YELLOW}Instalando Ollama en Linux...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
}

# Función para iniciar Ollama
start_ollama() {
    echo -e "${YELLOW}Iniciando servicio Ollama...${NC}"
    
    # Detectar sistema operativo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - iniciar como servicio de fondo
        ollama serve > /dev/null 2>&1 &
        sleep 3
    else
        # Linux - iniciar como servicio
        ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
    
    # Verificar que se inició correctamente
    if check_ollama_running; then
        echo -e "${GREEN}✓ Ollama está corriendo${NC}"
    else
        echo -e "${RED}✗ Error: Ollama no se pudo iniciar${NC}"
        echo "Intenta iniciarlo manualmente con: ollama serve"
        exit 1
    fi
}

# Función para descargar modelo
download_model() {
    local model=$1
    echo -e "${YELLOW}Descargando modelo: ${model}...${NC}"
    echo "Esto puede tomar varios minutos dependiendo de tu conexión..."
    
    ollama pull "$model"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Modelo ${model} descargado exitosamente${NC}"
    else
        echo -e "${RED}✗ Error al descargar modelo ${model}${NC}"
        exit 1
    fi
}

# Verificar sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo -e "${RED}Error: Sistema operativo no soportado: $OSTYPE${NC}"
    echo "Por favor, instala Ollama manualmente desde https://ollama.com"
    exit 1
fi

# Verificar si Ollama está instalado
if check_ollama_installed; then
    OLLAMA_VERSION_INSTALLED=$(ollama --version 2>/dev/null || echo "installed")
    echo -e "${GREEN}✓ Ollama ya está instalado${NC}"
    echo "  Versión: $OLLAMA_VERSION_INSTALLED"
else
    echo -e "${YELLOW}Ollama no está instalado. Instalando...${NC}"
    
    if [ "$OS" == "macos" ]; then
        install_ollama_macos
    else
        install_ollama_linux
    fi
    
    if check_ollama_installed; then
        echo -e "${GREEN}✓ Ollama instalado exitosamente${NC}"
    else
        echo -e "${RED}✗ Error: Ollama no se pudo instalar${NC}"
        exit 1
    fi
fi

# Verificar si Ollama está corriendo
if check_ollama_running; then
    echo -e "${GREEN}✓ Ollama está corriendo${NC}"
else
    echo -e "${YELLOW}Ollama no está corriendo. Iniciando...${NC}"
    start_ollama
fi

# Verificar modelo por defecto (llama3)
echo -e "\n${YELLOW}Verificando modelo por defecto (llama3)...${NC}"
if ollama list | grep -q "llama3"; then
    echo -e "${GREEN}✓ Modelo llama3 ya está disponible${NC}"
else
    echo -e "${YELLOW}Modelo llama3 no encontrado. Descargando...${NC}"
    download_model "llama3"
fi

echo -e "\n${GREEN}=== Setup completado ===${NC}"
echo -e "Ollama está listo para usar."
echo -e "Modelos disponibles:"
ollama list

echo -e "\n${GREEN}Para probar Ollama, ejecuta:${NC}"
echo "  ollama run llama3 'Hola, ¿cómo estás?'"
