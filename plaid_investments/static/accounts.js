const accountTable = document.getElementById("account-table");

async function getAccounts() {
  let accountResponse = await fetch("/api/get_accounts");
  let jsonResponse = await accountResponse.json();
  if ("accounts" in jsonResponse) {
    let accounts = jsonResponse["accounts"];
    for (account of accounts) {
      if ("content" in document.createElement("template")) {
        let template = document.querySelector("#row-template");
        let clone = template.content.cloneNode(true);

        let accountName = clone.querySelector(".full-name");
        accountName.title = account["official_name"];
        accountName.innerText = account["friendly_name"];

        let mask = clone.querySelector(".mask");
        mask.innerText = ` (x${account["mask"]})`;

        let subtype = clone.querySelector(".subtype");
        subtype.innerText = account["subtype"];

        let balanceButton = clone.querySelector(".getBalance");
        balanceButton.addEventListener("click", () => {
          getAccountBalance(account["item_id"], account["account_id"])
        });

        accountTable.append(clone);
      }
    }
  }
}

/**
 *
 * @param {string} item
 * @param {Array} accountIds
 */
async function getAccountBalance(item, accountIds) {
  console.log(`item: ${item}`);
  console.log(`accountIds: ${accountIds}`)
  let accountResponse = await fetch(
    "/api/get_account_balance?" + new URLSearchParams({item: item, account_ids: accountIds}),
    );
  let jsonResponse = await accountResponse.json();
  console.log(jsonResponse);
}

getAccounts();
