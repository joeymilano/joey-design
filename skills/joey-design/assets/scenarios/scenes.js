const brief = JSON.parse(document.querySelector('#brief').textContent)
const get = id => document.getElementById(id)
const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
const storageKey = 'joey-scenario/' + brief.kind + '/' + brief.id
function readSaved(){
  try {return JSON.parse(localStorage.getItem(storageKey)) || {}} catch {return {}}
}
function save(value){
  try {localStorage.setItem(storageKey, JSON.stringify(value))} catch {}
}
function download(name, type, content){
  const url = URL.createObjectURL(new Blob([content], {type}))
  const link = document.createElement('a')
  link.href = url
  link.download = name
  document.body.append(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}
for(const [target, field] of Object.entries({brand:'title',edition:'edition',headline:'headline',intro:'intro',credit:'source'})){
  get(target).textContent = brief[field]
}
const desk = get('desk')
const items = brief.items
function samples(){
  const photo = new Image()
  photo.alt = brief.alt
  photo.src = brief.image
  get('cover').append(photo)
  const saved = readSaved()
  const quantities = Object.fromEntries(items.map(item => [item.id, Math.min(9,Math.max(0,Number.parseInt(saved?.[item.id],10) || 0))]))
  desk.innerHTML = '<div class="bar"><h2>Choose your cuts</h2><span class="meta">Sample request</span></div>' +
    items.map(item => `<div class="row"><span aria-hidden="true" class="swatch" style="--swatch:${esc(item.color)}"></span><div><small>${esc(item.code)}</small><h3>${esc(item.name)}</h3></div><div class="sample-info"><strong>${esc(item.spec)}</strong><p>${esc(item.note)}</p></div><div class="controls"><button data-step="-1" data-id="${esc(item.id)}" aria-label="Remove one ${esc(item.name)}">−</button><span class="qty num" id="q-${esc(item.id)}"></span><button data-step="1" data-id="${esc(item.id)}" aria-label="Add one ${esc(item.name)}">+</button></div></div>`).join('') +
    '<div class="summary"><p role="status" id="total"></p><button class="solid" id="export">Download request (.txt)</button></div>'
  function render(){
    const total = Object.values(quantities).reduce((sum,n) => sum+n,0)
    get('total').textContent = total ? total + (total===1 ? ' cut selected' : ' cuts selected') : 'Choose a cut to start your request'
    get('export').disabled = total===0
    for(const item of items) get('q-'+item.id).textContent = quantities[item.id]
    desk.querySelectorAll('[data-step]').forEach(b => {
      const n = quantities[b.dataset.id]
      b.disabled = b.dataset.step==='1' ? n>=9 : n===0
    })
  }
  desk.addEventListener('click',e => {
    const b = e.target.closest('[data-step]')
    if(!b) return
    quantities[b.dataset.id] += Number(b.dataset.step)
    save(quantities)
    render()
  })
  get('export').onclick = () => {
    const cuts = items.filter(i=>quantities[i.id]).map(i => `${i.code} | ${i.name} | ${i.spec} | ${quantities[i.id]} ${quantities[i.id]===1?'cut':'cuts'}`)
    download(brief.id+'-request.txt','text/plain;charset=utf-8',[brief.title,'Sample request','',...cuts,'','Please confirm availability and shipping before dispatch.','',brief.source].join('\r\n'))
  }
  render()
}
function report(){
  const metrics = [brief.metrics.visits, brief.metrics.actions, brief.metrics.rate]
  const read = (pair, metric) => metric===2 ? (pair[0] ? pair[1]*100/pair[0] : null) : pair[metric]
  const display = (n, metric) => n===null ? '无基数' : metric===2 ? n.toFixed(1)+'%' : n.toLocaleString('zh-CN')
  let metric = 1
  desk.innerHTML = `<div class="bar"><h2>两周对照</h2><span>${esc(brief.previous)} / ${esc(brief.current)}</span></div>
    <div class="toolbar"><div aria-label="指标">${metrics.map((m,i)=>`<button data-metric="${i}">${m}</button>`).join('')}</div><select aria-label="渠道" id="channel"><option value="">全部渠道</option>${items.map(i=>`<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('')}</select></div>
    <div class="legend"><span><i></i>上期</span><span><i></i>本期</span></div><div id="chart" class="compare"></div><div class="table-wrap"><table><caption>渠道明细</caption><thead><tr><th>渠道</th><th>上期</th><th>本期</th><th>变化</th></tr></thead><tbody id="rows"></tbody></table></div><div class="summary"><span id="scope" role="status"></span><button id="export">下载当前 CSV</button></div>`
  function selected(){return items.filter(i => !get('channel').value || i.id===get('channel').value)}
  function render(){
    const rows = selected()
    const sum = rows.reduce((a,r)=>[a[0]+r.current[0],a[1]+r.current[1]],[0,0])
    get('cover').innerHTML = `<strong class="big">${display(read(sum,metric),metric)}</strong><span>本期${metrics[metric]} · ${esc(get('channel').selectedOptions[0].textContent)}</span>`
    desk.querySelectorAll('[data-metric]').forEach(b=>b.setAttribute('aria-pressed',Number(b.dataset.metric)===metric))
    const max = Math.max(1,...rows.flatMap(i=>[read(i.previous,metric),read(i.current,metric)]))
    get('chart').innerHTML = rows.map(i => `<div class="series"><strong>${esc(i.name)}</strong><div class="bars">${['previous','current'].map(key => {
      const n = read(i[key],metric)
      return `<div class="barline ${key}"><span class="track"><i class="length" style="width:${100*(n||0)/max}%"></i></span><small class="num">${display(n,metric)}</small></div>`
    }).join('')}</div></div>`).join('')
    get('rows').innerHTML = rows.map(i=>{
      const a=read(i.previous,metric), b=read(i.current,metric)
      const delta=a===null||b===null ? '无基数' : (b>a?'+':'')+(metric===2?(b-a).toFixed(1)+' 个百分点':(b-a).toLocaleString('zh-CN'))
      return `<tr><th scope="row">${esc(i.name)}</th><td>${display(a,metric)}</td><td>${display(b,metric)}</td><td>${delta}</td></tr>`
    }).join('')
    get('scope').textContent = '当前指标 · '+metrics[metric]+' / '+rows.length+' 个渠道'
  }
  desk.querySelectorAll('[data-metric]').forEach(b=>b.onclick=()=>{metric=Number(b.dataset.metric);render()})
  get('channel').onchange = render
  get('export').onclick = () => {
    const field = v => '"'+(typeof v === 'number' ? String(v) : String(v).replace(/^[=+@-]/,"'$&")).replace(/"/g,'""')+'"'
    const records = [['渠道','指标',brief.previous,brief.current,metric===2?'变化（百分点）':'变化','上期'+metrics[0],'上期'+metrics[1],'本期'+metrics[0],'本期'+metrics[1]]]
    for(const i of selected()){
      const a=read(i.previous,metric), b=read(i.current,metric)
      const raw=n=>n===null?'':metric===2?n.toFixed(1)+'%':n
      const delta=a===null||b===null?'':metric===2?Number((b-a).toFixed(1)):b-a
      records.push([i.name,metrics[metric],raw(a),raw(b),delta,...i.previous,...i.current])
    }
    download(brief.id+'-report.csv','text/csv;charset=utf-8','\uFEFF'+records.map(r=>r.map(field).join(',')).join('\r\n'))
  }
  render()
}
function agenda(){
  get('cover').innerHTML = '<div aria-hidden="true" class="rosette"><i></i><i></i></div>'
  const overlap = (a,b) => Date.parse(a.start)<Date.parse(b.end) && Date.parse(b.start)<Date.parse(a.end)
  const stored = readSaved()
  const chosen = new Set()
  for(const item of items){
    if(Array.isArray(stored) && stored.includes(item.id) && !items.some(i=>chosen.has(i.id)&&overlap(i,item))) chosen.add(item.id)
  }
  const tracks = [...new Set(items.map(i=>i.track))]
  const clock = new Intl.DateTimeFormat('zh-CN',{hour:'2-digit',minute:'2-digit',hourCycle:'h23',timeZone:brief.timezone})
  const date = new Intl.DateTimeFormat('zh-CN',{year:'numeric',month:'short',day:'numeric',timeZone:brief.timezone})
  let track = ''
  desk.innerHTML = `<div class="bar"><h2>挑一堂课</h2><span>${esc(brief.timezone)}</span></div><div class="toolbar"><div class="controls">${['',...tracks].map(t=>`<button data-track="${esc(t)}">${esc(t||'全部场地')}</button>`).join('')}</div></div><div id="sessions"></div><div class="summary"><span id="count"></span><button class="solid" id="export">导出我的日历 (.ics)</button></div><p class="status" role="status" id="notice"></p>`
  function render(){
    desk.querySelectorAll('[data-track]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.track===track))
    get('sessions').innerHTML = items.filter(i=>!track||i.track===track).map(i=>`<div class="row"><time datetime="${esc(i.start)}"><small>${date.format(new Date(i.start))}</small>${clock.format(new Date(i.start))}<small>至 ${clock.format(new Date(i.end))}</small></time><div><small>${esc(i.track)} / ${esc(i.place)}</small><h3>${esc(i.name)}</h3><p>${esc(i.note)}</p></div><button data-session="${esc(i.id)}" aria-pressed="${chosen.has(i.id)}" aria-label="${chosen.has(i.id)?'移出':'加入'} · ${esc(i.name)}">${chosen.has(i.id)?'移出课表':'加入课表'}</button></div>`).join('')
    get('count').textContent='我的课表 · '+chosen.size+' 堂'
    get('export').disabled=!chosen.size
  }
  desk.addEventListener('click',e=>{
    const b=e.target.closest('button')
    if(!b) return
    if(b.hasAttribute('data-track')){track=b.dataset.track;render();return}
    if(!b.dataset.session) return
    const id=b.dataset.session, item=items.find(i=>i.id===id)
    if(chosen.delete(id)){get('notice').textContent='已移出「'+item.name+'」'}
    else {
      const clash=items.find(i=>chosen.has(i.id)&&overlap(i,item))
      if(clash){get('notice').textContent='与「'+clash.name+'」撞时了，先移出那堂再换课';return}
      chosen.add(id)
      get('notice').textContent='已加入「'+item.name+'」'
    }
    save([...chosen]);render()
    desk.querySelector('[data-session="'+id+'"]').focus()
  })
  const stamp = s => new Date(s).toISOString().replace(/[-:]/g,'').replace(/\.\d{3}/,'')
  const ical = s => s.replace(/\\/g,'\\\\').replace(/\r\n|\r|\n/g,'\\n').replace(/[,;]/g,'\\$&')
  function fold(line){
    let result='', length=0
    for(const ch of line){
      const size=new TextEncoder().encode(ch).length
      if(length+size>75){result+='\r\n ';length=1}
      result+=ch;length+=size
    }
    return result
  }
  get('export').onclick=()=>{
    const lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Joey Design//Programme//EN','CALSCALE:GREGORIAN']
    for(const i of items.filter(i=>chosen.has(i.id))){
      lines.push('BEGIN:VEVENT','UID:'+brief.id+'-'+i.id+'@joey-design.local','DTSTAMP:'+stamp(Date.now()),'DTSTART:'+stamp(i.start),'DTEND:'+stamp(i.end),'SUMMARY:'+ical(i.name),'LOCATION:'+ical(i.place),'DESCRIPTION:'+ical(i.note),'END:VEVENT')
    }
    lines.push('END:VCALENDAR')
    download(brief.id+'.ics','text/calendar;charset=utf-8',lines.map(fold).join('\r\n')+'\r\n')
  }
  render()
}
if(brief.kind==='samples') samples()
if(brief.kind==='report') report()
if(brief.kind==='agenda') agenda()
