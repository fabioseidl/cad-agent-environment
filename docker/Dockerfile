# CAD modeling environment for agents: build123d + OpenCASCADE, headless.
#
# build123d 0.13 requires Python >=3.11,<3.15. 3.12 is the conservative choice:
# cadquery-ocp-novtk ships wheels for it on linux/amd64 and linux/arm64.
FROM python:3.12-slim-bookworm

# OpenCASCADE (OCP) links against libGL/libX11 even for headless use, and
# fontconfig is required by build123d's Text()/font features.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libx11-6 \
        libxext6 \
        libexpat1 \
        fontconfig \
        fonts-dejavu-core \
        git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/mpl \
    XDG_CACHE_HOME=/tmp/cache \
    PYTHONPATH=/work/.agents/tools

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Fail the build if the headless import chain is broken.
RUN python -c "import build123d, matplotlib, yaml; \
from build123d import Box; \
assert abs(Box(10, 10, 10).volume - 1000) < 1e-6; \
print('build123d', build123d.__version__, 'OK')"

WORKDIR /work
ENTRYPOINT ["python", "-m", "cadkit.cli"]
CMD ["--help"]
