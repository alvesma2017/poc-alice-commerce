// Pega o transactionID do nó de criação da transação
const trxId = $node["SPG - Create Payment"].json.transactionID;

// Pega e limpa o telefone vindo do Webhook
const raw = ($node["Webhook - IA"].json.body?.phone ?? "").toString().replace(/\D/g, "");

// Validações simples
if (!trxId) throw new Error("transactionID ausente.");
if (raw.length < 10) throw new Error("Telefone inválido.");

// Monta o body solicitado pela API
const body = { customerPhone: '55#${raw}'};

// Inclui "inAPP" somente se veio true do Webhook
if ($node["Webhook - IA"].json.body?.inAPP === true) {
  body.inAPP = true;
}

// Retorna no formato esperado pelo n8n
return [{ json: { transactionID: trxId, body } }];