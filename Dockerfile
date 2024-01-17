FROM node:lts as builder

ARG BWS_SDK_VERSION=0.4.0 \
    RUST_VERSION=1.75.0

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

# Install Rust
RUN dpkgArch="$(dpkg --print-architecture)" &&\
    case "${dpkgArch##*-}" in \
        amd64) rustArch='x86_64-unknown-linux-gnu' ;; \
        armhf) rustArch='armv7-unknown-linux-gnueabihf' ;; \
        arm64) rustArch='aarch64-unknown-linux-gnu' ;; \
        *) echo >&2 "unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac &&\
    url="https://static.rust-lang.org/rustup/dist/${rustArch}/rustup-init" &&\
    wget "$url" &&\
    chmod +x rustup-init &&\
    ./rustup-init -y --no-modify-path --profile minimal --default-host ${rustArch} &&\
    rm rustup-init &&\
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME &&\
    rustup --version &&\
    cargo --version &&\
    rustc --version

# Clone BWS SDK
RUN git clone https://github.com/bitwarden/sdk.git &&\
    cd sdk &&\
    git checkout bws-v${BWS_SDK_VERSION}

WORKDIR /sdk

# Compile Rust package
RUN cargo build --package bitwarden-py --release

# Generate schemas
RUN npm ci &&\
    npm run schemas

COPY build-reqs.txt .

# Compile Python bindings
RUN apt update &&\
    apt install -y python3-pip &&\
    rm /usr/lib/python3.*/EXTERNALLY-MANAGED || true &&\
    pip install -r build-reqs.txt &&\
    cd languages/python &&\
    python3 setup.py develop &&\
    mv bitwarden_py.*.so bitwarden_py.so &&\
    rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim-bookworm

ENV BWS_ORG_ID=
ENV BWS_ACCESS_TOKEN_FILE=
ENV BWS_ACCESS_TOKEN=
ENV SECRET_TOKEN_FILE=
ENV SECRET_TOKEN=
ENV LOG_LEVEL=INFO

WORKDIR /app

COPY server/reqs.txt .

RUN pip install -r reqs.txt &&\
    mkdir bitwarden_sdk

COPY server/ .

COPY --from=builder /sdk/languages/python/bitwarden_py.so .
COPY --from=builder /sdk/languages/python/bitwarden_sdk bitwarden_sdk

EXPOSE 5000

ENTRYPOINT [ "python", "server.py" ]
