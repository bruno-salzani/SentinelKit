# 🛡️ SentinelKit — Cyber‑Security Learning Toolkit

![Status](https://img.shields.io/badge/Status-Ativo-brightgreen)
![Framework](https://img.shields.io/badge/Language-Python-blue)
![Stack](https://img.shields.io/badge/Stack-Paramiko%20%7C%20OpenCV%20%7C%20Selenium-orange)
![Infra](https://img.shields.io/badge/Infra-Windows%20%7C%20PowerShell-lightgrey)

Canivete suíço educacional para exploração de redes, sistemas e ambientes de usuário no Windows. O projeto foca em segurança ética e aprendizado baseado em consentimento, oferecendo ferramentas para automação de tarefas de auditoria, monitoramento de rede e interrogação de dispositivos.

---

# 🎯 Objetivo do Projeto

Prover um ambiente prático para o estudo de cibersegurança e administração de sistemas:

- **Auditoria de Ativos**: Inventário detalhado de hardware, software e rede.
- **Exploração Remota**: Domínio de protocolos SSH/SFTP e controle de desktop (RDP-like).
- **Monitoramento Ético**: Captura de inputs e logs de sistema com transparência e consentimento.
- **Interrogação de Periferia**: Análise de roteadores e dispositivos de rede via scripts automatizados.

Foco em:
- **Feedback Estruturado**: Saídas em JSON para análise determinística.
- **Modularidade**: Scripts independentes que seguem o princípio de responsabilidade única.
- **Educação Ética**: Ênfase em conformidade legal e uso em ambientes controlados.

---

# 🧠 Estratégia e Arquitetura

O toolkit é construído sobre uma base modular em Python, utilizando APIs nativas do Windows e bibliotecas de alto nível para orquestração:



1.  **Core Scripts**: Lógica de execução para descoberta e controle.
2.  **Support Layer**: Helpers compartilhados para logs, constantes e tratamento de arquivos.
3.  **Result Engine**: Estrutura que organiza capturas, JSONs e artefatos por timestamp.
4.  **Security Layer**: Verificações de permissão (Admin) e interfaces de usuário para consentimento.

Diretrizes técnicas:
- **JSON-First**: Todo scan gera um reporte estruturado para fácil integração.
- **Cross-Protocol**: Suporte a SSH, HTTP (JS injection via Selenium) e Win32 APIs.
- **User-Centric Monitoring**: Ferramentas de captura com indicadores visuais claros para o usuário.

---

# 🔄 Fluxos Cobertos

1.  **Acesso e Controle Remoto**
    - Streaming de tela e controle de mouse/teclado em LAN.
    - Navegação recursiva em sistemas de arquivos via SFTP.
2.  **Interrogação de Infraestrutura**
    - Identificação de topologia de rede e portas abertas.
    - Extração de logs e snapshots de configuração de roteadores.
3.  **Monitoramento de Ambiente**
    - Gravação de inputs em janelas específicas (batching de 5 segundos).
    - Inventário de processos e privilégios de sistema.

---

# 📁 Estrutura do Projeto

```bash
src/
├── main.py              # Menu interativo principal
├── scripts/             # Core das ferramentas
│   ├── device_access.py    # Host de acesso remoto
│   ├── remote_viewer.py    # Visualizador de acesso remoto
│   ├── ssh_file_browser.py # Navegador SSH/SFTP
│   ├── device_details.py   # Inventário de sistema
│   ├── network_info.py     # Scan de rede
│   ├── router_details.py   # Auditoria de roteadores (HTTP/JS)
│   ├── keyboard-inputs.pyw # Gravador de inputs (UI visível)
│   └── support.py          # Helpers e utilitários
results/                 # Artefatos gerados (JSON, Capturas, Downloads)
commands.md              # Guia consolidado de comandos
requirements.txt         # Dependências do projeto
