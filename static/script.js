document.getElementById("licitacao-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const dados = {
        number_days: formData.get("number_days"),
        // email: formData.get("email"),
        // senha: formData.get("senha"),
        keywords: formData.get("keywords").split(",").map(p => p.trim())
    };

    const res = await fetch("/licitacoes", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(dados)
    });

    const resultado = await res.json();

    document.getElementById("resultado").innerText = JSON.stringify(resultado, null, 2);
});