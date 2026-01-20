  FROM node:20

  ARG TZ
  ARG CLAUDE_CODE_VERSION=1
  ARG GIT_DELTA_VERSION
  ARG ZSH_IN_DOCKER_VERSION
  
  ENV TZ="${TZ}"
  
  # ---------- 基本ツール ------------------------------------------------
  RUN set -eux; \
      apt-get update && \
      apt-get install -y --no-install-recommends \
        git procps sudo fzf zsh man-db unzip gnupg2 gh \
        iptables ipset iproute2 dnsutils aggregate jq less \
        curl wget ca-certificates \
        tree \
      && apt-get clean && rm -rf /var/lib/apt/lists/* && \
      \
      # 2) AWS CLI v2 （アーキテクチャ自動判定）
      ARCH="$(dpkg --print-architecture)"; \
      case "$ARCH" in \
        amd64) AWS_ARCH="x86_64" ;; \
        arm64) AWS_ARCH="aarch64" ;; \
        *)     echo "Unsupported architecture: ${ARCH}" && exit 1 ;; \
      esac; \
      curl -sSL "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o /tmp/awscliv2.zip && \
      unzip -q /tmp/awscliv2.zip -d /tmp && \
      /tmp/aws/install && \
      rm -rf /tmp/aws /tmp/awscliv2.zip
  
  # ---------- NPM グローバル領域 --------------------------------------
  RUN mkdir -p /usr/local/share/npm-global && chown -R node:node /usr/local/share
  
  # ---------- bash history 永続化用ディレクトリ ----------------------------
  RUN mkdir -p /commandhistory \
      && touch /commandhistory/.bash_history \
      && chmod 777 /commandhistory/.bash_history
  
  ENV DEVCONTAINER=true
  
  # ---------- ワークスペース ------------------------------------------
  # /home/node/.claude /home/node/.codex は volume / bind mount の受け皿
  RUN mkdir -p /workspace /home/node/.claude /home/node/.codex /home/node/.gemini \
      && chown -R node:node /workspace /home/node/.claude /home/node/.codex /home/node/.gemini
  
  WORKDIR /workspace
  
  # ---------- git-delta ------------------------------------------------
  RUN ARCH=$(dpkg --print-architecture) && \
      wget -q "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
      dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
      rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"
  
  # ---------- 非 root ユーザ ------------------------------------------
  USER node
  
  ENV NPM_CONFIG_PREFIX=/usr/local/share/npm-global
  ENV PATH=$PATH:/usr/local/share/npm-global/bin
  # postinstall の権限切替を抑制（npm は ENV を拾います）
  ENV NPM_CONFIG_UNSAFE_PERM=true
  ENV SHELL=/bin/zsh
  
  # ---------- Zsh (powerlevel10k + plugins) ----------------------------
  RUN sh -c "$(wget -qO- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
        -p git \
        -a "source /usr/share/doc/fzf/examples/key-bindings.zsh" \
        -a "source /usr/share/doc/fzf/examples/completion.zsh" \
        -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.zsh_history" \
        -x
  
  # ---------- SSH config for GitHub (devcontainer 専用) ---------------
  # /host-ssh は devcontainer.json 側で
  # "source=${localEnv:HOME}/.ssh,target=/host-ssh,..." としてマウントする前提
  RUN mkdir -p /home/node/.ssh && \
    chmod 700 /home/node/.ssh && \
    printf '%s\n' \
"    Host github.com" \
"    HostName github.com" \
"    User git" \
"    IdentityFile /host-ssh/id_rsa" \
"    IdentitiesOnly yes" \
"    AddKeysToAgent yes" \
"    StrictHostKeyChecking accept-new" \
    > /home/node/.ssh/config && \
    chmod 600 /home/node/.ssh/config
  
  # ---------- Node CLI (グローバル) ------------------------------------
  RUN npm config set fund false && \
      npm config set audit false && \
      npm config set progress false
  
  RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}
  RUN npm install -g @openai/codex
  RUN npm install -g @google/gemini-cli
  RUN npm install -g typescript ts-node eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin aws-cdk@2
  