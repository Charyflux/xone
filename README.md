<!-- ═══════════════════════════════════════════════════════════ -->
<!--                        X-ONE · README                        -->
<!-- ═══════════════════════════════════════════════════════════ -->

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:00eeff,50:7c3aed,100:aa44ff&height=210&section=header&text=X-ONE&fontSize=90&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Neural%20Network%20·%20AI%20Brain%20for%20Pentesting&descAlignY=60&descSize=18" alt="X-ONE"/>
</p>

<p align="center">
  <a href="https://github.com/Charyflux/xone/stargazers"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=00EEFF&center=true&vCenter=true&width=720&lines=IA+de+pentesting+100%25+local%2C+sem+censura;Sem+custos+de+API+%C2%B7+As+tuas+conversas+n%C3%A3o+saem+da+m%C3%A1quina;Multi-modelo+%C2%B7+OSINT+%C2%B7+An%C3%A1lise+de+vulnerabilidades;O+teu+co-piloto+ofensivo%2C+sem+rodeios" alt="Typing SVG"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-SSE_Streaming-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Vers%C3%A3o-5.0-aa44ff?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Licen%C3%A7a-Uso_Autorizado-ff3355?style=for-the-badge"/>
</p>

<p align="center">
  <b>🧠 Roda na tua própria máquina. Sem nuvem. Sem filtros desnecessários. Sem faturas de API.</b>
</p>

<p align="center">
  <a href="#-instalação">🚀 Instalar</a> ·
  <a href="#-o-que-faz">✨ Features</a> ·
  <a href="#-modelos">🤖 Modelos</a> ·
  <a href="#-porquê-usar">💡 Porquê</a> ·
  <a href="#-arquitetura">🏗️ Arquitetura</a>
</p>

---

## 🧠 O que é o X-ONE

O **X-ONE** é uma **interface de IA para pentesting e bug bounty** que corre **inteiramente na tua máquina**. Escolhes o modelo local que queres no menu lateral, fazes a pergunta técnica que precisas — e recebes código funcional, PoCs, análises de vulnerabilidades e recon, com respostas de streaming em tempo real numa interface *cyberpunk* animada.

```
┌─────────────────────────────────────────────────────────────┐
│  Tu:      "Cria um PoC de SSRF que atinge a metadata da AWS"  │
│                                                               │
│  ChatGPT: "Desculpa, não posso ajudar com isso…"             │
│                                                               │
│  X-ONE:   import requests                                     │
│           targets = ["http://169.254.169.254/latest/meta…"]  │
│           for t in targets: r = requests.get(...)   ← pronto  │
└─────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> O X-ONE é uma ferramenta para **profissionais de segurança**: pentest autorizado, programas de bug bounty com escopo, CTFs e investigação/educação. **Usa-o apenas contra alvos que tens permissão explícita para testar.**

---

## ✨ O que faz

<table>
<tr>
<td width="50%" valign="top">

### 🤖 Multi-modelo num clique
Menu lateral com **dropdown** para trocar de modelo na hora, com descrição de cada um. Do ultra-rápido ao mais capaz em código.

### ⚡ Streaming em tempo real
Respostas token-a-token via **SSE**, com render throttled (sem lag) e auto-scroll inteligente que não te puxa para baixo quando lês.

### 🎨 Realce de sintaxe + copiar
Blocos de código com **highlight.js**, botão **copiar** em cada bloco e um badge a dizer qual modelo respondeu.

### 🧵 Conversas isoladas + histórico
Cada aba tem a **sua própria conversa** (nada de contexto misturado). Histórico persistente em SQLite, com restaurar e apagar.

</td>
<td width="50%" valign="top">

### 🕵️ OSINT de empresa/domínio
Script consolidado de recon: emails+hosts (**theHarvester**), serviços expostos (**Shodan**), tech-stack/WAF (**whatweb/wafw00f**) e segredos em repos (**gitleaks/trufflehog**).

### 🎯 Análise de vulnerabilidades
Pede um finding e recebe impacto real, **CVSS v3.1**, PoC funcional, passos de validação, bypass de WAF e report pronto.

### 🖼️ Visão + voz (opcional)
Cola uma **imagem** (screenshot de um erro, código) direto no chat. Transcrição de voz por microfone e TTS opcional.

### 🔌 Integração AVEONE
Recebe o contexto dos teus scans automaticamente e mantém-no partilhado entre sessões — a IA já sabe o que encontraste.

</td>
</tr>
</table>

---

## 🤖 Modelos

O menu lateral vem pré-configurado com 4 perfis. Todos correm **localmente** via Ollama — escolhe conforme queres **velocidade** ou **qualidade**:

| Perfil | Modelo | Tamanho | Perfil de uso |
|:---|:---|:---:|:---|
| ⚡ **MODO RÁPIDO** | `qwen2.5:1.5b` | ~1 GB | Respostas simples, quase instantâneo |
| 🦙 **GERAL 3B** | `llama3.2` | ~2 GB | Modelo geral equilibrado |
| 🧠 **CODER 3B** | `qwen2.5-coder:3b` | ~2 GB | **Bom código, rápido — o melhor equilíbrio** |
| ☠️ **SEM FILTROS** | `qwen2.5-coder:7b` | ~4.7 GB | Melhor qualidade de código |

> 💡 **Dica:** trocar de modelo é instantâneo no dropdown. Cada modelo fica "quente" em memória por 2h após o uso (keep-alive), por isso só pagas o carregamento inicial uma vez. Preferes máxima ausência de filtros? Adiciona `dolphin-llama3` (não-censurado). Preferes velocidade real? Um modelo cloud da Ollama ou a API da Anthropic.

---

## 💡 Porquê usar

<table>
<tr>
<td align="center" width="25%">🔒<br><b>Privacidade total</b><br><sub>As tuas perguntas nunca saem da tua máquina. Zero telemetria.</sub></td>
<td align="center" width="25%">💸<br><b>Custo zero</b><br><sub>Sem faturas de API. Corre local, ilimitado, para sempre.</sub></td>
<td align="center" width="25%">🚫<br><b>Sem rodeios</b><br><sub>Respostas técnicas diretas, sem avisos desnecessários em cada linha.</sub></td>
<td align="center" width="25%">🧰<br><b>Arsenal integrado</b><br><sub>OSINT, findings, recon e análise num só sítio.</sub></td>
</tr>
</table>

---

## 📦 O que precisas

| Requisito | Versão | Notas |
|:---|:---|:---|
| **Python** | 3.10+ | Backend FastAPI |
| **Ollama** | recente | Motor dos modelos locais — [ollama.com](https://ollama.com) |
| **RAM** | 8 GB+ | 16 GB+ recomendado para os modelos de 7B |
| **Disco** | ~10 GB | Para os modelos (opcional, só os que usares) |
| **ffmpeg + sox** | opcional | Só se ativares a voz (TTS) |

---

## 🚀 Instalação

### 1️⃣ Instala o Ollama e puxa os modelos

```bash
# Linux / macOS
curl -fsSL https://ollama.com/install.sh | sh

