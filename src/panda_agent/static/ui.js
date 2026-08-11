/* Local-only UI helpers. The API requests are owned by HTMX markup. */
(function () {
  "use strict";

  function announce(message) {
    var live = document.getElementById("ui-live-status");
    if (live) live.textContent = message || "";
  }

  function fillQuestion(event) {
    var button = event.currentTarget;
    var field = document.getElementById("question");
    if (!field) return;
    field.value = button.getAttribute("data-fill-question") || "";
    field.focus();
    field.setSelectionRange(field.value.length, field.value.length);
  }

  function actionStatus(result, message) {
    var status = result && result.querySelector("[data-action-status]");
    if (status) status.textContent = message || "";
    announce(message);
  }

  function copyText(text, done) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      navigator.clipboard.writeText(text).then(function () {
        done(true);
      }).catch(function () {
        done(false);
      });
      return;
    }
    var helper = document.createElement("textarea");
    helper.value = text;
    helper.setAttribute("readonly", "readonly");
    helper.style.position = "fixed";
    helper.style.opacity = "0";
    document.body.appendChild(helper);
    helper.select();
    var copied = false;
    try {
      copied = document.execCommand("copy");
    } catch (_error) {
      copied = false;
    }
    document.body.removeChild(helper);
    done(copied);
  }

  function copyAnswer(event) {
    var result = event.currentTarget.closest(".result-card");
    var answer = result && result.querySelector(".answer");
    if (!answer) return;
    copyText(answer.textContent || "", function (copied) {
      actionStatus(result, copied ? "Answer copied." : "Copy failed; select the answer text manually.");
    });
  }

  function resultPayload(result) {
    if (!result) return null;
    var raw = result.getAttribute("data-result-json");
    if (raw === null) {
      var node = result.querySelector("[data-result-json]");
      raw = node && node.textContent;
    }
    if (raw === null || raw === undefined) return null;
    try {
      return JSON.parse(raw || "{}");
    } catch (_error) {
      return null;
    }
  }

  function downloadJson(event) {
    var result = event.currentTarget.closest(".result-card");
    var payload = resultPayload(result);
    if (!payload) {
      actionStatus(result, "The result JSON is unavailable.");
      return;
    }
    var requestId = String(payload.request_id || "request").replace(/[^A-Za-z0-9_-]+/g, "-");
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "panda-qa-" + (requestId || "request") + ".json";
    link.click();
    URL.revokeObjectURL(url);
    actionStatus(result, "JSON download started.");
  }

  function activateTab(button, tabs) {
    var target = button.getAttribute("data-tab-target");
    tabs.querySelectorAll("[role=tab]").forEach(function (tab) {
      var active = tab === button;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.setAttribute("tabindex", active ? "0" : "-1");
    });
    tabs.querySelectorAll("[data-tab-panel]").forEach(function (panel) {
      var active = panel.getAttribute("data-tab-panel") === target;
      panel.hidden = !active;
      panel.classList.toggle("is-active", active);
    });
    button.focus();
  }

  function bindTabs(root) {
    (root || document).querySelectorAll("[data-tabs]").forEach(function (tabs) {
      if (tabs.getAttribute("data-tabs-bound") === "true") return;
      tabs.setAttribute("data-tabs-bound", "true");
      var buttons = Array.prototype.slice.call(tabs.querySelectorAll("[role=tab]"));
      buttons.forEach(function (button, index) {
        button.addEventListener("click", function () { activateTab(button, tabs); });
        button.addEventListener("keydown", function (event) {
          if (["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"].indexOf(event.key) < 0) return;
          event.preventDefault();
          var next = index;
          if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % buttons.length;
          if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + buttons.length) % buttons.length;
          if (event.key === "Home") next = 0;
          if (event.key === "End") next = buttons.length - 1;
          activateTab(buttons[next], tabs);
        });
      });
    });
  }

  function bindResultActions(root) {
    (root || document).querySelectorAll("[data-copy-answer]").forEach(function (button) {
      if (button.getAttribute("data-bound") === "true") return;
      button.setAttribute("data-bound", "true");
      button.addEventListener("click", copyAnswer);
    });
    (root || document).querySelectorAll("[data-download-json]").forEach(function (button) {
      if (button.getAttribute("data-bound") === "true") return;
      button.setAttribute("data-bound", "true");
      button.addEventListener("click", downloadJson);
    });
    (root || document).querySelectorAll(".citation-link").forEach(function (link) {
      if (link.getAttribute("data-bound") === "true") return;
      link.setAttribute("data-bound", "true");
      link.addEventListener("click", function () {
        var id = link.getAttribute("href");
        if (!id || id.charAt(0) !== "#") return;
        window.setTimeout(function () {
          var card = document.querySelector(id);
          if (card && typeof card.focus === "function") {
            card.setAttribute("tabindex", "-1");
            card.focus({ preventScroll: true });
          }
        }, 0);
      });
    });
  }

  function bindExamples(root) {
    (root || document).querySelectorAll("[data-fill-question]").forEach(function (button) {
      if (button.getAttribute("data-bound") === "true") return;
      button.setAttribute("data-bound", "true");
      button.addEventListener("click", fillQuestion);
    });
  }

  function bind(root) {
    bindExamples(root);
    bindTabs(root);
    bindResultActions(root);
  }

  document.addEventListener("DOMContentLoaded", function () {
    bind(document);
    document.addEventListener("htmx:beforeRequest", function () { announce("Question is being processed."); });
    document.addEventListener("htmx:afterSwap", function (event) {
      bind(event.target || document);
      var detail = event.detail || {};
      var path = detail.requestConfig && detail.requestConfig.path;
      var status = detail.xhr && detail.xhr.status;
      if (path === "/ui/qa" && status >= 400) {
        announce(status === 429 ? "The agent is busy." : status === 504 ? "The question reached the local deadline." : "The question could not be completed.");
      } else if (path === "/ui/health" && status === 503) {
        announce("The local runtime is not ready.");
      } else {
        announce("Question result updated.");
      }
    });
    document.addEventListener("htmx:beforeSwap", function (event) {
      var detail = event.detail || {};
      var path = detail.requestConfig && detail.requestConfig.path;
      var status = detail.xhr && detail.xhr.status;
      if ((path === "/ui/health" && status === 503) ||
          (path === "/ui/qa" && status >= 400 && status <= 599)) {
        detail.shouldSwap = true;
        detail.isError = false;
      }
    });
    document.addEventListener("htmx:responseError", function () { announce("The request returned an error."); });
    document.addEventListener("htmx:sendError", function () { announce("The request could not reach the local service."); });
  });
}());
