FROM python:3.12-bookworm as builder

# renovate: datasource=github-releases depName=bitwarden/sdk
# TODO: pin to release tag when new release published on bitwarden/sdk; depends on aef6a21
# ARG BWS_SDK_VERSION=0.4.0
ARG BWS_SDK_BRANCH=main

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

# Install Rust & Node
RUN dpkgArch="$(dpkg --print-architecture)" &&\
    case "${dpkgArch##*-}" in \
        amd64) rustArch='x86_64-unknown-linux-gnu' ;; \
        armhf) rustArch='armv7-unknown-linux-gnueabihf' ;; \
        arm64) rustArch='aarch64-unknown-linux-gnu' ;; \
        *) echo >&2 "unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac &&\
    url="https://static.rust-lang.org/rustup/dist/${rustArch}/rustup-init" &&\
    wget -q "$url" &&\
    chmod +x rustup-init &&\
    ./rustup-init -y --no-modify-path --profile minimal --default-host ${rustArch} &&\
    rm rustup-init &&\
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME &&\
    rustup --version &&\
    cargo --version &&\
    rustc --version &&\
    apt update &&\
    apt-get install -y --no-install-recommends npm &&\
    rm -rf /var/lib/apt/lists/*

# Clone BWS SDK
RUN git clone https://github.com/bitwarden/sdk.git &&\
    cd sdk &&\
    [ -n "${BWS_SDK_VERSION}" ] && git checkout bws-v${BWS_SDK_VERSION} || git checkout ${BWS_SDK_BRANCH}

WORKDIR /sdk

# Generate schemas
RUN npm ci &&\
    npm run schemas

COPY build-requirements.txt .

# Compile Python bindings
RUN pip install --no-cache -r build-requirements.txt &&\
    cd languages/python &&\
    maturin build --compatibility linux

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

ENV ORG_ID=
ENV SECRET_TTL=
ENV DEBUG=false

WORKDIR /app

COPY server/requirements.txt .
COPY --from=builder /sdk/target/wheels/bitwarden_sdk*.whl .

RUN find . -name "bitwarden_sdk*.whl" -exec pip install --no-cache-dir -r requirements.txt {} \; &&\
    rm -v bitwarden_sdk*.whl

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "python", "server.py" ]
