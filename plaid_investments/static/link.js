const createLinkToken = async () => {
  const response = await fetch("/api/create_link_token");
  const data = await response.json();
  const linkToken = data.link_token;
  localStorage.setItem("link_token", linkToken);
  return linkToken;
};

createLinkToken().then((token) => {
  const handler = Plaid.create({
    token: token,
    onSuccess: (public_token, metadata) => {
      fetch("/api/exchange_public_token", {
        method: "POST",
        body: JSON.stringify({ public_token: public_token }),
        headers: {
          "Content-Type": "application/json",
        },
      }).then(async (response) => {
        let responseLocation = document.getElementById("response");
        let responseText = await response.text();
        responseLocation.innerText = responseText;
      });
    },
    onLoad: () => {},
    onExit: (err, metadata) => {
      console.log(`Error: ${err}`);
    },
    onEvent: (eventName, metadata) => {},
  });

  const linkAccountButton = document.getElementById("link-account");
  linkAccountButton.addEventListener("click", (event) => {
    handler.open();
  });
});
