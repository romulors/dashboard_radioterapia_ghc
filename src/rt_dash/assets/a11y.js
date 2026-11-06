/*
 * Acessibilidade dos gráficos (WCAG 2.2 AA / EN 301 549, cláusula 9).
 *
 * 1. Texto alternativo e tabela de dados gerados dos próprios dados a cada desenho (1.1.1, 1.3.1):
 *    o resumo vai para o <figcaption> visível e para o aria-label do SVG; a tabela vai para "Ver dados em tabela".
 * 2. Modo alto contraste (1.4.1, 1.4.11): troca cores por versões sólidas escuras (window.RT_A11Y.mapa, vindo de
 *    viz/theme.py) e acrescenta hachura nas barras, traço nas linhas e símbolo nos marcadores.
 * 3. Abas navegáveis pelas setas, Home e End (2.1.1, 4.1.2).
 */
(function () {
  "use strict";
  var CFG = window.RT_A11Y || { mapa: {}, escala: null, padroes: [""], tracos: ["solid"], simbolos: ["circle"] };
  var MAX_LINHAS = 400;

  // ------------------------------------------------------------------ formatação
  function num(v, casas) {
    if (v === null || v === undefined || v === "" || isNaN(v)) return "–";
    var n = Number(v);
    if (casas === undefined) casas = Math.abs(n) >= 100 || Number.isInteger(n) ? 0 : Math.abs(n) < 1 ? 2 : 1;
    return n.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
  }
  function rotulo(v) {
    if (v === null || v === undefined) return "";
    var s = String(v);
    var m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (m) return m[3] + "/" + m[2] + "/" + m[1];
    return s;
  }
  function arr(a) {
    if (!a) return [];
    if (Array.isArray(a)) return a;
    if (a.length !== undefined) return Array.prototype.slice.call(a);
    return [];
  }
  function visiveis(gd) {
    // ignora traços auxiliares (hastes do lollipop/barbell, linhas de ligação) e séries ocultas pela legenda
    // _fullData traz os arrays já decodificados (o Dash envia números como binário base64 em gd.data)
    return (gd._fullData || gd.data || []).filter(function (t) {
      if (t.visible === false || t.visible === "legendonly") return false;
      return !(t.hoverinfo === "skip" && t.showlegend === false);
    });
  }
  function nomeTrace(t, i) {
    var n = t.name || "";
    return n && !/^trace \d+$/.test(n) ? String(n).replace(/<[^>]+>/g, "") : "Série " + (i + 1);
  }
  function horizontal(t) {
    return t.orientation === "h";
  }
  function ehNumero(v) {
    return typeof v === "number" || (typeof v === "string" && v !== "" && !isNaN(v) && !/^\d{4}-\d{2}/.test(v));
  }
  function deitado(t) {
    // horizontal declarado (barras) ou implícito (pontos com categorias no eixo y: barbell, lollipop)
    var x = arr(t.x), y = arr(t.y);
    return horizontal(t) || (x.length > 0 && ehNumero(x[0]) && y.length > 0 && typeof y[0] === "string" && !ehNumero(y[0]));
  }
  function pares(t) {
    return deitado(t) ? { cat: arr(t.y), val: arr(t.x) } : { cat: arr(t.x), val: arr(t.y) };
  }
  function mediana(v) {
    var s = v.filter(function (a) { return a !== null && !isNaN(a); }).map(Number).sort(function (a, b) { return a - b; });
    return s.length ? s[Math.floor(s.length / 2)] : NaN;
  }
  function tituloEixo(gd, eixo) {
    var ax = gd._fullLayout && gd._fullLayout[eixo];
    var txt = ax && ax.visible !== false && ax.title && ax.title.text ? ax.title.text : "";
    return /^Click to enter/.test(txt) ? "" : txt;
  }
  function percentual(gd, t) {
    var ax = deitado(t) ? gd.layout.xaxis : (t.yaxis === "y2" ? gd.layout.yaxis2 : gd.layout.yaxis);
    return ax && ax.tickformat && String(ax.tickformat).indexOf("%") >= 0;
  }
  function fmtValor(gd, t, v) {
    return percentual(gd, t) ? num(v * 100, 0) + "%" : num(v);
  }

  // ------------------------------------------------------------------ resumo em texto
  function resumoTrace(gd, t, i) {
    var nome = nomeTrace(t, i);
    if (t.type === "indicator") {
      if (t.title && t.title.text) nome = t.title.text;
      var suf = (t.number && t.number.suffix) || "";
      return nome.replace(/<[^>]+>/g, "") + ": " + num(t.value, 0) + suf + (t.gauge && t.gauge.threshold && t.gauge.threshold.value ? "; meta em " + num(t.gauge.threshold.value, 0) + suf : "");
    }
    if (t.type === "heatmap") {
      var z = arr(t.z), xs = arr(t.x), ys = arr(t.y), max = -Infinity, min = Infinity, pmax = null;
      z.forEach(function (linha, r) {
        arr(linha).forEach(function (v, c) {
          if (v === null || isNaN(v)) return;
          if (v > max) { max = v; pmax = [ys[r], xs[c]]; }
          if (v < min) min = v;
        });
      });
      if (!isFinite(max)) return "Mapa de calor sem valores.";
      return "Mapa de calor com valores de " + num(min) + " a " + num(max) + "; maior valor em " + rotulo(pmax[0]) + ", " + rotulo(pmax[1]) + ".";
    }
    if (t.gauge && t.gauge.threshold && !t.gauge.threshold.value) { /* sem meta */ }
    if (t.type === "histogram") {
      var hv = arr(t.x).length ? arr(t.x) : arr(t.y);
      return nome + ": " + hv.length + " registros, mediana " + num(mediana(hv)) + ".";
    }
    var textos = arr(t.text);
    if (textos.length && textos.every(function (x) { return x === "✓" || x === "✕"; })) {
      var ok = textos.filter(function (x) { return x === "✓"; }).length;
      return nome + ": " + ok + " meses dentro da meta e " + (textos.length - ok) + " fora.";
    }
    var xs0 = arr(t.x), ys0 = arr(t.y);
    if ((t.type || "scatter") === "scatter" && xs0.length && ehNumero(xs0[0]) && ys0.length && ehNumero(ys0[0])) {
      var ex = tituloEixo(gd, "xaxis"), ey = tituloEixo(gd, "yaxis");
      var partes = [nome + ": " + xs0.length + (xs0.length === 1 ? " ponto" : " pontos")];
      if (ex) partes.push(ex + ", mediana " + num(mediana(xs0)));
      if (ey) partes.push(ey + ", mediana " + num(mediana(ys0)));
      return partes.join("; ") + ".";
    }
    if (t.type === "violin" || t.type === "box") {
      var vals = arr(horizontal(t) ? t.x : t.y).filter(function (v) { return v !== null && !isNaN(v); }).sort(function (a, b) { return a - b; });
      if (!vals.length) return "";
      return nome + ": " + vals.length + " valores, mediana " + num(vals[Math.floor(vals.length / 2)]) + ".";
    }
    if (t.type === "funnel") {
      var p = pares({ x: t.x, y: t.y, orientation: "h" });
      return "Funil: " + p.cat.map(function (c, k) { return rotulo(c) + " " + num(p.val[k]); }).join(", ") + ".";
    }
    var pr = pares(t);
    var val = pr.val.map(Number);
    var idx = val.map(function (v, k) { return k; }).filter(function (k) { return !isNaN(val[k]); });
    if (!idx.length) return "";
    if (idx.length === 1) return nome + ": " + fmtValor(gd, t, val[idx[0]]) + (pr.cat.length ? " em " + rotulo(pr.cat[idx[0]]) : "") + ".";
    var unicas = {};
    idx.forEach(function (k) { unicas[pr.cat[k]] = 1; });
    if (Object.keys(unicas).length === 1) {
      var vs = idx.map(function (k) { return val[k]; });
      return nome + ": " + vs.length + " pontos, de " + fmtValor(gd, t, Math.min.apply(null, vs)) + " a " + fmtValor(gd, t, Math.max.apply(null, vs)) + ", mediana " + fmtValor(gd, t, mediana(vs)) + ".";
    }
    var kmax = idx.reduce(function (a, b) { return val[b] > val[a] ? b : a; });
    var kmin = idx.reduce(function (a, b) { return val[b] < val[a] ? b : a; });
    var primeiro = idx[0], ultimo = idx[idx.length - 1];
    var categorico = typeof pr.cat[0] === "string" && !/^\d{4}-\d{2}-\d{2}/.test(pr.cat[0]);
    if (categorico && t.type === "bar" && horizontal(t)) {
      return nome + ": maior " + rotulo(pr.cat[kmax]) + " (" + fmtValor(gd, t, val[kmax]) + "), menor " + rotulo(pr.cat[kmin]) + " (" + fmtValor(gd, t, val[kmin]) + "); " + idx.length + " categorias.";
    }
    return nome + ": de " + fmtValor(gd, t, val[primeiro]) + " (" + rotulo(pr.cat[primeiro]) + ") a " + fmtValor(gd, t, val[ultimo]) + " (" + rotulo(pr.cat[ultimo]) + "); máximo " + fmtValor(gd, t, val[kmax]) + " em " + rotulo(pr.cat[kmax]) + ", mínimo " + fmtValor(gd, t, val[kmin]) + " em " + rotulo(pr.cat[kmin]) + ".";
  }

  function titulo(gd) {
    var fig = gd.closest("figure");
    var cartao = fig && fig.closest(".cartao, .slide, .card");
    var h = cartao && cartao.querySelector(".cartao-titulo, .slide-titulo");
    return h ? h.textContent.trim() : "Gráfico";
  }

  function resumo(gd) {
    var ts = visiveis(gd);
    if (!ts.length) {
      var aviso = (gd.layout.annotations || []).map(function (a) { return a.text; }).join(" ");
      return titulo(gd) + ". " + (aviso || "Sem dados para os filtros atuais.");
    }
    var partes = ts.slice(0, 5).map(function (t, i) { return resumoTrace(gd, t, i); }).filter(Boolean);
    var extra = ts.length > 5 ? " Mais " + (ts.length - 5) + " séries na tabela." : "";
    return titulo(gd) + ". " + partes.join(" ") + extra;
  }

  // ------------------------------------------------------------------ tabela equivalente
  function el(tag, texto, attrs) {
    var e = document.createElement(tag);
    if (texto !== undefined && texto !== null) e.textContent = texto;
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    return e;
  }

  function tabela(gd) {
    var ts = visiveis(gd);
    var tab = el("table", null, { class: "tabela-dados" });
    tab.appendChild(el("caption", "Dados de: " + titulo(gd)));
    var thead = el("thead"), tbody = el("tbody"), cab = el("tr");
    thead.appendChild(cab);
    tab.appendChild(thead);
    tab.appendChild(tbody);

    var heat = ts.filter(function (t) { return t.type === "heatmap"; })[0];
    if (heat) {
      var xs = arr(heat.x), ys = arr(heat.y), z = arr(heat.z);
      cab.appendChild(el("th", "", { scope: "col" }));
      xs.forEach(function (x) { cab.appendChild(el("th", rotulo(x), { scope: "col" })); });
      ys.slice(0, MAX_LINHAS).forEach(function (y, r) {
        var tr = el("tr");
        tr.appendChild(el("th", rotulo(y), { scope: "row" }));
        arr(z[r]).forEach(function (v) { tr.appendChild(el("td", num(v))); });
        tbody.appendChild(tr);
      });
      return tab;
    }
    var ind = ts.filter(function (t) { return t.type === "indicator"; });
    if (ind.length) {
      cab.appendChild(el("th", "Indicador", { scope: "col" }));
      cab.appendChild(el("th", "Valor", { scope: "col" }));
      cab.appendChild(el("th", "Meta", { scope: "col" }));
      ind.forEach(function (t, i) {
        var tr = el("tr");
        tr.appendChild(el("th", (t.title && t.title.text) || nomeTrace(t, i), { scope: "row" }));
        tr.appendChild(el("td", num(t.value, 0) + ((t.number && t.number.suffix) || "")));
        tr.appendChild(el("td", t.gauge && t.gauge.threshold && t.gauge.threshold.value ? num(t.gauge.threshold.value, 0) + ((t.number && t.number.suffix) || "") : "–"));
        tbody.appendChild(tr);
      });
      return tab;
    }
    var series = ts.filter(function (t) { return ["bar", "scatter", "scattergl", "funnel"].indexOf(t.type || "scatter") >= 0; });
    var xy = series.filter(function (t) { var a = arr(t.x), b = arr(t.y); return a.length && b.length && ehNumero(a[0]) && ehNumero(b[0]) && !horizontal(t); });
    if (xy.length && xy.length === series.length) {
      // dispersão: uma linha por ponto
      var ex = tituloEixo(gd, "xaxis") || "x", ey = tituloEixo(gd, "yaxis") || "y";
      ["Série", ex, ey].forEach(function (c) { cab.appendChild(el("th", c, { scope: "col" })); });
      var n = 0;
      xy.forEach(function (t, i) {
        var a = arr(t.x), b = arr(t.y);
        for (var k = 0; k < a.length && n < MAX_LINHAS; k++, n++) {
          var tr = el("tr");
          tr.appendChild(el("th", nomeTrace(t, i), { scope: "row" }));
          tr.appendChild(el("td", ex === "x" ? "" : num(a[k])));
          tr.appendChild(el("td", ey === "y" ? "" : num(b[k])));
          tbody.appendChild(tr);
        }
      });
      return tab;
    }
    if (!series.length) {
      cab.appendChild(el("th", "Observação", { scope: "col" }));
      var tr0 = el("tr");
      tr0.appendChild(el("td", "Este tipo de gráfico mostra distribuições; o resumo acima traz as medianas."));
      tbody.appendChild(tr0);
      return tab;
    }
    var ordem = [], linhas = {};
    series.forEach(function (t, i) {
      var pr = t.type === "funnel" ? pares({ x: t.x, y: t.y, orientation: "h" }) : pares(t);
      pr.cat.forEach(function (c, k) {
        var chave = rotulo(typeof c === "number" ? num(c) : c);
        if (!(chave in linhas)) { linhas[chave] = {}; ordem.push(chave); }
        linhas[chave][i] = t.type === "funnel" ? num(pr.val[k]) : fmtValor(gd, t, pr.val[k]);
      });
    });
    var categoriaNome = series.some(horizontal) ? "Categoria" : (gd.layout.xaxis && gd.layout.xaxis.title && gd.layout.xaxis.title.text) || "Categoria";
    cab.appendChild(el("th", categoriaNome, { scope: "col" }));
    series.forEach(function (t, i) { cab.appendChild(el("th", nomeTrace(t, i), { scope: "col" })); });
    ordem.slice(0, MAX_LINHAS).forEach(function (chave) {
      var tr = el("tr");
      tr.appendChild(el("th", chave, { scope: "row" }));
      series.forEach(function (t, i) { tr.appendChild(el("td", linhas[chave][i] !== undefined ? linhas[chave][i] : "–")); });
      tbody.appendChild(tr);
    });
    if (ordem.length > MAX_LINHAS) {
      var nota = el("tr");
      nota.appendChild(el("td", "Mostrando " + MAX_LINHAS + " de " + ordem.length + " linhas.", { colspan: String(series.length + 1) }));
      tbody.appendChild(nota);
    }
    return tab;
  }

  function descrever(gd) {
    var fig = gd.closest("figure.grafico-a11y");
    var texto = resumo(gd);
    var svgs = gd.querySelectorAll("svg.main-svg");
    svgs.forEach(function (s, i) {
      if (i === 0) { s.setAttribute("role", "img"); s.setAttribute("aria-label", texto); }
      else s.setAttribute("aria-hidden", "true");
    });
    if (!fig) return;
    var cap = fig.querySelector(".grafico-alt");
    if (cap) cap.textContent = texto;
    var caixa = fig.querySelector(".grafico-tabela");
    if (caixa) {
      caixa.innerHTML = "";
      try { caixa.appendChild(tabela(gd)); } catch (e) { caixa.textContent = "Tabela indisponível para este gráfico."; }
    }
  }

  // ------------------------------------------------------------------ alto contraste
  function ligado() {
    return document.body.classList.contains("alto-contraste");
  }
  function mapear(c) {
    if (Array.isArray(c)) return c.map(mapear);
    if (typeof c !== "string") return c;
    var k = c.toUpperCase();
    return CFG.mapa[k] || c;
  }
  function pegar(obj, caminho) {
    return caminho.split(".").reduce(function (o, p) { return o ? o[p] : undefined; }, obj);
  }
  var ATRIBUTOS = ["marker.color", "line.color", "marker.line.color", "fillcolor"];

  function aplicarContraste(gd) {
    if (!window.Plotly || !gd.data || gd._rtAcData === gd.data || gd._rtAcOcupado) return;
    // restyle pode disparar plotly_afterplot de forma síncrona: a trava evita aplicar duas vezes
    gd._rtAcOcupado = true;
    var originais = [];
    var pendentes = [];
    gd.data.forEach(function (t, i) {
      var orig = {}, upd = {};
      ATRIBUTOS.forEach(function (a) {
        var v = pegar(t, a);
        if (v === undefined) return;
        var novo = mapear(v);
        if (JSON.stringify(novo) !== JSON.stringify(v)) { orig[a] = v; upd[a] = [novo]; }
      });
      var tipo = t.type || "scatter";
      if (tipo === "bar" && i > 0 && !pegar(t, "marker.pattern.shape")) {
        orig["marker.pattern.shape"] = "";
        upd["marker.pattern.shape"] = [CFG.padroes[i % CFG.padroes.length]];
      }
      if (tipo === "scatter" && t.mode && t.mode.indexOf("lines") >= 0 && t.showlegend !== false && !pegar(t, "line.dash")) {
        orig["line.dash"] = "solid";
        upd["line.dash"] = [CFG.tracos[i % CFG.tracos.length]];
      }
      if (tipo === "scatter" && t.mode && t.mode.indexOf("markers") >= 0 && !pegar(t, "marker.symbol")) {
        orig["marker.symbol"] = "circle";
        upd["marker.symbol"] = [CFG.simbolos[i % CFG.simbolos.length]];
      }
      if (tipo === "heatmap" && CFG.escala) {
        orig.colorscale = t.colorscale;
        upd.colorscale = [CFG.escala];
      }
      originais.push(orig);
      if (Object.keys(upd).length) pendentes.push([upd, i]);
    });
    gd._rtAcOrig = originais;
    gd._rtAcData = gd.data;
    try {
      pendentes.forEach(function (p) { window.Plotly.restyle(gd, p[0], [p[1]]); });
      var anotacoes = {};
      ((gd.layout && gd.layout.annotations) || []).forEach(function (a, k) {
        var c = a.font && a.font.color;
        if (c && mapear(c) !== c) anotacoes["annotations[" + k + "].font.color"] = c;
      });
      var novas = {};
      Object.keys(anotacoes).forEach(function (k) { novas[k] = mapear(anotacoes[k]); });
      if (Object.keys(novas).length) window.Plotly.relayout(gd, novas);
      gd._rtAcAnot = anotacoes;
    } finally {
      gd._rtAcData = gd.data;
      gd._rtAcOcupado = false;
    }
  }

  function removerContraste(gd) {
    if (!window.Plotly || !gd._rtAcOrig || gd._rtAcData !== gd.data) { gd._rtAcData = null; return; }
    gd._rtAcOcupado = true;
    gd._rtAcOrig.forEach(function (orig, i) {
      var upd = {};
      Object.keys(orig).forEach(function (a) { upd[a] = [orig[a]]; });
      if (Object.keys(upd).length) window.Plotly.restyle(gd, upd, [i]);
    });
    if (gd._rtAcAnot && Object.keys(gd._rtAcAnot).length) window.Plotly.relayout(gd, gd._rtAcAnot);
    gd._rtAcAnot = null;
    gd._rtAcOrig = null;
    gd._rtAcData = null;
    gd._rtAcOcupado = false;
  }

  // ------------------------------------------------------------------ ligação aos gráficos
  function aoDesenhar(gd) {
    acompanharVariante(gd);
    if (ligado()) aplicarContraste(gd);
    // adia a descrição: o Plotly ainda está montando o SVG
    clearTimeout(gd._rtTimer);
    gd._rtTimer = setTimeout(function () { descrever(gd); }, 60);
  }

  function ligar() {
    document.querySelectorAll(".js-plotly-plot").forEach(function (gd) {
      if (gd._rtLigado || typeof gd.on !== "function") return;
      gd._rtLigado = true;
      gd.on("plotly_afterplot", function () { aoDesenhar(gd); });
      aoDesenhar(gd);
    });
    abasAcessiveis();
  }

  // ------------------------------------------------------------------ abas pelo teclado
  function abasAcessiveis() {
    document.querySelectorAll(".abas").forEach(function (lista) {
      var links = lista.querySelectorAll(".nav-link");
      lista.setAttribute("role", "tablist");
      links.forEach(function (a) {
        var ativo = a.classList.contains("active");
        a.setAttribute("role", "tab");
        a.setAttribute("aria-selected", ativo ? "true" : "false");
        a.setAttribute("tabindex", ativo ? "0" : "-1");
        if (a.parentElement) a.parentElement.setAttribute("role", "presentation");
      });
      if (lista._rtTeclas) return;
      lista._rtTeclas = true;
      lista.addEventListener("keydown", function (ev) {
        var atual = Array.prototype.indexOf.call(links = lista.querySelectorAll(".nav-link"), document.activeElement);
        if (atual < 0) return;
        var alvo = { ArrowRight: atual + 1, ArrowLeft: atual - 1, Home: 0, End: links.length - 1 }[ev.key];
        if (alvo === undefined) return;
        ev.preventDefault();
        alvo = (alvo + links.length) % links.length;
        links[alvo].focus();
        links[alvo].click();
      });
    });
  }

  // Esc fecha as dicas dos botões dos gráficos (WCAG 1.4.13: conteúdo em foco ou hover precisa poder ser dispensado).
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    document.querySelectorAll(".grafico-btn").forEach(function (b) {
      ["mouseout", "mouseleave"].forEach(function (tipo) { b.dispatchEvent(new MouseEvent(tipo, { bubbles: tipo === "mouseout" })); });
      if (document.activeElement === b) b.blur();
    });
  });

  // ------------------------------------------------------------------ Expandir gráfico (foco num só gráfico)
  var expandido = null; // { botao, caixa, gd, fundo, original }

  function caixaDo(botao) {
    return botao.closest(".cartao") || botao.closest(".slide") || botao.closest("figure");
  }

  function ajustarAltura(estado) {
    var gd = estado.gd, o = estado.original;
    if (!gd || !window.Plotly) return;
    var largura = gd.parentElement ? gd.parentElement.clientWidth : gd.offsetWidth;
    var topo = gd.getBoundingClientRect().top - estado.caixa.getBoundingClientRect().top;
    var disponivel = estado.caixa.clientHeight - topo - 110; // espaço do resumo em texto e do botão da tabela
    var proporcional = o.altura * (largura / Math.max(o.largura, 1));
    var altura = Math.round(Math.max(o.altura, Math.min(disponivel, proporcional)));
    var mudar = { height: altura, width: largura };
    window.Plotly.relayout(gd, mudar);
  }

  function expandir(botao) {
    if (expandido) recolher();
    var caixa = caixaDo(botao);
    var gd = grafoDe(botao.getAttribute("data-grafico"));
    if (!caixa) return;
    var fundo = document.createElement("div");
    fundo.className = "fundo-foco";
    fundo.addEventListener("click", recolher);
    document.body.appendChild(fundo);
    expandido = {
      botao: botao, caixa: caixa, gd: gd, fundo: fundo,
      original: gd ? {
        altura: gd.offsetHeight, largura: gd.offsetWidth,
        layoutAltura: gd.layout && gd.layout.height, layoutLargura: gd.layout && gd.layout.width,
      } : null,
    };
    caixa.classList.add("cartao-expandido");
    caixa.setAttribute("role", "dialog");
    caixa.setAttribute("aria-modal", "true");
    document.body.classList.add("grafico-em-foco");
    botao.setAttribute("aria-expanded", "true");
    botao.setAttribute("aria-label", "Recolher gráfico e voltar ao painel");
    if (gd) requestAnimationFrame(function () { ajustarAltura(expandido); });
    botao.focus();
  }

  function recolher() {
    if (!expandido) return;
    var e = expandido;
    expandido = null;
    e.caixa.classList.remove("cartao-expandido");
    e.caixa.removeAttribute("role");
    e.caixa.removeAttribute("aria-modal");
    document.body.classList.remove("grafico-em-foco");
    if (e.fundo.parentNode) e.fundo.parentNode.removeChild(e.fundo);
    e.botao.setAttribute("aria-expanded", "false");
    e.botao.setAttribute("aria-label", "Expandir gráfico para a largura total da tela");
    if (e.gd && window.Plotly) {
      var volta = { height: e.original.layoutAltura || e.original.altura };
      volta.width = e.original.layoutLargura || null;
      window.Plotly.relayout(e.gd, volta).then(function () { window.Plotly.Plots.resize(e.gd); });
    }
    e.botao.focus();
  }

  document.addEventListener("click", function (ev) {
    var botao = ev.target.closest && ev.target.closest(".grafico-expandir");
    if (!botao) return;
    ev.preventDefault();
    if (expandido && expandido.botao === botao) recolher(); else expandir(botao);
  });

  document.addEventListener("keydown", function (ev) {
    if (!expandido) return;
    if (ev.key === "Escape") { ev.preventDefault(); recolher(); return; }
    if (ev.key !== "Tab") return;
    // Mantém o foco dentro do gráfico expandido (WCAG 2.4.3).
    var focaveis = Array.prototype.filter.call(
      expandido.caixa.querySelectorAll("button, summary, a[href], input, select, [tabindex]:not([tabindex='-1'])"),
      function (el) { return el.offsetParent !== null; }
    );
    if (!focaveis.length) return;
    var primeiro = focaveis[0], ultimo = focaveis[focaveis.length - 1];
    if (ev.shiftKey && document.activeElement === primeiro) { ev.preventDefault(); ultimo.focus(); }
    else if (!ev.shiftKey && document.activeElement === ultimo) { ev.preventDefault(); primeiro.focus(); }
  });

  window.addEventListener("resize", function () { if (expandido && expandido.gd) ajustarAltura(expandido); });

  // ------------------------------------------------------------------ Visualizações alternativas (⇄ e índice 2/4)
  // Cada gráfico guarda a figura original enviada pelo servidor e gera, no navegador, outras formas de mostrar os
  // mesmos valores (linhas ↔ barras ↔ área, histograma ↔ caixa ↔ violino, mapa de calor ↔ bolhas...).
  // Quando o servidor manda uma figura nova (filtro, mês), o gráfico volta à visualização 1.
  function grafoDe(id) {
    var el = document.getElementById(id);
    return el && (el.classList.contains("js-plotly-plot") ? el : el.querySelector(".js-plotly-plot"));
  }
  function idDe(gd) {
    var el = gd.closest(".dash-graph") || gd.parentElement;
    return el && el.id;
  }
  function clonar(v) {
    if (v === null || typeof v !== "object") return v;
    if (ArrayBuffer.isView(v)) return v.slice();
    if (Array.isArray(v)) return v.map(clonar);
    if (v instanceof Date) return new Date(v.getTime());
    var o = {};
    Object.keys(v).forEach(function (k) { if (k.charAt(0) !== "_") o[k] = clonar(v[k]); });
    return o;
  }
  function lista(v) { return v == null ? [] : Array.prototype.slice.call(v); }
  function numeros(l) { return l.length > 0 && l.every(function (v) { return typeof v === "number"; }); }
  function corUnica(c, reserva) { return typeof c === "string" ? c : (Array.isArray(c) && typeof c[0] === "string" ? c[0] : reserva); }
  var CORES = ["#038C8C", "#C2AA61", "#8C3603", "#014040", "#61C2AA", "#5A6B7B", "#B5651D", "#4D4D4D"];
  var COMUNS = ["name", "xaxis", "yaxis", "customdata", "legendgroup", "showlegend", "uid"];

  function pegarComuns(t) {
    var o = {};
    COMUNS.forEach(function (k) { if (t[k] !== undefined) o[k] = clonar(t[k]); });
    return o;
  }
  function ehReferencia(v) {
    return (v.dash && v.dash !== "solid") || /\b(meta|m[eé]dia|p90|lsc|lic|limite)\b/i.test(v.nome || "");
  }
  function resumoTraco(t, i) {
    var cor = corUnica(t.marker && t.marker.color, corUnica(t.line && t.line.color, CORES[i % CORES.length]));
    return {
      x: lista(t.x), y: lista(t.y), z: t.z ? lista(t.z).map(lista) : null, tipo: t.type, orient: t.orientation,
      modo: t.mode || "", base: t.base, fill: t.fill, stack: t.stackgroup, nome: t.name,
      dash: t.line && t.line.dash, cor: cor, escala: t.colorscale, visivel: t.visible !== false,
    };
  }

  function layoutDe(e, op) {
    var l = clonar(e.layout);
    op = op || {};
    if (op.semMarcas) { l.shapes = []; l.annotations = []; }
    if (op.trocarEixos) {
      var x = l.xaxis || {}, y = l.yaxis || {};
      l.xaxis = y; l.yaxis = x;
      [l.xaxis, l.yaxis].forEach(function (a) {
        if (a.autorange === "reversed") a.autorange = true;
        delete a.domain; delete a.anchor;
      });
    }
    if (op.semEixos) {
      l.xaxis = { visible: false }; l.yaxis = { visible: false };
      l.shapes = []; l.annotations = [];
    }
    if (op.eixoY) l.yaxis = Object.assign({ automargin: true }, op.eixoY);
    if (op.barmode) l.barmode = op.barmode;
    if (op.zeroY) {
      // barras e áreas precisam partir do zero para o tamanho ser comparável
      l.yaxis = Object.assign({}, l.yaxis, { rangemode: "tozero", autorange: true });
      delete l.yaxis.range;
    }
    if (op.legenda) l.showlegend = true;
    return l;
  }

  // Monta uma figura trocando só os traços principais; os de referência (meta, média...) seguem iguais.
  function porTraco(e, fazer, manterReferencias) {
    var dados = [];
    e.data.forEach(function (t, i) {
      var v = e.valores[i];
      if (!v) return;
      if (v.decor) return;
      if (ehReferencia(v)) { if (manterReferencias !== false) dados.push(clonar(t)); return; }
      var novo = fazer(t, v, i);
      if (novo) dados.push(novo);
    });
    return dados;
  }

  function nomeSerie(e, p) {
    var barras = p.every(function (v) { return v.tipo === "bar"; });
    if (barras) return p.length > 1 && e.layout.barmode === "stack" ? "Barras empilhadas" : "Barras";
    if (p.some(function (v) { return (v.fill && v.fill !== "none") || v.stack; })) return "Área";
    return p.every(function (v) { return v.modo.indexOf("lines") < 0; }) ? "Pontos" : "Linhas";
  }

  function familiaSerie(e, p) {
    var multi = p.length > 1;
    var positivos = p.every(function (v) { return v.y.every(function (y) { return y == null || y >= 0; }); });
    var soBarras = p.every(function (v) { return v.tipo === "bar"; });
    var empilhado = soBarras && multi && e.layout.barmode === "stack";
    var linha = function (t, v, i, extra) {
      var o = pegarComuns(t);
      o.type = "scatter"; o.x = v.x; o.y = v.y; o.mode = "lines+markers";
      o.line = { color: v.cor, width: 2.5 }; o.marker = { color: v.cor, size: 6 };
      return Object.assign(o, extra || {});
    };
    var barra = function (t, v) {
      var o = pegarComuns(t);
      o.type = "bar"; o.x = v.x; o.y = v.y;
      o.marker = { color: (t.marker && t.marker.color) || v.cor };
      return o;
    };
    var opcoes = {
      "Linhas": function () { return { data: porTraco(e, function (t, v, i) { return linha(t, v, i); }), layout: layoutDe(e) }; },
      "Barras": function () { return { data: porTraco(e, barra), layout: layoutDe(e, { barmode: "group", zeroY: true }) }; },
      "Barras empilhadas": function () { return { data: porTraco(e, barra), layout: layoutDe(e, { barmode: "stack", zeroY: true }) }; },
      "Área": function () {
        return { data: porTraco(e, function (t, v, i) {
          return linha(t, v, i, empilhado ? { mode: "lines", stackgroup: "a" } : { mode: "lines", fill: "tozeroy" });
        }), layout: layoutDe(e, { zeroY: true }) };
      },
      "Pontos": function () {
        return { data: porTraco(e, function (t, v, i) { return linha(t, v, i, { mode: "markers", marker: { color: v.cor, size: multi ? 7 : 10 } }); }), layout: layoutDe(e) };
      },
      // Catálogo T5: degraus mostram valores que mudam em saltos (mês a mês).
      "Degraus": function () {
        return { data: porTraco(e, function (t, v, i) { return linha(t, v, i, { line: { color: v.cor, width: 2.5, shape: "hv" } }); }), layout: layoutDe(e) };
      },
    };
    // Séries de tamanhos diferentes (ex.: pontos fora de controle por cima da linha) só trocam linha ↔ pontos.
    var iguais = p.every(function (v) { return v.x.length === p[0].x.length; });
    var nomes = ["Linhas"];
    if (iguais) nomes.push("Barras");
    if (iguais && multi && positivos && soBarras) nomes.push("Barras empilhadas");
    if (iguais) nomes.push("Área");
    nomes.push("Pontos");
    nomes.push("Degraus");
    return montarLista(nomeSerie(e, p), nomes, opcoes);
  }

  function familiaCategoriaH(e, p) {
    // Traços com categorias diferentes (ex.: destaque de cor) são uma série só, pintada em partes.
    var vistas = {}, compartilham = false;
    p.forEach(function (v) {
      var proprias = {};
      v.y.forEach(function (c) { proprias[c] = true; });
      Object.keys(proprias).forEach(function (c) { if (vistas[c]) compartilham = true; vistas[c] = true; });
    });
    var multi = p.length > 1 && compartilham;
    var modoUnico = p.length > 1 ? "overlay" : "group";
    var soBarras = p.every(function (v) { return v.tipo === "bar"; });
    var barrasH = function (t, v) {
      var o = pegarComuns(t);
      o.type = "bar"; o.orientation = "h"; o.x = v.x; o.y = v.y;
      o.marker = { color: (t.marker && t.marker.color) || v.cor };
      o.text = t.text; o.textposition = "outside";
      return o;
    };
    var opcoes = {
      "Barras": function () { return { data: porTraco(e, barrasH), layout: layoutDe(e, { barmode: modoUnico }) }; },
      "Barras agrupadas": function () { return { data: porTraco(e, barrasH), layout: layoutDe(e, { barmode: "group" }) }; },
      "Barras empilhadas": function () { return { data: porTraco(e, barrasH), layout: layoutDe(e, { barmode: "stack" }) }; },
      "Pontos": function () {
        return { data: porTraco(e, function (t, v) {
          var o = pegarComuns(t);
          o.type = "scatter"; o.mode = "markers"; o.x = v.x; o.y = v.y;
          o.marker = { color: (t.marker && t.marker.color) || v.cor, size: 11 };
          return o;
        }), layout: layoutDe(e) };
      },
      // Catálogo M9: pirulito = haste fina + ponto; menos tinta que a barra para muitas categorias.
      "Pirulito": function () {
        return { data: porTraco(e, function (t, v) {
          var o = pegarComuns(t);
          o.type = "scatter"; o.mode = "markers"; o.x = v.x; o.y = v.y;
          o.marker = { color: (t.marker && typeof t.marker.color === "string" && t.marker.color) || v.cor, size: 11 };
          o.error_x = { type: "data", symmetric: false, array: [], arrayminus: v.x.map(function (x) { return typeof x === "number" ? Math.max(x, 0) : 0; }), thickness: 2, width: 0, color: v.cor };
          return o;
        }), layout: layoutDe(e) };
      },
      "Colunas": function () {
        return { data: porTraco(e, function (t, v) {
          var o = pegarComuns(t);
          o.type = "bar"; o.x = v.y; o.y = v.x;
          o.marker = { color: (t.marker && t.marker.color) || v.cor };
          delete o.xaxis; delete o.yaxis;
          return o;
        }, false), layout: layoutDe(e, { trocarEixos: true, semMarcas: true, barmode: !multi ? modoUnico : (e.layout.barmode === "stack" ? "stack" : "group") }) };
      },
    };
    var nomes = multi ? ["Barras agrupadas"].concat(soBarras ? ["Barras empilhadas"] : [], ["Pontos", "Colunas"]) : ["Barras", "Pirulito", "Pontos", "Colunas"];
    var atual = soBarras
      ? (multi ? (e.layout.barmode === "stack" ? "Barras empilhadas" : "Barras agrupadas") : "Barras")
      : "Pontos";
    return montarLista(atual, nomes, opcoes);
  }

  function familiaHistograma(e, p) {
    var valores = function (v) { return v.x.length ? v.x : v.y; };
    var distrib = function (tipo, extra) {
      return function () {
        return { data: porTraco(e, function (t, v) {
          var o = pegarComuns(t);
          o.type = tipo; o.x = valores(v); o.orientation = "h"; o.name = v.nome || " ";
          o.marker = { color: v.cor }; o.line = { color: v.cor };
          return Object.assign(o, extra);
        }, false), layout: layoutDe(e, { eixoY: { title: { text: "" }, showticklabels: p.length > 1 } }) };
      };
    };
    var opcoes = {
      "Caixa": distrib("box", { boxpoints: "outliers", boxmean: true }),
      "Violino": distrib("violin", { box: { visible: true }, meanline: { visible: true }, points: false }),
      "Acumulada": function () {
        return { data: porTraco(e, function (t) {
          var o = clonar(t);
          o.cumulative = { enabled: true }; o.histnorm = "percent";
          return o;
        }, false), layout: layoutDe(e, { eixoY: { title: { text: "% acumulado" }, ticksuffix: "%" } }) };
      },
    };
    return montarLista("Histograma", ["Caixa", "Violino", "Acumulada"], opcoes);
  }

  function familiaCaixa(e, p) {
    var conv = function (tipo, extra) {
      return function () {
        return { data: porTraco(e, function (t, v) {
          var o = pegarComuns(t);
          o.type = tipo; o.x = v.x.length ? v.x : undefined; o.y = v.y.length ? v.y : undefined;
          if (t.orientation) o.orientation = t.orientation;
          o.marker = { color: v.cor }; o.line = { color: v.cor };
          o.hovertemplate = t.hovertemplate;
          return Object.assign(o, extra);
        }), layout: layoutDe(e) };
      };
    };
    var opcoes = {
      "Caixa": conv("box", { boxpoints: "outliers" }),
      "Violino": conv("violin", { box: { visible: true }, meanline: { visible: true }, points: false }),
      "Pontos": conv("box", { boxpoints: "all", jitter: 0.6, pointpos: 0, fillcolor: "rgba(0,0,0,0)", line: { width: 0 }, marker: { size: 5, opacity: 0.6 } }),
      // Catálogo D4 + D6: caixa com cada observação ao lado (jitter).
      "Caixa com pontos": conv("box", { boxpoints: "all", jitter: 0.5, pointpos: -1.6, marker: { size: 4, opacity: 0.55 } }),
    };
    var atual = p[0].tipo === "violin" ? "Violino" : "Caixa";
    return montarLista(atual, ["Caixa", "Violino", "Caixa com pontos", "Pontos"], opcoes);
  }

  // Pontos que são observações individuais por grupo (dot strip): alternativas são caixa e violino.
  function familiaDistribuicao(e, p) {
    var conv = function (tipo, extra) {
      return function () {
        return { data: porTraco(e, function (t, v) {
          var o = pegarComuns(t);
          o.type = tipo; o.x = v.x; o.orientation = "h"; o.name = v.nome || " ";
          o.marker = { color: v.cor }; o.line = { color: v.cor }; o.showlegend = false;
          return Object.assign(o, extra);
        }, false), layout: layoutDe(e, { semMarcas: true, eixoY: { title: { text: "" } } }) };
      };
    };
    return montarLista("Pontos", ["Caixa", "Violino", "Caixa com pontos"], {
      "Caixa com pontos": conv("box", { boxpoints: "all", jitter: 0.5, pointpos: -1.6, marker: { size: 4, opacity: 0.55 } }),
      "Caixa": conv("box", { boxpoints: "outliers", boxmean: true }),
      "Violino": conv("violin", { box: { visible: true }, meanline: { visible: true }, points: false }),
    });
  }
  var DISTRIBUICAO = ["g-nv-dotstrip"];

  function familiaCalor(e, p) {
    var v = p[0];
    var opcoes = {
      "Bolhas": function () {
        var xs = [], ys = [], zs = [], max = 0;
        var colunas = Math.max(1, (v.z[0] || []).length), linhas = Math.max(1, v.z.length);
        var maior = Math.max(8, Math.min(30, 520 / Math.max(colunas, linhas * 1.5)));
        v.z.forEach(function (linha, i) {
          linha.forEach(function (z, j) {
            if (z == null || isNaN(z)) return;
            xs.push(v.x.length ? v.x[j] : j); ys.push(v.y.length ? v.y[i] : i); zs.push(z);
            max = Math.max(max, Math.abs(z));
          });
        });
        return { data: [{
          type: "scatter", mode: "markers", x: xs, y: ys, text: zs, hovertemplate: "%{x} · %{y}: %{text}<extra></extra>",
          marker: { size: zs.map(function (z) { return 3 + maior * Math.sqrt(Math.abs(z) / (max || 1)); }), color: zs,
            colorscale: v.escala, showscale: true, line: { width: 0.5, color: "#2B2B2B" } },
        }], layout: layoutDe(e) };
      },
      "Linhas": function () {
        return { data: v.z.map(function (linha, i) {
          return { type: "scatter", mode: "lines+markers", x: v.x.length ? v.x : linha.map(function (_, j) { return j; }),
            y: linha, name: String(v.y.length ? v.y[i] : i), line: { color: CORES[i % CORES.length], width: 2 } };
        }), layout: layoutDe(e, { semMarcas: true, eixoY: { title: { text: "valor" } }, legenda: true }) };
      },
    };
    return montarLista("Mapa de calor", ["Bolhas", "Linhas"], opcoes);
  }

  function familiaDispersao(e, p) {
    var escala = [[0, "#F3F8F8"], [0.4, "#61C2AA"], [1, "#014040"]];
    var densidade = function (tipo, extra) {
      return function () {
        var grupos = {};
        p.forEach(function (v, i) {
          var t = e.data[e.valores.indexOf(v)] || {};
          var chave = (t.xaxis || "x") + "|" + (t.yaxis || "y");
          var g = grupos[chave] = grupos[chave] || { x: [], y: [], xaxis: t.xaxis, yaxis: t.yaxis };
          g.x = g.x.concat(v.x); g.y = g.y.concat(v.y);
        });
        var dados = Object.keys(grupos).map(function (k, i) {
          var g = grupos[k];
          var o = { type: tipo, x: g.x, y: g.y, colorscale: escala, showscale: i === 0, name: "Densidade" };
          if (g.xaxis) o.xaxis = g.xaxis;
          if (g.yaxis) o.yaxis = g.yaxis;
          return Object.assign(o, extra);
        });
        return { data: dados, layout: layoutDe(e) };
      };
    };
    var opcoes = {
      "Densidade": densidade("histogram2d", { nbinsx: 20, nbinsy: 20 }),
      "Contornos": densidade("histogram2dcontour", { ncontours: 12, contours: { coloring: "heatmap" }, line: { width: 0.5 } }),
    };
    return montarLista("Dispersão", ["Densidade", "Contornos"], opcoes);
  }

  function montarLista(atual, nomes, opcoes) {
    var l = [{ nome: atual, original: true }];
    nomes.forEach(function (n) { if (n !== atual && opcoes[n]) l.push({ nome: n, montar: opcoes[n] }); });
    return l;
  }

  function classificar(e) {
    // Traços de 1–2 pontos ao lado de traços maiores são enfeites (conectores, rótulos de mediana).
    var maior = Math.max.apply(null, e.valores.map(function (v) { return Math.max(v.x.length, v.y.length); }).concat([0]));
    e.valores.forEach(function (v) { v.decor = v.tipo === "scatter" && Math.max(v.x.length, v.y.length) <= 2 && maior > 2; });
    var p = e.valores.filter(function (v) { return v.visivel && !v.decor && !ehReferencia(v); });
    if (!p.length) return [];
    var tipos = {};
    p.forEach(function (v) { tipos[v.tipo] = true; });
    var t = Object.keys(tipos);
    var so = function () {
      var aceitos = Array.prototype.slice.call(arguments);
      return t.every(function (k) { return aceitos.indexOf(k) >= 0; });
    };
    if (so("histogram")) return familiaHistograma(e, p);
    if (so("box", "violin")) return familiaCaixa(e, p);
    if (so("heatmap") && p.length === 1 && p[0].z) return familiaCalor(e, p);
    if (!so("bar", "scatter")) return [];
    if (p.some(function (v) { return v.base != null && lista(v.base).length; })) return [];
    var soPontos = p.every(function (v) { return v.tipo === "scatter" && v.modo.indexOf("lines") < 0 && numeros(v.x); });
    var repetem = p.every(function (v) { return !numeros(v.y) && new Set(v.y).size < v.y.length; });
    if (soPontos && (repetem || DISTRIBUICAO.indexOf(e.id) >= 0)) return familiaDistribuicao(e, p);
    var horizontal = p.every(function (v) {
      return v.tipo === "bar" ? v.orient === "h" : (numeros(v.x) && !numeros(v.y) && v.y.length > 0);
    });
    if (horizontal) return familiaCategoriaH(e, p);
    var dispersao = p.every(function (v) { return v.tipo === "scatter" && v.modo.indexOf("lines") < 0 && numeros(v.x) && numeros(v.y); });
    if (dispersao) return familiaDispersao(e, p);
    var xs = p[0].x;
    if (p.every(function (v) { return v.orient !== "h"; }) && (!numeros(xs) || xs.length <= 24)) return familiaSerie(e, p);
    return [];
  }

  function guardarOriginal(gd) {
    var fig = gd.closest("figure");
    var permitido = !fig || fig.getAttribute("data-alternativas") !== "0";
    var e = {
      data: clonar(gd.data || []), layout: clonar(gd.layout || {}),
      valores: (gd._fullData || []).map(resumoTraco), indice: 0, id: idDe(gd),
    };
    var meta = (e.layout && typeof e.layout.meta === "object" && e.layout.meta) || {};
    try { e.lista = permitido && meta.rt_auto !== false ? classificar(e) : []; } catch (err) { e.lista = []; }
    // Alternativas montadas no servidor (viz/alternativas.py) entram depois das automáticas.
    var extras = permitido && Array.isArray(meta.rt_alternativas) ? meta.rt_alternativas : [];
    if (extras.length) {
      if (!e.lista.length) e.lista = [{ nome: meta.rt_nome || "Original", original: true }];
      else if (meta.rt_nome) e.lista[0].nome = meta.rt_nome;
      var usados = {};
      e.lista.forEach(function (x) { usados[x.nome] = true; });
      extras.forEach(function (a) {
        if (usados[a.nome]) return;
        usados[a.nome] = true;
        e.lista.push({ nome: a.nome, montar: function () {
          var l = clonar(a.layout || {});
          if (e.layout.template) l.template = clonar(e.layout.template);
          return { data: clonar(a.data || []), layout: l };
        } });
      });
    }
    e.dados = gd.data;
    gd._rtVar = e;
    atualizarContador(gd);
  }

  function atualizarContador(gd) {
    var id = idDe(gd), e = gd._rtVar;
    if (!id || !e) return;
    var total = Math.max(e.lista.length, 1), atual = e.indice + 1;
    var nome = e.lista.length ? e.lista[e.indice].nome : "Única visualização";
    var cont = document.getElementById(id + "-variante");
    if (cont) {
      cont.textContent = atual + "/" + total;
      cont.title = nome + " (visualização " + atual + " de " + total + ")";
      cont.setAttribute("aria-label", "Visualização " + atual + " de " + total + ": " + nome);
    }
    var botao = document.getElementById(id + "-alternar");
    if (botao) {
      botao.disabled = total < 2;
      if (total > 1) {
        var prox = e.lista[(e.indice + 1) % total].nome;
        botao.setAttribute("aria-label", "Alternar visualização. Próxima: " + prox + " (" + ((e.indice + 1) % total + 1) + " de " + total + ")");
      }
    }
  }

  function mostrarVariante(gd, k) {
    var e = gd._rtVar;
    if (!e || e.lista.length < 2 || !window.Plotly) return;
    e.indice = (k + e.lista.length) % e.lista.length;
    var item = e.lista[e.indice];
    var fig;
    try {
      fig = item.original ? { data: clonar(e.data), layout: clonar(e.layout) } : item.montar();
    } catch (err) {
      fig = { data: clonar(e.data), layout: clonar(e.layout) };
      e.indice = 0;
    }
    if (gd.layout && gd.layout.height) fig.layout.height = gd.layout.height;
    if (gd.layout && gd.layout.width) fig.layout.width = gd.layout.width;
    fig.layout.datarevision = Date.now();
    gd._rtTrocando = true;
    window.Plotly.react(gd, fig.data, fig.layout).then(
      function () { gd._rtTrocando = false; e.dados = gd.data; atualizarContador(gd); },
      function () { gd._rtTrocando = false; }
    );
    atualizarContador(gd);
  }

  // Chamado a cada desenho: figura nova do servidor → guarda como original; desenho nosso → só registra.
  function acompanharVariante(gd) {
    if (gd._rtTrocando) { if (gd._rtVar) gd._rtVar.dados = gd.data; return; }
    if (!gd._rtVar || gd._rtVar.dados !== gd.data) guardarOriginal(gd);
  }

  document.addEventListener("click", function (ev) {
    var botao = ev.target.closest && ev.target.closest(".grafico-alternar");
    if (!botao || botao.disabled) return;
    var gd = grafoDe(botao.getAttribute("data-grafico"));
    if (gd && gd._rtVar) mostrarVariante(gd, gd._rtVar.indice + 1);
  });

  setInterval(ligar, 700);
  document.addEventListener("DOMContentLoaded", ligar);

  // ------------------------------------------------------------------ API para o callback do interruptor
  window.dash_clientside = window.dash_clientside || {};
  window.dash_clientside.rtA11y = {
    alternarContraste: function (valor) {
      document.body.classList.toggle("alto-contraste", !!valor);
      document.querySelectorAll(".js-plotly-plot").forEach(function (gd) {
        if (valor) aplicarContraste(gd); else removerContraste(gd);
      });
      return !!valor;
    },
  };
  window.rtA11y = { descrever: descrever, resumo: resumo };
})();
