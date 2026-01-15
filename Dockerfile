# Use Python on Debian Trixie (testing)
FROM python:3.12-slim-trixie

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for AgenTTY:
# - openssh-client: for start_ssh
# - telnet: for start_telnet
# - procps: useful for process management in terminal
# - Network tools: curl, wget, ping, net-tools, dnsutils, ip
# - Dev tools: git, vim, nano, tree, jq, zip, unzip
# - Debug tools: lsof, netcat, traceroute
# - Sudo: for privilege escalation
# - Expert Network Tools: nmap, tcpdump, mtr, socat, iperf3, rsync, ethtool
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    telnet \
    procps \
    curl \
    wget \
    iputils-ping \
    net-tools \
    dnsutils \
    iproute2 \
    git \
    vim \
    nano \
    tree \
    jq \
    zip \
    unzip \
    lsof \
    netcat-openbsd \
    traceroute \
    sudo \
    nmap \
    tcpdump \
    mtr-tiny \
    socat \
    iperf3 \
    rsync \
    ethtool \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . /app

# Install the package
RUN pip install --no-cache-dir .

# Create a non-root user for security, but give it sudo access for the benchmark
RUN useradd -m -s /bin/bash agent && \
    echo "agent ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/agent && \
    chmod 0440 /etc/sudoers.d/agent && \
    chown -R agent:agent /app

USER agent

# Default entrypoint
ENTRYPOINT ["agentty"]
