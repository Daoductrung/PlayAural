window.PLAYAURAL_WEB_VERSION = "1.0.4.8";

function startupErrorMessage() {
  const language = String(navigator.language || "").toLowerCase();
  if (language.startsWith("vi")) {
    return "Không thể khởi động PlayAural Web. Vui lòng tải lại trang.";
  }
  return "PlayAural Web could not start. Please refresh this page.";
}

function showStartupError(error) {
  console.error("PlayAural web client failed to start.", error);
  const target = document.getElementById("live-assertive") || document.body;
  const message = document.createElement("p");
  message.textContent = startupErrorMessage();
  target.appendChild(message);
}

function loadOptionalConfig() {
  return new Promise((resolve) => {
    const script = document.createElement("script");
    script.src = "config.js";
    script.async = false;
    script.addEventListener("load", () => resolve(), { once: true });
    script.addEventListener("error", () => resolve(), { once: true });
    document.head.appendChild(script);
  });
}

loadOptionalConfig()
  .then(() => import("./app.js"))
  .catch(showStartupError);
