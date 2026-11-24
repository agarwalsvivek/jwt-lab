document.getElementById("reset").addEventListener("click", async () => {
  localStorage.clear();
  await fetch("/api/logout", { method: "POST" });
  document.getElementById("status").textContent = "Cleared localStorage and the access_token cookie.";
});