# Puxa os modelos do menu (escolhe os que quiseres)
ollama pull qwen2.5:1.5b        # ⚡ rápido
ollama pull llama3.2            # 🦙 geral
ollama pull qwen2.5-coder:3b   # 🧠 coder rápido
ollama pull qwen2.5-coder:7b   # ☠️ melhor código
```

### 2️⃣ Clona e instala as dependências

```bash
git clone https://github.com/Charyflux/xone.git
cd xone
pip install -r requirements.txt
```

### 3️⃣ Configura (opcional)

```bash
cp .env.example .env
# Edita o .env se quiseres mudar a porta, o modelo padrão, etc.
```

<details>
<summary><b>⚙️ Variáveis do .env</b></summary>

```ini
OLLAMA_URL=http://localhost:11434   # onde o Ollama escuta
OLLAMA_MODEL=qwen2.5:1.5b           # modelo padrão
PORT=7777                          # porta do X-ONE
MAX_HISTORY=20                     # nº de mensagens de contexto
MAX_TOKENS=2048                    # tamanho máx. de resposta
TTS_ENABLED=0                      # 1 = ativa a voz (precisa ffmpeg+sox)
# ANTHROPIC_API_KEY=               # opcional: usa Claude na nuvem em vez do local
```
</details>

### 4️⃣ Arranca

```bash
python brain_server.py
```

Abre **http://localhost:7777** 🎉

<details>
<summary><b>🔧 Correr como serviço (systemd, arranca sempre)</b></summary>

```ini
# /etc/systemd/system/xone.service
[Unit]
Description=X-ONE AI Brain
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
WorkingDirectory=/caminho/para/xone
Environment=PORT=7777
ExecStart=/usr/bin/python3 /caminho/para/xone/brain_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now xone.service
```
</details>

---

## 🎮 Como usar

1. **Escolhe o modelo** no dropdown do canto superior esquerdo (a descrição explica cada um).
2. **Escreve a tua pergunta** na barra inferior — ou cola uma imagem, ou usa o microfone.
3. A resposta faz **stream** em tempo real, com código realçado e botão de copiar.
4. Precisas de mudar de assunto? **CLR** limpa e abre uma conversa nova e isolada.
5. Queres voltar a uma conversa antiga? Abre o **Histórico** e restaura.

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│  Browser (index.html)                                         │
│  • UI cyberpunk animada (canvas neural network)               │
│  • Streaming SSE · markdown + highlight.js · sessão isolada   │
└───────────────────────────┬──────────────────────────────────┘
                            │  HTTP / SSE
┌───────────────────────────▼──────────────────────────────────┐
│  brain_server.py (FastAPI)                                    │
│  • /api/chat  → streaming token-a-token                       │
│  • histórico por-sessão + contexto AVEONE partilhado          │
│  • sampling afinado por modelo · num_ctx 8192                 │
│  • sessões em SQLite · findings · OSINT · recon tools         │
└───────────────────────────┬──────────────────────────────────┘
                            │  /api/chat (template nativo)
┌───────────────────────────▼──────────────────────────────────┐
│  Ollama  (localhost:11434)                                    │
│  qwen2.5 · qwen2.5-coder · llama3.2 · dolphin-llama3 · …       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧩 Stack

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>
  <img src="https://img.shields.io/badge/highlight.js-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>
</p>

---

## 🗺️ Roadmap

- [x] Multi-modelo com dropdown + descrições
- [x] Histórico de conversa isolado por sessão
- [x] Migração para `/api/chat` nativo + `num_ctx` maior
- [x] Botão copiar, regenerar e badge do modelo
- [x] Script OSINT de empresa/domínio
- [ ] Busca web / RAG sobre os teus próprios findings
- [ ] Execução de ferramentas de recon pelos modelos locais
- [ ] Temas de UI alternativos

---

## ⚠️ Aviso legal

O X-ONE destina-se a **testes de segurança autorizados**, programas de **bug bounty com escopo**, **CTFs** e **investigação/educação**. O uso desta ferramenta contra sistemas sem autorização explícita é **ilegal** e é da tua inteira responsabilidade. Os autores não se responsabilizam por uso indevido.

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:aa44ff,50:7c3aed,100:00eeff&height=120&section=footer"/>
</p>

<p align="center">
  <sub>⚡ Feito para quem faz segurança ofensiva a sério. Dá uma ⭐ se te for útil.</sub>
</p>
