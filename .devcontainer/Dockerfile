FROM ghcr.io/astral-sh/uv:python3.12-bookworm

RUN echo "Acquire::http::Proxy \"http://10.1.10.168:3142\";" > /etc/apt/apt.conf.d/00aptproxy
