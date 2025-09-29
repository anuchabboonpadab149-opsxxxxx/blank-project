(function(){
  const params = new URLSearchParams(location.search);
  const apiFromQS = params.get("api");
  if (apiFromQS) localStorage.setItem("api_base_override", apiFromQS);
  const apiOverride = localStorage.getItem("api_base_override") || (window.API_BASE_OVERRIDE || "").trim();
  window.APP_CONFIG = {
    API_BASE: apiOverride || (location.hostname === "localhost" ? "http://localhost:8000" : "https://your-gateway-domain.example"),
    ADMIN_BEARER: "",
  };
})();