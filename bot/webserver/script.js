// Toggling active class on items
let reveal = (item) => {
    $("#" + item + "-container").toggleClass("active");
}

// Opening the bot page
let add = () => {
    window.open("https://discord.com/api/oauth2/authorize?client_id=681498257284661258&permissions=8&scope=bot", '_blank').focus();
}

// Opening the support server invite
let support = () => {
    window.open("https://discord.gg/PhGUpgnqv8", '_blank').focus();
}

// Opening the OAuth login page
let login = () => {
    window.open("https://discord.com/oauth2/authorize?response_type=token&client_id=681498257284661258&scope=identify", '_blank').focus();
}

// Base website URL
let base_url = "http://73.127.246.154:25565";


// If they've logged in (theres info in the url hash)
if (window.location.hash) {
    // Grab all the info
    var hash = window.location.hash;
    var hashes = hash.split("&");

    // If the info includes an access token
    if (hashes[1].startsWith("access_token")) {
        // Yoink it
        var token = hashes[1].split("access_token=")[1];
        // Create a request to the server with the token
        var tokenRequest = new Request(`${base_url}/get-user-data`, {
            method: "POST",
            body: JSON.stringify({
                bearer_token: token
            })
        });

        // Actually submit the request
        fetch(tokenRequest).then((response) => {
            // Get the response's JSON
            response.json().then((json) => {
                
            })
        })
    }
}