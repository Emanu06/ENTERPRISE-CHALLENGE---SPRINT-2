const money=v=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(v);
const api=path=>fetch(`/api/${path}`).then(r=>r.ok?r.json():r.json().then(x=>Promise.reject(x)));
const cards=(target,values)=>document.querySelector(target).innerHTML=values.map(([label,value])=>`<div class="card"><small>${label}</small><b>${value}</b></div>`).join('');
async function load(){
 const [d,invoices,pred,anomalies]=await Promise.all([api('dashboard'),api('faturas'),api('ia/previsao-demanda'),api('ia/anomalias')]);
 document.querySelector('#period').textContent=d.periodo;
 cards('#cards',[['Sessões',d.sessoes],['Energia entregue',`${d.energia_total_kwh} kWh`],['Usuários ativos',d.usuarios_ativos],['Receita estimada',money(d.receita_estimada)],['Sessões interrompidas',d.interrompidas]]);
 const average=d.usuarios_ativos?d.energia_total_kwh/d.usuarios_ativos:0;
 cards('#indicatorCards',[['Consumo médio por usuário',`${average.toFixed(1)} kWh`],['Taxa de interrupção',`${((d.interrompidas/d.sessoes)*100).toFixed(1)}%`],['Alertas de IA',anomalies.length],['Próximo pico',pred.length?pred.reduce((a,b)=>a.kwh_estimado>b.kwh_estimado?a:b).faixa:'—'],['Receita projetada',money(d.receita_estimada)]]);
 document.querySelector('#invoices').innerHTML=invoices.map(i=>`<tr><td>${i.usuario}<br><small>${i.unidade}</small></td><td>${i.energia_total_kwh.toFixed(2)} kWh</td><td>${money(i.custo_energia)}</td><td>${money(i.custo_infraestrutura)}</td><td><b>${money(i.total)}</b></td></tr>`).join('');
 document.querySelector('#prediction').innerHTML=pred.map(p=>`<div><b>${p.faixa}</b><br>${p.kwh_estimado} kWh previstos · nível ${p.nivel}</div>`).join('')||'<div>Dados insuficientes para previsão.</div>';
 document.querySelector('#anomalies').innerHTML=anomalies.length?anomalies.map(a=>`<div class="warn"><b>${a.sessao_id}</b> · ${a.energia_kwh} kWh<br><small>${a.motivo} (${a.status})</small></div>`).join(''):'<div>Nenhuma anomalia encontrada.</div>';
 const max=Math.max(...invoices.map(i=>i.energia_total_kwh),1);
 document.querySelector('#consumptionBars').innerHTML=invoices.map(i=>`<div><span>${i.usuario}</span><div class="bar"><i style="width:${(i.energia_total_kwh/max)*100}%"></i></div><b>${i.energia_total_kwh.toFixed(1)} kWh</b></div>`).join('');
}
document.querySelectorAll('.tab').forEach(tab=>tab.onclick=()=>{document.querySelectorAll('.tab,.screen').forEach(x=>x.classList.remove('active'));tab.classList.add('active');document.querySelector(`#${tab.dataset.screen}`).classList.add('active')});
document.querySelector('#refresh').onclick=load;document.querySelector('#refreshIndicators').onclick=load;
document.querySelector('#form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.target));['energia_kwh','potencia_media_kw'].forEach(k=>f[k]=Number(f[k]));const feedback=document.querySelector('#feedback');try{const r=await fetch('/api/sessoes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(f)});const b=await r.json();if(!r.ok)throw b;feedback.textContent=`✓ ${b.mensagem}`;await load()}catch(x){feedback.textContent=`Erro: ${x.detail||'não foi possível registrar'}`}};
load().catch(e=>document.body.insertAdjacentHTML('beforeend',`<p>Erro ao carregar API: ${e}</p>`));
