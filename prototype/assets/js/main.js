/* Минимум JS: меню на телефоне, выбор канала записи на месте, «Скопировать», закреплённая кнопка.
   Без JS всё работает: меню открыто списком, «Записаться» ведёт к блоку «Запись». */
(function () {
  "use strict";

  // меню на телефоне
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      toggle.setAttribute("aria-label", open ? "Открыть меню" : "Закрыть меню");
      nav.classList.toggle("is-open", !open);
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a") && nav.classList.contains("is-open")) {
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Открыть меню");
        nav.classList.remove("is-open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        toggle.click();
        toggle.focus();
      }
    });
  }

  // Высота первого экрана учитывает фактическую высоту шапки.
  var homeHero = document.querySelector(".hero");
  var header = document.querySelector(".site-header");
  if (homeHero && header) {
    var measureHeader = function () {
      homeHero.style.setProperty("--site-header-height", header.getBoundingClientRect().height + "px");
    };
    measureHeader();
    if ("ResizeObserver" in window) new ResizeObserver(measureHeader).observe(header);
  }

  // Обложка видео-знакомства становится интерактивной после загрузки скрипта.
  var videoButton = document.querySelector(".video-play");
  var introVideo = document.querySelector(".video-frame");
  if (videoButton && introVideo) {
    var videoStage = videoButton.parentElement;
    introVideo.hidden = true;
    videoButton.hidden = false;
    videoStage.classList.add("is-preview");
    videoButton.addEventListener("click", function () {
      introVideo.hidden = false;
      introVideo.play().catch(function () {
        // При отказе браузера запустить ролик доступны его штатные controls.
      });
      introVideo.focus();
      videoButton.hidden = true;
      videoStage.classList.remove("is-preview");
    });
  }

  // Полноразмерные документы открываются поверх страницы.
  var docViewer = document.getElementById("doc-viewer");
  if (docViewer && typeof docViewer.showModal === "function") {
    var docImage = docViewer.querySelector("img");
    document.querySelectorAll(".doc__link").forEach(function (link) {
      link.addEventListener("click", function (event) {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        docImage.alt = link.textContent.trim();
        docImage.src = link.href;
        docViewer.showModal();
      });
    });
  }

  // «Записаться» раскрывает выбор Telegram / ВКонтакте на месте, без всплывающих окон
  document.querySelectorAll("[data-choose]").forEach(function (btn) {
    var panel = document.getElementById(btn.getAttribute("data-choose"));
    if (!panel) return;
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-controls", panel.id);
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var open = panel.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", String(open));
      if (open) {
        var first = panel.querySelector("a");
        if (first) first.focus();
      }
    });
  });

  // «Скопировать» пример первого сообщения
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    var src = document.getElementById(btn.getAttribute("data-copy"));
    var status = btn.parentNode.querySelector(".copy-status");
    btn.addEventListener("click", function () {
      var text = src ? src.innerText.trim() : "";
      var done = function () { if (status) { status.textContent = "Скопировано"; setTimeout(function () { status.textContent = ""; }, 2500); } };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
      } else { fallback(text); done(); }
    });
  });
  function fallback(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "absolute"; ta.style.left = "-9999px";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) { /* ничего */ }
    document.body.removeChild(ta);
  }

  // закреплённая кнопка записи: после первого экрана, прячется у блока «Запись» и в подвале
  var sticky = document.querySelector(".sticky-cta");
  var hero = document.querySelector(".hero, .page-head");
  if (sticky && hero && "IntersectionObserver" in window) {
    var heroVisible = true, endVisible = false;
    var update = function () { sticky.classList.toggle("is-visible", !heroVisible && !endVisible); };
    new IntersectionObserver(function (es) { heroVisible = es[0].isIntersecting; update(); }).observe(hero);
    var ends = document.querySelectorAll("#contact, .site-footer");
    var seen = new Map();
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { seen.set(e.target, e.isIntersecting); });
      endVisible = Array.from(seen.values()).some(Boolean);
      update();
    });
    ends.forEach(function (el) { io.observe(el); });
  }
})();
