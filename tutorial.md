# Tutorial de Uso — SentinelKit

Este guia oferece uma ordem sugerida e um passo a passo prático para usar os scripts do SentinelKit em Windows.

## Pré‑requisitos

1. Instale Python 3.10+ e, quando necessário, execute o PowerShell como Administrador.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Estrutura de saída: os resultados são salvos em `results/` (JSON, CSV, imagens, WAV).

## Fluxo Sugerido (Ordem)

1. Iniciar pelo menu ou GUI
2. Mapear dispositivo (inventário)
3. Monitorar recursos em tempo real (opcional)
4. Mapear rede local
5. Descobrir hosts ativos
6. Escolher um alvo e inspecionar serviços
7. Coletar credenciais (quando aplicável)
8. Navegar arquivos via SSH/SFTP (quando aplicável)
9. Registrar atividades (logs, screenshots, áudio, clipboard)
10. Testar desktop remoto (host/viewer)

## Início Rápido

- Menu interativo:

```bash
python src/main.py
```

- GUI com botões, tooltips e “?” para instruções:

```bash
python src/scripts/gui_launcher.py
```

## Passo a Passo

### 1) Inventário do Dispositivo — Device Details

Coleta OS/CPU/Memória/Disco/Rede em JSON.

```bash
python src/scripts/device_details.py
```
Saída: `results/device_details_YYYY-MM-DD.json`

### 2) Monitor em Tempo Real (Opcional) — System Monitor Dashboard

Visual de CPU/RAM/Disk atualizado a cada segundo. Pressione `Q` para sair.

```bash
python src/scripts/system_monitor.py
```

### 3) Mapear Rede — Network Info

IP público, WiFi, interfaces e vizinhança ARP.

```bash
python src/scripts/network_info.py
```
Saída: `results/network_info_*.json`

### 4) Hosts Ativos — LAN Ping Sweep

Varre `/24` para encontrar IPs ativos. Informe a base (ex.: `192.168.1`) ou deixe vazio para auto.

```bash
python src/scripts/ping_sweep.py
```
Saída: `results/ping_sweep_*.json`

### 5) Portas Abertas — Port Scanner

Escolha o alvo (IP/host) e o modo: `common` (principais portas) ou `all` (1–1024).

```bash
python src/scripts/port_scanner.py <TARGET_IP> --mode common
python src/scripts/port_scanner.py <TARGET_IP> --mode all
```

### 6) Banners de Serviços — Banner Grabber

Captura banners de serviços para identificação.

```bash
python src/scripts/banner_grabber.py <HOST> "<PORTS_COMMA>"
# Ex.: python src/scripts/banner_grabber.py 192.168.1.10 "80,22,25"
```
Saída: `results/banners_*.json`

### (Opcional via GUI) Fingerprint Unificado — Service Fingerprint

Executa port scan e banner grabber na sequência (GUI: informe alvo e modo).

```bash
# Use pela GUI: python src/scripts/gui_launcher.py
```
Saída: `results/fingerprint_*.json`

### 7) Credenciais — Dump WiFi & System Credentials

Pode requerer privilégios de Administrador.

```bash
python src/scripts/credentials.py --elevate
```
Saída: `results/credentials_*.json`

### 8) SSH/SFTP Browser

Lista e baixa arquivos via SSH/SFTP. Informe host, usuário e senha.

```bash
python src/scripts/ssh_file_browser.py <HOST> <USER> --password "<PASSWORD>"
```
Saída: `results/ssh_listing_*.json`

### 9) Scanner de Arquivos — File System Scanner

Varre diretórios com profundidade e tamanho, opcionalmente calcula SHA256.

```bash
python src/scripts/device_files.py --path "<CAMINHO>" --depth 2
# Para hashing (menu principal oferece flag; via CLI):
# python src/scripts/device_files.py --path "<CAMINHO>" --depth 2 --hash
```
Saída: `results/filesystem.json`

### 10) Registro de Sistema — System Monitor Logger

Grava CPU e Memória por segundo em CSV. Duração opcional.

```bash
python src/scripts/system_monitor_log.py
# ou informar duração (segundos) pela GUI
```
Saída: `results/monitor_logs/log_*.csv`

### 11) Processos — Process Top Viewer

Mostra processos por CPU/mem, em tempo real. Pressione `Q` para sair.

```bash
python src/scripts/process_monitor.py
```

### 12) Screenshot

Captura tela e salva imagem.

```bash
python src/scripts/screenshot.py
```
Saída: `results/screenshots/`

### 13) Áudio — Audio Recorder

Grava o microfone até pressionar `Q`. Instala dependências automaticamente se necessário.

```bash
python src/scripts/audio_recorder.py
```
Saída: `results/audio/audio_*.wav`

### 14) Clipboard — Clipboard Dump

Exporta texto do clipboard; instala `pywin32` automaticamente.

```bash
python src/scripts/clipboard_dump.py
```
Saída: `results/clipboard/clipboard_*.txt`

### 15) Câmera — Camera Access (Viewer)

Abre a câmera; `S` salva snapshot, `Q` sai.

```bash
python src/scripts/camera_access.py
```
Saída: `results/camera_captures/`

### 16) Teclado — Keylogger UI (Visível)

Grava entradas de teclado com janela visível.

```bash
python src/scripts/keyboard-inputs.pyw
```
Saída: `results/inputs/`

### 17) WiFi — WiFi Networks Scanner

Lista redes próximas (Windows).

```bash
python src/scripts/wifi_scan.py
```
Saída: `results/wifi_networks_*.json`

