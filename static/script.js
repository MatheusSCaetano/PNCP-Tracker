document.getElementById("licitacao-form").addEventListener("submit", async (e) => {
    
    e.preventDefault();

    const formData = new FormData(e.target);

    const dados = {
        number_days: formData.get("number_days"),
        prompt: formData.get("prompt"),
        keywords: formData.get("keywords")//.split(",").map(p => p.trim())
    };

    console.log("Dados a serem enviados:", dados);

    const res = await fetch("/licitacoes", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(dados)
    });

    const resultado = await res.json();

    document.getElementById("results").innerText = JSON.stringify(resultado, null, 2);
});