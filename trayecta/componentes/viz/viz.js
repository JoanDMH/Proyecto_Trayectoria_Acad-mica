/* TRAYECTA · visualizaciones D3 (componente bidireccional de Streamlit sin dependencias de compilación) */
(function () {
  const send = (type, extra) => window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type }, extra || {}), '*');
  const setHeight = () => send('streamlit:setFrameHeight', { height: Math.ceil(document.body.scrollHeight) + 4 });
  const setValue = v => send('streamlit:setComponentValue', { value: v, dataType: 'json' });

  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const C = {};
  ['ink', 'ink-2', 'muted', 'grid', 's1', 's2', 's1-soft', 'crit', 'warn', 'good', 'n0', 'n1', 'n2', 'n3', 'n4'].forEach(k => C[k] = css('--' + k));
  const NIVEL = { 'Confirmado': C.crit, 'Seguimiento': C.warn, 'Sin alerta': C.good };
  const SIT = ['Sin restricciones', 'Promedio acumulado bajo', 'Máximo cuatro cursos', 'Solo puede inscribir reprobados', 'Pierde la calidad de estudiante'];
  const SITC = { 'Sin restricciones': C.n0, 'Promedio acumulado bajo': C.n1, 'Máximo cuatro cursos': C.n2,
                 'Solo puede inscribir reprobados': C.n3, 'Pierde la calidad de estudiante': C.n4 };
  const SITL = { 'Sin restricciones': '✓', 'Promedio acumulado bajo': '↓', 'Máximo cuatro cursos': '↻',
                 'Solo puede inscribir reprobados': '◐', 'Pierde la calidad de estudiante': '✕' };
  let SITINFO = {};                                     // descripciones en lenguaje claro (vienen de motor.SITUACIONES)
  const sitTexto = k => { const i = SITINFO[k]; return i ? `<br>${i.que_paso}<br><span class="k">${i.implica}</span>` : ''; };
  const fmt = (v, d = 2) => (v == null || isNaN(v)) ? '—' : Number(v).toFixed(d).replace('.', ',');
  const tip = d3.select('#tip');
  const showTip = (ev, html) => {
    tip.html(html).style('opacity', 1);
    const w = tip.node().offsetWidth, h = tip.node().offsetHeight;
    let x = ev.clientX + 14, y = ev.clientY + 14;
    if (x + w > window.innerWidth - 6) x = ev.clientX - w - 14;
    if (y + h > window.innerHeight - 6) y = ev.clientY - h - 10;
    tip.style('left', x + 'px').style('top', y + 'px');
  };
  const hideTip = () => tip.style('opacity', 0);
  const helpIcon = (sel, texto) => sel.append('span').attr('class', 'help').text('?')
    .on('mousemove', ev => showTip(ev, texto)).on('mouseleave', hideTip);
  const legend = (root, items) => {
    const l = root.append('div').attr('class', 'legend');
    items.forEach(it => { const s = l.append('span'); s.append('i').attr('class', it.line ? 'line' : null).style('background', it.color); s.append('span').text(it.label); });
  };
  const width = () => Math.max(320, document.getElementById('root').clientWidth);

  const R = {};

  /* ── Héroe de la cohorte ─────────────────────────────────────────────── */
  R.hero = (root, d) => {
    const h = root.append('div').attr('class', 'hero');
    const row = h.append('div').attr('class', 'row');
    const left = row.append('div').style('min-width', '250px');
    left.append('h1').text(d.titulo);
    left.append('div').attr('class', 'sub').text(d.subtitulo);
    const chips = left.append('div').attr('class', 'chips');
    (d.chips || []).forEach(c => chips.append('span').attr('class', 'chip').text(c));
    row.append('div').attr('class', 'big').html(`${d.n}<small>estudiantes</small>`);

    const seg = row.append('div').attr('class', 'seg-wrap');
    const top = seg.append('div').attr('class', 'seg-lbl');
    top.append('span').html('Alerta al cierre del 1.<sup>er</sup> semestre');
    const ht = top.append('span'); helpIcon(ht, d.ayuda);
    const W = 340, H = 18;
    const svg = seg.append('svg').attr('width', W).attr('height', H);
    const parts = [['Confirmado', d.confirmado], ['Seguimiento', d.seguimiento], ['Sin alerta', d.sin]];
    const tot = d3.sum(parts, p => p[1]) || 1;
    let x = 0;
    parts.forEach(([k, v]) => {
      const w = Math.max(v > 0 ? 6 : 0, (W - 4) * v / tot);
      svg.append('rect').attr('x', x).attr('height', 16).attr('rx', 4).attr('fill', NIVEL[k]).attr('width', 0)
        .on('mousemove', ev => showTip(ev, `<b>${k}</b><br>${v} estudiantes · ${fmt(100 * v / tot, 0)} %`)).on('mouseleave', hideTip)
        .transition().duration(700).attr('width', Math.max(0, w - 2));
      x += w;
    });
    const lab = seg.append('div').style('display', 'flex').style('gap', '26px').style('margin-top', '10px');
    parts.forEach(([k, v]) => {
      const b = lab.append('div');
      b.append('div').style('font-size', '28px').style('font-weight', 800).style('line-height', '1').html(
        `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${NIVEL[k]};margin-right:7px;vertical-align:5px"></span>${v}`);
      b.append('div').style('font-size', '11.5px').style('color', '#C7D2FE').style('margin-top', '3px').text(k.toLowerCase());
    });
    const r2 = row.append('div').style('display', 'flex').style('gap', '26px');
    const ring = (lbl, val, color, sub) => {
      const box = r2.append('div').style('text-align', 'center');
      const s = box.append('svg').attr('width', 92).attr('height', 92);
      const g = s.append('g').attr('transform', 'translate(46,46)');
      const arc = d3.arc().innerRadius(34).outerRadius(42).cornerRadius(4).startAngle(0);
      g.append('path').attr('d', arc.endAngle(2 * Math.PI)()).attr('fill', 'rgba(255,255,255,.13)');
      g.append('path').attr('fill', color).transition().duration(900)
        .attrTween('d', () => t => arc.endAngle(2 * Math.PI * val * t)());
      g.append('text').attr('text-anchor', 'middle').attr('dy', 7).attr('fill', '#fff').attr('font-size', 20).attr('font-weight', 800)
        .text(sub != null ? sub : fmt(100 * val, 0) + '%');
      box.append('div').style('font-size', '11.5px').style('color', '#C7D2FE').style('max-width', '110px').text(lbl);
    };
    ring('graduación esperada (media)', d.grad_media, '#34D399');
    ring('ya perdieron la calidad de estudiante', d.observados / Math.max(1, d.n), '#FCA5A5', d.observados);
  };


  /* ── Héroe del estudiante ────────────────────────────────────────────── */
  R.estudiante = (root, d) => {
    const h = root.append('div').attr('class', 'hero');
    const row = h.append('div').attr('class', 'row');
    const left = row.append('div').style('min-width', '230px');
    left.append('div').style('font-size', '12px').style('color', '#C7D2FE').style('letter-spacing', '.8px').text('FICHA DE TRAYECTORIA');
    left.append('h1').style('font-size', '34px').text(d.id);
    left.append('div').attr('class', 'sub').text(d.sub);
    const chips = left.append('div').attr('class', 'chips');
    (d.avisos || []).forEach(c => chips.append('span').attr('class', 'chip').text(c));
    const ring = (lbl, val, color, zonas, texto) => {
      const box = row.append('div').style('text-align', 'center');
      const s = box.append('svg').attr('width', 118).attr('height', 118);
      const g = s.append('g').attr('transform', 'translate(59,59)');
      const arc = d3.arc().innerRadius(42).outerRadius(53).cornerRadius(4).startAngle(0);
      g.append('path').attr('d', arc.endAngle(2 * Math.PI)()).attr('fill', 'rgba(255,255,255,.12)');
      (zonas || []).forEach(([a, b, c]) => g.append('path').attr('d', d3.arc().innerRadius(56).outerRadius(59).startAngle(2 * Math.PI * a).endAngle(2 * Math.PI * b)()).attr('fill', c));
      g.append('path').attr('fill', color).transition().duration(900).attrTween('d', () => t => arc.endAngle(2 * Math.PI * val * t)());
      g.append('text').attr('text-anchor', 'middle').attr('dy', 8).attr('fill', '#fff').attr('font-size', 24).attr('font-weight', 800).text(fmt(val));
      box.append('div').style('font-size', '12px').style('color', '#E0E7FF').style('font-weight', 700).text(texto);
      box.append('div').style('font-size', '11px').style('color', '#A5B4FC').text(lbl);
    };
    ring('riesgo académico', d.p, NIVEL[d.nivel], d.zonas, d.nivel);
    ring('probabilidad de graduación', d.g, '#34D399', null, 'Graduación');
    const facts = row.append('div').style('display', 'grid').style('grid-template-columns', 'auto auto').style('gap', '6px 22px')
      .style('font-size', '13px').style('color', '#C7D2FE');
    (d.hechos || []).forEach(([k, v]) => { facts.append('div').text(k); facts.append('div').style('color', '#fff').style('font-weight', 700).text(v); });
  };


  /* ── Validación de una cohorte cargada ───────────────────────────────── */
  R.carga = (root, d) => {
    const h = root.append('div').attr('class', 'hero');
    const row = h.append('div').attr('class', 'row');
    const left = row.append('div').style('min-width', '220px');
    left.append('div').style('font-size', '12px').style('color', '#C7D2FE').style('letter-spacing', '.8px').text('VALIDACIÓN DE LA COHORTE');
    left.append('h1').text(d.ok ? '✓ Lista para procesar' : '⚠ Revise los avisos');
    const chips = left.append('div').attr('class', 'chips');
    d.planes.forEach(p => chips.append('span').attr('class', 'chip').text('plan ' + p));
    [[d.estudiantes, 'estudiantes'], [d.registros, 'registros de notas'], [d.fuera, 'códigos fuera del catálogo'], [d.mezcla, 'con planes mezclados']]
      .forEach(([v, l]) => row.append('div').attr('class', 'big').style('font-size', '40px').html(`${v}<small>${l}</small>`));
    const seg = row.append('div').style('flex', '1 1 280px');
    seg.append('div').attr('class', 'seg-lbl').html('<span>Cómo se tradujo cada registro</span>');
    const W = Math.max(260, Math.min(420, seg.node().clientWidth || 360));
    const svg = seg.append('svg').attr('width', W).attr('height', 18);
    const col = { 'Curso del plan 2018': '#67E8F9', 'Equivalencia oficial 2011 → 2018': '#A5B4FC', 'Curso institucional': '#F9A8D4', 'Curso 2011 sin equivalente': '#FCD34D', 'Código no reconocido': '#FCA5A5' };
    const tot = d3.sum(d.fuentes, f => f.n) || 1; let x = 0;
    d.fuentes.forEach(f => {
      const w = Math.max(4, (W - 4) * f.n / tot);
      svg.append('rect').attr('x', x).attr('height', 16).attr('rx', 4).attr('fill', col[f.fuente] || '#fff').attr('width', Math.max(0, w - 2))
        .on('mousemove', ev => showTip(ev, `<b>${f.fuente}</b><br>${f.n} registros · ${fmt(100 * f.n / tot, 0)} %`)).on('mouseleave', hideTip);
      x += w;
    });
    const lg = seg.append('div').style('display', 'flex').style('flex-wrap', 'wrap').style('gap', '6px 14px').style('margin-top', '8px')
      .style('font-size', '11.5px').style('color', '#E0E7FF');
    d.fuentes.forEach(f => lg.append('span').html(`<span style="display:inline-block;width:9px;height:9px;border-radius:3px;background:${col[f.fuente] || '#fff'};margin-right:5px"></span>${f.fuente} · ${f.n}`));
  };

  /* ── Enjambre de riesgo (un punto = un estudiante) ───────────────────── */
  R.enjambre = (root, d) => {
    const W = width(), H = d.alto || 300, m = { l: 18, r: 18, t: 34, b: 34 };
    const xmax = Math.max(0.85, d3.max(d.estudiantes, e => e.p) + 0.05);
    const x = d3.scalePow().exponent(0.5).domain([0, xmax]).range([m.l, W - m.r]);
    const svg = root.append('svg').attr('width', W).attr('height', H);
    const ue = d.umbrales.equilibrado, uc = d.umbrales.confirmado;
    const zonas = [['Sin alerta', 0, ue], ['Seguimiento', ue, uc], ['Confirmado', uc, xmax]];
    zonas.forEach(([k, a, b]) => {
      svg.append('rect').attr('x', x(a)).attr('y', m.t - 8).attr('width', Math.max(0, x(b) - x(a))).attr('height', H - m.t - m.b + 8)
        .attr('fill', NIVEL[k]).attr('opacity', .07).attr('rx', 6);
      svg.append('text').attr('x', (x(a) + x(b)) / 2).attr('y', 16).attr('text-anchor', 'middle').attr('font-size', 12)
        .attr('font-weight', 700).attr('fill', NIVEL[k]).text(k.toUpperCase());
    });
    [ue, uc].forEach(u => {
      svg.append('line').attr('x1', x(u)).attr('x2', x(u)).attr('y1', m.t - 8).attr('y2', H - m.b).attr('stroke', C.ink).attr('stroke-dasharray', '3 4').attr('opacity', .45);
      svg.append('text').attr('x', x(u) + 4).attr('y', H - m.b - 6).attr('font-size', 10.5).attr('fill', C['ink-2']).text('umbral ' + fmt(u));
    });
    svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`)
      .call(d3.axisBottom(x).tickValues([0, .02, .05, .1, .2, .3, .4, .5, .6, .8].filter(v => v <= xmax)).tickFormat(v => fmt(v, 2)).tickSizeOuter(0));
    svg.append('text').attr('x', W - m.r).attr('y', H - 4).attr('text-anchor', 'end').attr('font-size', 11).attr('fill', C.muted)
      .text('puntaje de riesgo académico →');
    const r = d.estudiantes.length > 120 ? 4.5 : 6.5;
    const nodes = d.estudiantes.map(e => Object.assign({}, e, { x: x(e.p), y: (H - m.b + m.t) / 2 }));
    const sim = d3.forceSimulation(nodes).force('x', d3.forceX(n => x(n.p)).strength(1))
      .force('y', d3.forceY((H - m.b + m.t) / 2).strength(0.06)).force('c', d3.forceCollide(r + 1.2)).stop();
    for (let i = 0; i < 260; i++) sim.tick();
    const g = svg.append('g');
    g.selectAll('circle').data(nodes).join('circle')
      .attr('cx', n => n.x).attr('cy', n => Math.max(m.t, Math.min(H - m.b - r, n.y))).attr('r', 0)
      .attr('fill', n => NIVEL[n.nivel]).attr('stroke', n => n.obs ? C.ink : '#fff').attr('stroke-width', n => n.obs ? 1.6 : 1.4)
      .style('cursor', 'pointer')
      .on('mousemove', (ev, n) => {
        d3.select(ev.currentTarget).attr('r', r + 3);
        showTip(ev, `<b>${n.id}</b> · ${n.nivel}<br><span class="k">puntaje</span> ${fmt(n.p)} · <span class="k">graduación</span> ${fmt(n.g)}` +
          `<br><span class="k">semestres</span> ${n.sem ?? '—'} · ${n.sit || ''}${n.obs ? '<br>⚑ ya perdió la calidad de estudiante' : ''}<br><span class="k">clic para abrir la ficha</span>`);
      })
      .on('mouseleave', ev => { d3.select(ev.currentTarget).attr('r', r); hideTip(); })
      .on('click', (ev, n) => setValue({ accion: 'ficha', id: n.id, t: Date.now() }))
      .transition().delay((n, i) => i * 6).duration(400).attr('r', r);
  };

  /* ── Situación normativa por semestre (columnas apiladas) ───────────── */
  R.situacion = (root, d) => {
    legend(root, SIT.map(s => ({ label: s, color: SITC[s] })));
    const W = width(), H = d.alto || 290, m = { l: 36, r: 8, t: 8, b: 34 };
    const sems = [...new Set(d.filas.map(f => f.semestre))].sort((a, b) => a - b);
    const tabla = sems.map(s => { const o = { semestre: s }; SIT.forEach(k => o[k] = 0); d.filas.filter(f => f.semestre === s).forEach(f => o[f.situacion] = f.n); return o; });
    const st = d3.stack().keys(SIT)(tabla);
    const x = d3.scaleBand().domain(sems).range([m.l, W - m.r]).padding(0.28);
    const y = d3.scaleLinear().domain([0, d3.max(tabla, t => d3.sum(SIT, k => t[k]))]).nice().range([H - m.b, m.t]);
    const svg = root.append('svg').attr('width', W).attr('height', H);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).select('.domain').remove();
    svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSizeOuter(0)).select('.domain').remove();
    svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickFormat(s => s + '.º').tickSizeOuter(0));
    svg.append('g').selectAll('g').data(st).join('g').attr('fill', s => SITC[s.key])
      .selectAll('rect').data(s => s.map(v => Object.assign(v, { key: s.key }))).join('rect')
      .attr('x', v => x(v.data.semestre)).attr('width', x.bandwidth())
      .attr('y', H - m.b).attr('height', 0).attr('rx', 3)
      .on('mousemove', (ev, v) => {
        const tot = d3.sum(SIT, k => v.data[k]);
        showTip(ev, `<b>${v.data.semestre}.º semestre</b> · ${v.key}: <b>${v[1] - v[0]}</b> de ${tot} estudiantes${sitTexto(v.key)}`);
      }).on('mouseleave', hideTip)
      .transition().duration(600).delay((v, i) => i * 30)
      .attr('y', v => y(v[1]) + 1).attr('height', v => Math.max(0, y(v[0]) - y(v[1]) - 2));
  };

  /* ── Trayectoria de un estudiante (dos paneles con eje x compartido) ── */
  R.trayectoria = (root, d) => {
    legend(root, [{ label: 'promedio acumulado', color: C.s1, line: 1 }, { label: 'promedio del periodo', color: C.s2, line: 1 },
                  { label: 'créditos aprobados', color: C['s1-soft'] }, { label: 'créditos reprobados', color: C.n3 }]);
    const S = d.semestres, W = width(), m = { l: 40, r: 14 };
    const H1 = 210, Hs = 44, H2 = 120, H = H1 + Hs + H2 + 30;
    const x = d3.scalePoint().domain(S.map(s => s.semestre)).range([m.l + 24, W - m.r - 24]);
    const svg = root.append('svg').attr('width', W).attr('height', H);
    const y1 = d3.scaleLinear().domain([0, 5]).range([H1 - 10, 12]);
    svg.append('rect').attr('x', m.l).attr('y', y1(3)).attr('width', W - m.l - m.r).attr('height', y1(0) - y1(3)).attr('fill', C.crit).attr('opacity', .05);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y1).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).select('.domain').remove();
    svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y1).ticks(5).tickSizeOuter(0)).select('.domain').remove();
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y1(3)).attr('y2', y1(3)).attr('stroke', C.crit).attr('stroke-dasharray', '4 4').attr('opacity', .7);
    svg.append('text').attr('x', W - m.r).attr('y', y1(3) - 5).attr('text-anchor', 'end').attr('font-size', 10.5).attr('fill', C.crit).text('3,0 · mínimo aprobatorio');
    const line = k => d3.line().defined(s => s[k] != null).x(s => x(s.semestre)).y(s => y1(s[k])).curve(d3.curveMonotoneX);
    [['prom_periodo', C.s2], ['prom_acum', C.s1]].forEach(([k, c]) => {
      const p = svg.append('path').datum(S).attr('fill', 'none').attr('stroke', c).attr('stroke-width', k === 'prom_acum' ? 2.6 : 2).attr('d', line(k));
      const L = p.node().getTotalLength(); p.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L).transition().duration(900).attr('stroke-dashoffset', 0);
      svg.append('g').selectAll('circle').data(S.filter(s => s[k] != null)).join('circle').attr('cx', s => x(s.semestre)).attr('cy', s => y1(s[k]))
        .attr('r', 4.5).attr('fill', c).attr('stroke', '#fff').attr('stroke-width', 2);
    });
    // franja de situación normativa
    const ys = H1 + 6;
    svg.append('text').attr('x', m.l - 4).attr('y', ys + 20).attr('text-anchor', 'end').attr('font-size', 10).attr('fill', C.muted).text('estado');
    const chip = svg.append('g').selectAll('g').data(S).join('g').attr('transform', s => `translate(${x(s.semestre)},${ys + 16})`);
    chip.append('rect').attr('x', -15).attr('y', -13).attr('width', 30).attr('height', 26).attr('rx', 7).attr('fill', s => SITC[s.situacion] || C.n0);
    chip.append('text').attr('text-anchor', 'middle').attr('dy', 4.5).attr('font-size', 11).attr('font-weight', 700)
      .attr('fill', s => s.situacion === 'Sin restricciones' ? C['ink-2'] : '#fff').text(s => SITL[s.situacion] || '·');
    chip.style('cursor', 'help').on('mousemove', (ev, s) => showTip(ev, `<b>${s.semestre}.º semestre · ${s.situacion}</b>${sitTexto(s.situacion)}`)).on('mouseleave', hideTip);
    // créditos
    const y2top = H1 + Hs + 6, y2 = d3.scaleLinear().domain([0, Math.max(20, d3.max(S, s => s.cred_aprob + s.cred_reprob))]).range([y2top + H2, y2top]);
    svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y2).ticks(3).tickSizeOuter(0)).select('.domain').remove();
    const bw = Math.min(34, (W - m.l - m.r) / S.length * 0.5);
    S.forEach(s => {
      const cx = x(s.semestre);
      svg.append('rect').attr('x', cx - bw / 2).attr('width', bw).attr('rx', 4).attr('fill', C['s1-soft'])
        .attr('y', y2(0)).attr('height', 0).transition().duration(600).attr('y', y2(s.cred_aprob)).attr('height', Math.max(0, y2(0) - y2(s.cred_aprob)));
      if (s.cred_reprob > 0) svg.append('rect').attr('x', cx - bw / 2).attr('width', bw).attr('rx', 4).attr('fill', C.n3)
        .attr('y', y2(s.cred_aprob + s.cred_reprob)).attr('height', Math.max(0, y2(s.cred_aprob) - y2(s.cred_aprob + s.cred_reprob) - 2));
    });
    svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${y2top + H2})`).call(d3.axisBottom(x).tickFormat(s => s + '.º').tickSizeOuter(0)).select('.domain').attr('stroke', C.grid);
    // capa de lectura (cruz vertical + detalle)
    const cross = svg.append('line').attr('y1', 8).attr('y2', y2top + H2).attr('stroke', C.ink).attr('opacity', 0);
    const step = S.length > 1 ? x(S[1].semestre) - x(S[0].semestre) : W;
    S.forEach(s => {
      svg.append('rect').attr('x', x(s.semestre) - step / 2).attr('width', step).attr('y', 0).attr('height', y2top + H2).attr('fill', 'transparent')
        .on('mousemove', ev => {
          cross.attr('x1', x(s.semestre)).attr('x2', x(s.semestre)).attr('opacity', .15);
          showTip(ev, `<b>${s.semestre}.º semestre</b> · ${s.periodo} · ${s.plan}<br><span class="k">promedio del periodo</span> ${fmt(s.prom_periodo)}` +
            `<br><span class="k">promedio acumulado</span> ${fmt(s.prom_acum)}<br><span class="k">créditos</span> ${s.cred_aprob + s.cred_reprob} · reprobados ${s.cred_reprob}` +
            `<br><b>${s.situacion}</b>${sitTexto(s.situacion)}`);
        }).on('mouseleave', () => { cross.attr('opacity', 0); hideTip(); });
    });
    const ls = root.append('div').attr('class', 'legend').style('margin-top', '4px');
    SIT.forEach(k => { const sp = ls.append('span').style('cursor', 'help');
      sp.append('b').style('display', 'inline-flex').style('align-items', 'center').style('justify-content', 'center').style('width', '18px').style('height', '16px')
        .style('border-radius', '4px').style('font-size', '10px').style('background', SITC[k]).style('color', k === SIT[0] ? C['ink-2'] : '#fff').text(SITL[k]);
      sp.append('span').style('margin-left', '6px').text(k);
      sp.on('mousemove', ev => showTip(ev, `<b>${k}</b>${sitTexto(k)}`)).on('mouseleave', hideTip); });
  };

  /* ── Perfil de ingreso frente a la cohorte ───────────────────────────── */
  R.perfil = (root, d) => {
    const W = width(), rowH = 46, m = { l: 168, r: 70, t: 6 }, H = m.t + rowH * d.vars.length + 8;
    const svg = root.append('svg').attr('width', W).attr('height', H);
    d.vars.forEach((v, i) => {
      const y0 = m.t + i * rowH + rowH / 2;
      const ext = d3.extent(v.cohorte.concat([v.valor]));
      const x = d3.scaleLinear().domain(ext).nice().range([m.l, W - m.r]);
      svg.append('text').attr('x', m.l - 12).attr('y', y0 + 4).attr('text-anchor', 'end').attr('font-size', 12.5).attr('fill', C['ink-2']).text(v.nombre);
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y0).attr('y2', y0).attr('stroke', C.grid).attr('stroke-width', 8).attr('stroke-linecap', 'round');
      const q = d3.quantile(v.cohorte.slice().sort(d3.ascending), 0.5);
      svg.append('g').selectAll('circle').data(v.cohorte).join('circle').attr('cx', c => x(c)).attr('cy', (c, j) => y0 + ((j * 7919) % 11 - 5))
        .attr('r', 2.4).attr('fill', C.muted).attr('opacity', .35);
      svg.append('line').attr('x1', x(q)).attr('x2', x(q)).attr('y1', y0 - 10).attr('y2', y0 + 10).attr('stroke', C['ink-2']).attr('stroke-width', 1.5);
      const pct = 100 * v.cohorte.filter(c => c <= v.valor).length / v.cohorte.length;
      const col = pct < 25 ? C.crit : pct < 50 ? C.warn : C.good;
      svg.append('circle').attr('cx', x(v.valor)).attr('cy', y0).attr('r', 0).attr('fill', col).attr('stroke', '#fff').attr('stroke-width', 2.5)
        .on('mousemove', ev => showTip(ev, `<b>${v.nombre}</b><br>valor ${fmt(v.valor, v.dec)} · mediana de la cohorte ${fmt(q, v.dec)}<br>percentil ${fmt(pct, 0)}`))
        .on('mouseleave', hideTip).transition().duration(600).attr('r', 8.5);
      svg.append('text').attr('x', W - m.r + 10).attr('y', y0 + 4).attr('font-size', 12.5).attr('font-weight', 700).attr('fill', C.ink)
        .text(`p${fmt(pct, 0)}`);
    });
  };

  /* ── Barras horizontales con línea base ──────────────────────────────── */
  R.barras = (root, d) => {
    const W = width(), rowH = d.fila || 34, m = { l: d.margen || 170, r: 56, t: 22, b: 26 }, H = m.t + rowH * d.items.length + m.b;
    const x = d3.scaleLinear().domain([0, d.xmax || 1]).range([m.l, W - m.r]);
    const svg = root.append('svg').attr('width', W).attr('height', H);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickSize(-(H - m.t - m.b)).tickFormat('')).select('.domain').remove();
    svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickFormat(v => fmt(v, 1)).tickSizeOuter(0));
    d.items.forEach((it, i) => {
      const y = m.t + i * rowH + 6, h = rowH - 12;
      const col = it.destacado ? (d.color || C.s1) : (d.color2 || C['s1-soft']);
      svg.append('text').attr('x', m.l - 10).attr('y', y + h / 2 + 4).attr('text-anchor', 'end').attr('font-size', 12.5)
        .attr('font-weight', it.destacado ? 700 : 500).attr('fill', C.ink).text(it.nombre);
      svg.append('rect').attr('x', m.l).attr('y', y).attr('height', h).attr('rx', 4).attr('fill', col).attr('width', 0)
        .on('mousemove', ev => showTip(ev, `<b>${it.nombre}</b><br>${fmt(it.valor, 3)}${it.sd ? ' ± ' + fmt(it.sd, 3) : ''}${it.nota ? '<br>' + it.nota : ''}`))
        .on('mouseleave', hideTip).transition().duration(700).delay(i * 60).attr('width', Math.max(0, x(it.valor) - m.l));
      if (it.sd) svg.append('line').attr('x1', x(it.valor - it.sd)).attr('x2', x(it.valor + it.sd)).attr('y1', y + h / 2).attr('y2', y + h / 2)
        .attr('stroke', C.ink).attr('stroke-width', 1.4).attr('opacity', .55);
      svg.append('text').attr('x', x(it.valor + (it.sd || 0)) + 6).attr('y', y + h / 2 + 4).attr('font-size', 12).attr('font-weight', 700)
        .attr('fill', C.ink).text(fmt(it.valor, 3));
    });
    if (d.base != null) {
      svg.append('line').attr('x1', x(d.base)).attr('x2', x(d.base)).attr('y1', m.t - 6).attr('y2', H - m.b).attr('stroke', C.crit).attr('stroke-width', 1.6).attr('stroke-dasharray', '5 4');
      svg.append('text').attr('x', x(d.base) + 5).attr('y', m.t - 8).attr('font-size', 11).attr('font-weight', 600).attr('fill', C.crit).text(d.base_label || ('azar ' + fmt(d.base, 3)));
    }
  };

  /* ── Curva de umbral ─────────────────────────────────────────────────── */
  R.curva = (root, d) => {
    const series = [['recall', 'casos detectados', C.s1], ['precision', 'alertas acertadas', C.s2], ['pct', '% de la cohorte alertada', C.muted]];
    legend(root, series.map(s => ({ label: s[1], color: s[2], line: 1 })));
    const W = width(), H = d.alto || 260, m = { l: 38, r: 14, t: 10, b: 30 };
    const x = d3.scaleLinear().domain([0, d3.max(d.filas, f => f.umbral)]).range([m.l, W - m.r]);
    const y = d3.scaleLinear().domain([0, 1]).range([H - m.b, m.t]);
    const svg = root.append('svg').attr('width', W).attr('height', H);
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat('')).select('.domain').remove();
    svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(v => fmt(v, 1))).select('.domain').remove();
    svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(8).tickFormat(v => fmt(v, 1)).tickSizeOuter(0));
    (d.marcas || []).forEach(mk => {
      svg.append('line').attr('x1', x(mk.u)).attr('x2', x(mk.u)).attr('y1', m.t).attr('y2', H - m.b).attr('stroke', NIVEL[mk.nombre] || C.ink).attr('stroke-width', 1.5).attr('stroke-dasharray', '4 4');
      svg.append('text').attr('x', x(mk.u) + 4).attr('y', m.t + 12).attr('font-size', 11).attr('font-weight', 700).attr('fill', NIVEL[mk.nombre] || C.ink).text(mk.nombre);
    });
    series.forEach(([k, , c]) => svg.append('path').datum(d.filas).attr('fill', 'none').attr('stroke', c).attr('stroke-width', 2)
      .attr('stroke-dasharray', k === 'pct' ? '2 3' : null).attr('d', d3.line().x(f => x(f.umbral)).y(f => y(f[k])).curve(d3.curveStepAfter)));
    const cross = svg.append('line').attr('y1', m.t).attr('y2', H - m.b).attr('stroke', C.ink).attr('opacity', 0);
    svg.append('rect').attr('x', m.l).attr('y', m.t).attr('width', W - m.l - m.r).attr('height', H - m.t - m.b).attr('fill', 'transparent')
      .on('mousemove', ev => {
        const u = x.invert(d3.pointer(ev)[0]);
        const f = d.filas.reduce((a, b) => Math.abs(b.umbral - u) < Math.abs(a.umbral - u) ? b : a);
        cross.attr('x1', x(f.umbral)).attr('x2', x(f.umbral)).attr('opacity', .25);
        showTip(ev, `<b>umbral ${fmt(f.umbral)}</b><br>detecta ${fmt(100 * f.recall, 0)} % · acierta ${fmt(100 * f.precision, 0)} %<br>alerta a ${f.alertas} estudiantes (${fmt(100 * f.pct, 0)} %)`);
      }).on('mouseleave', () => { cross.attr('opacity', 0); hideTip(); });
  };

  /* ── Indicador semicircular ──────────────────────────────────────────── */
  R.gauge = (root, d) => {
    const W = Math.min(width(), 380), H = 210, cx = W / 2, cy = 150, ro = 120, ri = 92;
    const svg = root.append('svg').attr('width', W).attr('height', H).style('display', 'block').style('margin', '0 auto');
    const a = d3.scaleLinear().domain([0, 1]).range([-Math.PI / 2, Math.PI / 2]);
    const arc = d3.arc().innerRadius(ri).outerRadius(ro).cornerRadius(3);
    const g = svg.append('g').attr('transform', `translate(${cx},${cy})`);
    (d.zonas || [[0, 1, d.color || C.s1]]).forEach(([s, e, c]) => g.append('path').attr('d', arc({ startAngle: a(s), endAngle: a(e) - 0.012 })).attr('fill', c).attr('opacity', d.zonas ? .22 : .15));
    g.append('path').attr('fill', d.color || C.s1).transition().duration(900).attrTween('d', () => t => arc({ startAngle: a(0), endAngle: a(d.valor * t) }));
    const nd = g.append('line').attr('x1', 0).attr('y1', 0).attr('x2', 0).attr('y2', -(ri - 10)).attr('stroke', C.ink).attr('stroke-width', 3).attr('stroke-linecap', 'round')
      .attr('transform', 'rotate(-90)');
    nd.transition().duration(900).attr('transform', `rotate(${a(d.valor) * 180 / Math.PI})`);
    g.append('circle').attr('r', 6).attr('fill', C.ink);
    g.append('text').attr('text-anchor', 'middle').attr('y', 46).attr('font-size', 34).attr('font-weight', 800).attr('fill', C.ink).text(fmt(d.valor));
    if (d.etiqueta) g.append('text').attr('text-anchor', 'middle').attr('y', -ro - 12).attr('font-size', 13).attr('font-weight', 700).attr('fill', d.color || C.ink).text(d.etiqueta);
  };

  let ultimo = null;
  function render(args) {
    const key = JSON.stringify(args);
    if (key === ultimo) return; ultimo = key;
    const root = d3.select('#root'); root.html('');
    const datos = typeof args.datos === 'string' ? JSON.parse(args.datos) : args.datos;
    if (datos && datos.sit_info) SITINFO = datos.sit_info;
    if (args.titulo) {
      const h = root.append('div').style('display', 'flex').style('align-items', 'center').style('margin', '2px 0 6px')
        .style('font-weight', 700).style('font-size', '15px').style('color', C.ink);
      h.append('span').text(args.titulo);
      if (args.ayuda) helpIcon(h, args.ayuda).style('color', C.muted);
    }
    try { R[args.tipo](root, datos); } catch (e) { root.append('pre').text(String(e && e.stack || e)); }
    setTimeout(setHeight, 30); setTimeout(setHeight, 700);
  }
  window.addEventListener('message', ev => { if (ev.data && ev.data.type === 'streamlit:render') render(ev.data.args); });
  window.addEventListener('resize', () => { ultimo = null; });
  send('streamlit:componentReady', { apiVersion: 1 });
})();