### 18) Desktop Remoto — Host e Viewer

- Host (execute no PC a ser acessado):
```bash
python src/scripts/device_access.py
```

- Viewer (execute no seu PC, informe IP do Host):
```bash
python src/scripts/remote_viewer.py <TARGET_IP>
```

### 19) HTTP Security Check

Verifica cabeçalhos de segurança HTTP (HSTS, CSP, X‑Frame‑Options) em um host:porta.

```bash
python src/scripts/http_security_check.py <HOST> [PORT]
# Ex.: python src/scripts/http_security_check.py example.com 80
```
Saída: `results/http_security/security_HOST_DATE.json`

### 20) TLS/Cert Inspector

Captura certificado TLS, emissor, validade e alerta se expira em ≤30 dias.

```bash
python src/scripts/tls_cert_inspector.py <HOST> [PORT]
# Ex.: python src/scripts/tls_cert_inspector.py example.com 443
```
Saída: `results/tls/tls_HOST_DATE.json`

### 21) SMB Shares Enumerator

Enumera compartilhamentos SMB. Informe um host ou deixe vazio para tentar LAN.

```bash
python src/scripts/smb_shares_enumerator.py --host <HOST_OPCIONAL>
```
Saída: `results/smb/shares_DATE.json`

### 22) Windows Event Logs Export

Exporta eventos de um canal nas últimas N horas, filtrando por nível opcional.

```bash
python src/scripts/windows_event_export.py --channel System --hours 4 --level Error
```
Saída: `results/event_logs/events_CHANNEL_DATE.json`

### 23) Autoruns & Startup Audit

Lista itens de inicialização (pastas, chaves Run) e tarefas agendadas.

```bash
python src/scripts/autoruns_startup_audit.py
```
Saída: `results/autoruns/autoruns_DATE.json`

### 24) Installed Programs Inventory

Inventário de programas Win32 e MSIX com versão e publisher.

```bash
python src/scripts/installed_programs_inventory.py
```
Saída: `results/programs/programs_DATE.json`

### 25) Firewall Rules Dump

Exporta regras básicas do Windows Firewall.

```bash
python src/scripts/firewall_rules_dump.py
```
Saída: `results/firewall/firewall_DATE.json`

### 26) Scheduled Tasks Audit

Lista tarefas agendadas e identifica falhas recentes.

```bash
python src/scripts/scheduled_tasks_audit.py
```
Saída: `results/scheduled_tasks/tasks_DATE.json`

### 27) USB Devices History

Lista histórico de dispositivos USB do sistema.

```bash
python src/scripts/usb_devices_history.py
```
Saída: `results/usb/usb_DATE.json`

### 28) Browser Profiles Snapshot

Coleta dados não sensíveis dos navegadores (Chrome/Edge/Firefox): perfis, versões, extensões.

```bash
python src/scripts/browser_profiles_snapshot.py
```
Saída: `results/browser/browser_DATE.json`

### 29) HTTP Directory Bruteforce (educacional)

Testa paths comuns com rate‑limit.

```bash
python src/scripts/http_directory_bruteforce.py <BASE_URL> [RATE_MS]
# Ex.: python src/scripts/http_directory_bruteforce.py http://example.com 200
```
Saída: `results/http_bruteforce/dir_bruteforce_DATE.json`

Parâmetros avançados:
- Lista de paths via CSV ou arquivo: `--paths "admin/,login/,robots.txt"` ou `--paths-file @c:\lista.txt`
- Concorrência: `--concurrency 5`
- Filtro de status: `--status 200,301,302,401,403`
- Timeout: `--timeout 5`

No GUI, informe Base URL, Rate ms, Paths, Concorrência, Status e Timeout pelos diálogos.

### 30) Port Range Profiler

Perfil por faixa de portas com banners e tempos.

```bash
python src/scripts/port_range_profiler.py <HOST> <START-END> --timeout 1.5
# Ex.: python src/scripts/port_range_profiler.py 192.168.1.10 30000-30100 --timeout 1.5
```
Saída: `results/port_range/range_HOST_START_END_DATE.json`

- Teste local (abre host e viewer no mesmo PC):
```bash
python src/scripts/launch_session.py
```

## Dicas Práticas

- IP/Host do alvo: é o dispositivo que você quer inspecionar/conectar (`192.168.1.x`, `localhost`, ou domínio).
- Descobrir alvos: combine “Network Info” e “LAN Ping Sweep” para levantar IPs ativos.
- Teclas rápidas: `Q` para sair em dashboards/monitores; `S` no viewer de câmera para snapshots.
- Saídas: verifique a pasta `results/` para JSON, CSV, imagens e áudio gerados.

## Novos Recursos de UX no GUI

- Busca rápida: campo “Search” filtra botões por nome (desabilita os não coincidentes).
- Categorias visuais: separação por blocos (Rede, Sistema etc.) para navegação mais rápida.
- Abrir último resultado: botão “Open Latest Result” pede a subpasta (ex.: `http_security`, `tls`, `smb`) e abre o arquivo mais recente daquela categoria.

## Padrão de Saída JSON (Envelope)

- Todos os resultados principais incluem um envelope:
  - `meta`: informações do script (`script`), timestamp (`ts`), versão (`version`) e alvo (`host` quando aplicável).
  - `data`: conteúdo específico coletado pelo script.
- Exemplo resumido:
```json
{
  "meta": { "script": "http_security_check", "ts": "20260202_121314", "version": "1.0", "host": "example.com" },
  "data": { "headers": { "...": "..." }, "checks": { "hsts": true } }
}
```
