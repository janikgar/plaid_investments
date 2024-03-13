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
    onSuccess: async (publicToken, metadata) => {
      let tokenResponse = await (await exchangePublicToken(publicToken)).json();
      let itemResponse = await (await createItem(tokenResponse["item_id"], tokenResponse["access_token"])).json();
      let accountResponse = await (await createAccountsFromItem(itemResponse["item_id"], itemResponse["access_token"])).json();
      console.log(accountResponse);
      // exchangePublicToken(publicToken).then(tokenResponse => {
      //   console.log(`tokenResponse: ${tokenResponse}`)
      //   createItem(
      //     tokenResponse["item_id"],
      //     tokenResponse["access_token"],
      //   ).then(itemResponse => {
      //     createAccountsFromItem(
      //       itemResponse["item_id"],
      //       itemResponse["access_token"]
      //     )
      //       .then((accountsResponse) => {
      //         console.log(accountsResponse);
      //       })
      //       .catch((reason) => {
      //         console.log(`could not create accounts: ${reason}`);
      //       });
      //   }).catch(reason => {
      //     console.log(`could not create item: ${reason}`);
      //   })
      // }).catch(reason => {
      //   console.log(`could not exchange token: ${reason}`);
      // })
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

/**
 * 
 * @param {string} itemId 
 * @param {string} accessToken 
 */
const createAccountsFromItem = (itemId, accessToken) => {
  return fetch("/api/create_accounts_from_item",{
    method: "POST",
    body: JSON.stringify({
      item_id: itemId,
      access_token: accessToken,
    }),
    headers: {
      "Content-Type": "application/json",
    }
  });
}

/**
 * 
 * @param {string} publicToken 
 */
const exchangePublicToken = (publicToken) => {
  return fetch("/api/exchange_public_token", {
    method: "POST",
    body: JSON.stringify({ public_token: publicToken }),
    headers: {
      "Content-Type": "application/json",
    },
  });
}

/**
 * 
 * @param {string} itemId 
 * @param {string} accessToken 
 */
const createItem = (itemId, accessToken) => {
  return fetch("/api/create_item", {
    method: "POST",
    body: JSON.stringify({
      item_id: itemId,
      access_token: accessToken,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  });
}