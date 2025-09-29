(function(){
  const params = new URLSearchParams(location.search);
  const apiFromQS = params.get("api");
  if (apiFromQS) localStorage.setItem("api_base_override", apiFromQS);
  const apiOverride = localStorage.getItem("api_base_override") || (window.API_BASE_OVERRIDE || "").trim();
  window.APP_CONFIG = {
    // NOTE: replace with your final gateway domain after Render deploy
    API_BASE: apiOverride || (location.hostname === "localhost" ? "http://localhost:8000" : "https://gateway-production.example"),
    ADMIN_BEARER: "",
  };
})();