#!/usr/bin/env bash
# Faz login no Salesforce com usuario + senha + token de seguranca
# (mesmo fluxo da biblioteca simple_salesforce do Python) e grava a
# sessao em SALESFORCE_SESSION_ID no .env.
# A senha e pedida no terminal e NAO e salva em lugar nenhum.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a; . ./.env; set +a
: "${SALESFORCE_USERNAME:?preencha SALESFORCE_USERNAME no .env}"
: "${SALESFORCE_SECURITY_TOKEN:?preencha SALESFORCE_SECURITY_TOKEN no .env}"
VER="${SALESFORCE_API_VERSION#v}"
HOST="${SALESFORCE_INSTANCE_URL%/}"

if [ -n "${SALESFORCE_PASSWORD:-}" ]; then
  SENHA="$SALESFORCE_PASSWORD"
else
  echo "(a senha nao aparece enquanto voce digita; digite e aperte Enter)"
  read -rsp "Senha do Salesforce ($SALESFORCE_USERNAME): " SENHA; echo
fi

xml_escape() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g' -e "s/'/\&apos;/g"; }
U=$(printf '%s' "$SALESFORCE_USERNAME" | xml_escape)
P=$(printf '%s%s' "$SENHA" "$SALESFORCE_SECURITY_TOKEN" | xml_escape)
unset SENHA

RESP=$(curl -s -m 30 "$HOST/services/Soap/u/$VER" \
  -H 'Content-Type: text/xml; charset=UTF-8' -H 'SOAPAction: login' \
  --data-binary @- <<EOF
<?xml version="1.0" encoding="utf-8"?>
<env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
  <env:Body><n1:login xmlns:n1="urn:partner.soap.sforce.com"><n1:username>$U</n1:username><n1:password>$P</n1:password></n1:login></env:Body>
</env:Envelope>
EOF
)
unset P

SID=$(printf '%s' "$RESP" | sed -n 's:.*<sessionId>\([^<]*\)</sessionId>.*:\1:p')
if [ -z "$SID" ]; then
  echo "Falhou o login:"
  printf '%s' "$RESP" | sed -n 's:.*<faultstring>\([^<]*\)</faultstring>.*:\1:p'
  exit 1
fi

if grep -q '^SALESFORCE_SESSION_ID=' .env; then
  sed -i '' "s#^SALESFORCE_SESSION_ID=.*#SALESFORCE_SESSION_ID=$SID#" .env
else
  printf 'SALESFORCE_SESSION_ID=%s\n' "$SID" >> .env
fi
echo "Login OK. Sessao gravada no .env (vale algumas horas)."
