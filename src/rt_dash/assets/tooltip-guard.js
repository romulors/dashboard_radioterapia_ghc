/*
 * Guarda dos tooltips (dbc.Tooltip / Popper).
 *
 * Problema: às vezes um tooltip fica "preso" no canto superior esquerdo da página. Isso acontece quando o
 * Popper perde o elemento de referência (botão escondido, desmontado ou sem tamanho) enquanto o tooltip
 * ainda está aberto: a posição calculada vira (0, 0) e o React não recebe o mouseleave/blur que o fecharia.
 *
 * Correção: enquanto houver tooltip na página, verifica a cada 300 ms (e em scroll, resize, clique, tecla
 * e troca de aba do navegador) se ele ainda tem motivo para estar aberto. Se não tiver, esconde.
 * Um tooltip é legítimo quando o seu botão de origem existe, está visível e está com o mouse em cima
 * ou com o foco do teclado. Para tooltips sem ligação explícita (aria-describedby), usa os sinais do
 * próprio Popper: referência escondida ou posição na origem (0, 0).
 */
(function () {
  "use strict";
  var CLASSE = "tooltip-orfao";
  var timer = null;

  var estilo = document.createElement("style");
  estilo.textContent = "." + CLASSE + " { display: none !important; }";
  document.head.appendChild(estilo);

  function gatilhoDe(tip) {
    if (!tip.id) return null;
    try {
      return document.querySelector('[aria-describedby~="' + CSS.escape(tip.id) + '"]');
    } catch (e) {
      return null;
    }
  }

  function visivel(el) {
    if (!el || !el.isConnected) return false;
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  function ativo(el) {
    return el === document.activeElement || el.matches(":hover") || !!el.querySelector(":hover");
  }

  function naOrigem(tip) {
    var m = /translate(?:3d)?\(\s*(-?[\d.]+)px,\s*(-?[\d.]+)px/.exec(tip.style.transform || "");
    if (!m) return false;
    return Math.abs(parseFloat(m[1])) < 2 && Math.abs(parseFloat(m[2])) < 24;
  }

  function orfao(tip) {
    var alvo = gatilhoDe(tip);
    if (alvo) return !visivel(alvo) || !ativo(alvo);
    return tip.getAttribute("data-popper-reference-hidden") === "true" || naOrigem(tip);
  }

  function verificar() {
    var tips = document.querySelectorAll(".tooltip");
    for (var i = 0; i < tips.length; i++) {
      var tip = tips[i];
      if (orfao(tip)) tip.classList.add(CLASSE);
      else tip.classList.remove(CLASSE);
    }
    if (tips.length && !timer) timer = setInterval(verificar, 300);
    if (!tips.length && timer) { clearInterval(timer); timer = null; }
  }

  // Tooltip novo na página: verifica logo depois de o Popper posicionar.
  new MutationObserver(function (mudancas) {
    for (var i = 0; i < mudancas.length; i++) {
      var nos = mudancas[i].addedNodes;
      for (var j = 0; j < nos.length; j++) {
        if (nos[j].nodeType === 1 && nos[j].classList.contains("tooltip")) {
          setTimeout(verificar, 50);
          return;
        }
      }
    }
  }).observe(document.body, { childList: true });

  ["scroll", "resize", "click", "keyup", "focusin", "visibilitychange", "blur"].forEach(function (ev) {
    window.addEventListener(ev, function () { setTimeout(verificar, 0); }, true);
  });
})();
