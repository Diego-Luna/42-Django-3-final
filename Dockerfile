FROM debian:bookworm

# Evitar interacciones durante la instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instalar paquetes necesarios y herramientas adicionales
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    gettext \
    zsh \
    git \
    curl \
    wget \
    vim \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Configurar zsh como shell por defecto
RUN chsh -s /usr/bin/zsh root

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt .

# Crear y activar entorno virtual, luego instalar dependencias
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto 8000
EXPOSE 8000

# Comando por defecto: mantener el contenedor corriendo
CMD ["tail", "-f", "/dev/null"]