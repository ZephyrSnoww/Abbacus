let reveal = (item) => {
    $("#" + item + "-container").toggleClass("active");
}

let add = () => {
    window.open("https://discord.com/api/oauth2/authorize?client_id=681498257284661258&permissions=8&scope=bot", '_blank').focus();
}

let support = () => {
    window.open("https://discord.gg/PhGUpgnqv8", '_blank').focus();
}

let login = () => {
    window.open("https://discord.com/oauth2/authorize?response_type=token&client_id=681498257284661258&scope=identify", '_blank').focus();
}

let base_url = "http://73.127.246.154:25565";


if (window.location.hash) {
    var hash = window.location.hash;
    var hashes = hash.split("&");

    if (hashes[1].startsWith("access_token")) {
        var token = hashes[1].split("access_token=")[1];
        var tokenRequest = new Request(`${base_url}/get-user-data`, {
            method: "POST",
            body: JSON.stringify({
                bearer_token: token
            })
        });
    }
}