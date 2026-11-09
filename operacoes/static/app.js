const $ = id => document.getElementById(id);
let selected = null;
function message(text) { $('message').textContent = text; }
function element(tag, text) { const node = document.createElement(tag); node.textContent = text; return node; }
async function call(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.erro || `HTTP ${response.status}`);
  return data;
}
async function show(code) {
  selected = null; $('event').hidden = true; $('detail').replaceChildren();
  try {
    const data = await call('/api/entregas/' + encodeURIComponent(code));
    selected = data.codigo; $('code').value = data.codigo;
    $('detail').append(element('h3', data.codigo), element('p', `${data.origem} → ${data.destino}`), element('p', `Status: ${data.status}`));
    const list = document.createElement('ul');
    for (const event of data.ocorrencias) list.append(element('li', `${new Date(event.criado_em).toLocaleString('pt-BR')} — ${event.descricao}`));
    $('detail').append(list);
    if (!data.ocorrencias.length) $('detail').append(element('p', 'Nenhuma ocorrência registrada.'));
    $('event').hidden = false; message('Entrega consultada.');
  } catch (error) { message(error.message); }
}
async function load() {
  try {
    const data = await call('/api/entregas'); $('list').replaceChildren();
    for (const delivery of data.entregas) {
      const li = document.createElement('li'); const button = element('button', `${delivery.codigo} · ${delivery.destino}`);
      button.onclick = () => show(delivery.codigo); li.append(button); $('list').append(li);
    }
    message('Lista atualizada.');
  } catch (error) { $('list').replaceChildren(); message(error.message); }
}
$('search').onsubmit = event => { event.preventDefault(); show($('code').value.trim()); };
$('refresh').onclick = load;
$('event').onsubmit = async event => {
  event.preventDefault(); if (!selected) return;
  $('save').disabled = true;
  try {
    await call(`/api/entregas/${encodeURIComponent(selected)}/ocorrencias`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({descricao:$('description').value})});
    $('description').value = ''; await show(selected); message('Ocorrência registrada.');
  } catch (error) { message(error.message); }
  finally { $('save').disabled = false; }
};
load();
