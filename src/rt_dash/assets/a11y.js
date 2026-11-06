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
