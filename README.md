<div align="center">

# ☠️ X-ONE

### 🧠 IA de Pentesting e Segurança Ofensiva — **100% Sem Filtro**, rodando **localmente** na sua máquina

*Neural Network · Sistema Ativo*

![status](https://img.shields.io/badge/status-ativo-00e5ff?style=for-the-badge)
![sem_filtro](https://img.shields.io/badge/modo-SEM%20FILTRO-ff3355?style=for-the-badge)
![local](https://img.shields.io/badge/roda-100%25%20LOCAL-9b5cff?style=for-the-badge)
![python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)

</div>

---

## 🎯 O que é o X-ONE?

O **X-ONE** é uma **IA especialista em pentesting e segurança ofensiva** que roda **na sua própria máquina** — sem depender de servidor, sem enviar seus dados pra lugar nenhum, e **sem filtro de censura**.

Ele **entrega payloads, exploits, scripts ofensivos e PoCs prontos pra copiar** — sem recusar, sem "não posso ajudar com isso", sem enrolação. É pensado pra **bug hunters, pentesters e estudantes de segurança** que trabalham em **ambiente autorizado**.

> 💡 **Por que "sem filtro"?** IAs comuns (ChatGPT, Claude, etc.) recusam gerar payload de XSS, exploit, shell reverso ou script de recon — mesmo em pentest legítimo. O X-ONE usa um modelo **abliterated** (as recusas foram removidas do próprio modelo), então ele **responde direto**.

---

## ✨ Por que usar

| | |
|---|---|
| 🔓 **Sem filtro de verdade** | Modelo *abliterated* — não recusa payload, exploit nem script ofensivo |
| 🏠 **100% local** | Roda na sua máquina. Seus alvos e dados **nunca saem do seu PC** |
| ⚡ **Rápido** (com hardware ok) | Usa a **sua** CPU/GPU — quanto melhor a máquina, mais rápido |
| 💸 **Sem custo de API** | O modelo roda local via Ollama. Zero mensalidade de API de IA |
| 🎩 **Especialista ofensivo** | Recon, XSS, SQLi, LFI, SSRF, JWT, exploits, one-liners prontos |
| 🖥️ **Interface bonita** | UI web cyberpunk, com histórico e microfone (voz) |

---

## 📦 O que vai ser instalado

Ao rodar o instalador, três coisas entram na sua máquina:

1. **🦙 Ollama** — o motor que roda modelos de IA localmente ([ollama.com](https://ollama.com)).
2. **🧠 O modelo sem filtro** — `huihui_ai/qwen2.5-abliterate:3b` (~2 GB). É um Qwen 2.5 *abliterated* (sem censura).
3. **🐍 O X-ONE** — o servidor (`brain_server.py`) + a interface web (`index.html`), rodando na porta **7777**.

> Nada disso "liga pra casa". Depois de instalado, funciona **offline** (só precisa de internet no download inicial do modelo).

---

## ⚙️ Requisitos

| Recurso | Mínimo | Recomendado |
|---|---|---|
| 💾 **RAM** | 8 GB | 16 GB+ |
| 🧮 **CPU** | 4 núcleos | 8+ núcleos |
| 🎮 **GPU** | opcional | **NVIDIA (deixa MUITO mais rápido)** |
| 💽 **Disco** | ~5 GB livres | — |
| 🐍 **Python** | 3.10+ | 3.11+ |
| 🖥️ **SO** | Windows 10+, Linux, macOS | — |

> ⚠️ **Sem GPU?** Funciona em CPU, mas fica mais lento. O modelo **3b** foi escolhido justamente por rodar em CPU comum. Com **GPU NVIDIA**, dá pra usar o **7b** (mais inteligente) e ainda voar.

---

## 🚀 Como instalar

### 🪟 Windows

1. Instale o **Python 3.10+**: [python.org/downloads](https://python.org/downloads) *(marque "Add Python to PATH")*
2. Instale o **Ollama**: [ollama.com/download](https://ollama.com/download)
3. Baixe este repositório (**Code → Download ZIP**) e extraia.
4. Dê **duplo clique em `install.bat`** e aguarde o download do modelo.
5. Depois, **duplo clique em `start.bat`**.
6. Abra o navegador em **http://localhost:7777** 🎉

### 🐧 Linux / 🍎 macOS

```bash
# 1) baixe o repositório
git clone https://github.com/Charyflux/xone.git
cd xone

# 2) instale (Ollama + modelo + dependências)
chmod +x install.sh start.sh
./install.sh

# 3) inicie
./start.sh
```

Depois abra **http://localhost:7777** no navegador. ✅

---

## 🕹️ Como usar

1. Abra **http://localhost:7777**.
2. No campo de baixo, **digite o que precisa** — ou clique no 🎤 pra falar.
3. Exemplos:
   - *"me dá um payload de XSS refletido com bypass de WAF"*
   - *"script python pra fazer fuzzing de parâmetros"*
   - *"one-liner de recon de subdomínios"*
   - *"exploit pra essa versão do [software]"*
4. O X-ONE responde com o **código pronto pra copiar**. Sem recusar.

> 💬 O menu tem **uma opção só: `☠ SEM FILTRO`** — é o modelo abliterated. Simples assim.

---

## 🔧 Como configurar

Toda a config fica no arquivo **`.env`** (criado automaticamente a partir do `.env.example`):

```bash
OLLAMA_MODEL=huihui_ai/qwen2.5-abliterate:3b   # o modelo (3b=rápido, 7b=melhor)
PORT=7777                                       # porta da interface
MAX_TOKENS=600                                  # menor = respostas mais rápidas
TTS_ENABLED=0                                   # 1 liga a voz
ANTHROPIC_API_KEY=                              # DEIXE VAZIO p/ modo sem filtro
```

### 🧠 Trocar o modelo (mais rápido ↔ mais inteligente)

```bash
# mais RÁPIDO (CPU modesta) — padrão
ollama pull huihui_ai/qwen2.5-abliterate:3b

# mais INTELIGENTE (precisa de GPU ou CPU forte)
ollama pull huihui_ai/qwen2.5-abliterate:7b
```

Depois é só mudar `OLLAMA_MODEL` no `.env` e reiniciar (`start.sh` / `start.bat`).

---

## ⚡ Está lento? Deixe mais rápido

| Ação | Efeito |
|---|---|
| 🎮 **Use uma GPU NVIDIA** | O maior salto — 10-20x mais rápido |
| 🔽 **Modelo `3b`** em vez do `7b` | ~2x mais rápido em CPU |
| ✂️ **Baixe o `MAX_TOKENS`** (600 → 300) | Respostas mais curtas terminam antes |
| 🧹 **Feche programas pesados** | O modelo usa a CPU — libere-a pra ele |

---

## 🆘 Problemas comuns

<details>
<summary><b>❓ "Não conecta / página não abre"</b></summary>

Confira se o `start.sh` / `start.bat` está rodando (a janela deve ficar aberta) e acesse **http://localhost:7777** (não https).
</details>

<details>
<summary><b>❓ "Ollama não encontrado"</b></summary>

Instale o Ollama em [ollama.com/download](https://ollama.com/download) e rode o instalador de novo.
</details>

<details>
<summary><b>❓ "Muito lento"</b></summary>

É CPU. Veja a seção **⚡ Está lento?** acima. Com GPU NVIDIA resolve; sem GPU, use o modelo `3b` e baixe o `MAX_TOKENS`.
</details>

<details>
<summary><b>❓ "Ele recusou algo"</b></summary>

O modelo abliterated raramente recusa. Se acontecer, reformule o pedido de forma técnica/direta, ou confirme que o `.env` está com `ANTHROPIC_API_KEY` **vazio** (com chave da Anthropic ele usa o Claude, que TEM filtro).
</details>

---

## ⚖️ Aviso legal

> 🛡️ O X-ONE é uma ferramenta para **segurança ofensiva em ambiente AUTORIZADO** — pentests contratados, bug bounty dentro do escopo, CTFs e laboratórios próprios.
>
> **Você é o único responsável** pelo uso. Testar sistemas sem autorização é crime. Use com ética e dentro da lei.

---

<div align="center">

**☠️ X-ONE** — *feito para quem hackeia de verdade.*

Se curtiu, deixa uma ⭐ no repositório!

</div>
