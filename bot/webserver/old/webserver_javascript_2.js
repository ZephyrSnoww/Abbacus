// ==================================================
// The clock
// ==================================================
function tick() {
    const element = (
        <p>{new Date().toLocaleTimeString()}</p>
    );

    ReactDOM.render(element, document.getElementById("time"));
}

tick();
setInterval(tick, 1000);




// ==================================================
// Grabbing elements
// ==================================================
var site_container = document.getElementById("site-content-outer-container");
var slider_content = document.getElementById("sliding-content");
var home_page = document.getElementById("site-content-inner-container");
var user_page = document.getElementById("user-settings-inner-container");
var server_page = document.getElementById("server-settings-inner-container");





// ==================================================
// Starting variables
// ==================================================
var user_id;
var server_id;
var base_url = "http://4484c1d10149.ngrok.io";









// ==================================================
// Basic functions
// ==================================================
// ==================================================
// Redirect to bot invite link
// ==================================================
var serverInvite = () => {
    window.location.replace("https://discord.com/api/oauth2/authorize?client_id=681498257284661258&permissions=8&scope=bot");
}

// ==================================================
// Redirect to support server invite
// ==================================================
var supportInvite = () => {
    window.location.replace("https://discord.gg/PhGUpgnqv8");
}

// ==================================================
// Redirect to discord oauth
// ==================================================
var login = () => {
    window.location.replace("https://discord.com/oauth2/authorize?response_type=token&client_id=681498257284661258&scope=identify");
}

// ==================================================
// Simple getting element by id
// ==================================================
var id = (id) => document.getElementById(id);

var data = (data) => document.querySelectorAll(`[${data}]`);

// ==================================================
// Tab switching
// ==================================================
var switchTo = (what) => {
    if (what == "home") {
        home_page.scrollIntoView(false);
        site_container.scrollTop -= 50000;
    } else if (what == "user") {
        user_page.scrollIntoView(false);
        site_container.scrollTop -= 50000;
    } else {
        server_page.scrollIntoView(false);
        site_container.scrollTop -= 50000;
    }
}

// ==================================================
// Updating user color on input change
// ==================================================
id("user-color-input").addEventListener("input", (event) => {
    document.documentElement.style.setProperty('--user-color', id("user-color-input").value);
});

// ==================================================
// Integer to hex string
// ==================================================
const intToHex = function (rgb) { 
    var hex = Number(rgb).toString(16);
    while (hex.length % 2 == 1) {
        hex = "0" + hex;
    }
    return hex;
};

// ==================================================
// Hex string to integer
// ==================================================
const hexToInt = (number) => {
    if (number.startsWith("#")) {
        number = number.substring(1);
    }
    return parseInt(number, 16);
}

// ==================================================
// Hiding alert box
// ==================================================
var hideAlert = () => {
    id("alert-container").style.display = "none";
}

// ==================================================
// Manually firing events
// ==================================================
function fireEvent(element, event_type){
    if (element.fireEvent) {
        element.fireEvent('on' + event_type);
    } else {
        var evObj = document.createEvent('Events');
        evObj.initEvent(event_type, true, false);
        element.dispatchEvent(evObj);
    }
}

// ==================================================
// Checkboxes
// ==================================================
var handleCheckbox = (event) => {
    event.target.checked = event.target.checked;
}











// ==================================================
// More complicated functions
// ==================================================
// ==================================================
// Update collapsibles
// (Updates their max height)
// ==================================================
var updateCollapsibles = () => {
    var collapsibles = document.getElementsByClassName("collapsible-button");

    // ==================================================
    // Iterate through all collapsibles
    // ==================================================
    for (var i = 0; i < collapsibles.length; i++) {
        // ==================================================
        // Clone it (to remove any previous event listeners)
        // Add a click event listener
        // On click, expand dropdown
        // ==================================================
        var clone = collapsibles[i].cloneNode(true);
        collapsibles[i].parentNode.replaceChild(clone, collapsibles[i]);
        clone.addEventListener("click", (event) => {
            var targetElement = event.target;
            targetElement.classList.toggle("active-collapsible-button");
            var content = targetElement.nextElementSibling;
            if (content.style.display == "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
}

updateCollapsibles();



// ==================================================
// Add a hall
// ==================================================
var addHall = () => {

}



// ==================================================
// Submit server settings
// ==================================================
var submitServerSettings = () => {
    var settings = {
        "settings": {
            "halls": {},
        },
        "server_id": server_id
    };
    var halls = document.getElementsByClassName("hall-container");

    for (var hall in halls) {
        settings["settings"]["halls"][hall.getAttribute("server")] = {
            "requirement": data(`${hall_name}-requirement`).value,
            "announcement message": data(`${hall_name}-announcement`).value,
            "announcement message enabled": data(`${hall_name}-announcement-enabled`).value,
            "removal message": data(`${hall_name}-removal`).value,
            "removal message enabled": data(`${hall_name}-removal-enabled`).value,
            "placement message": data(`${hall_name}-placement`).value,
            "placement message proxied": data(`${hall_name}-placement-proxied`).value,
            "rival hall": data(`${hall_name}-rival`).value
        }
    }

    var request = new Request(`${base_url}/set-server-data`, {
        "method": "POST",
        "body": JSON.stringify({settings})
    });

    fetch(request).then((response) => {
        response.jdon().then((json) => {
            var elements = [];

            for (var setting in json) {
                elements.push(
                    <div className="paragraph">{setting} changed to {json[setting]}</div>
                );
            }

            var element = <div id="alert-content-container">{elements}</div>;
            id("alert-title").innerText = "Success!";

            if (elements.length == 0) {
                id("alert-title").innerText = "Whoops!";
                var element = (
                    <div id="alert-content-container">
                        <div className="paragraph">No settings were changed!</div>
                    </div>
                );
            }

            ReactDOM.render(element, id("alert-content"));

            id("alert-container").style.display = "flex";
        });
    });
}



// ==================================================
// Select a server
// ==================================================
var selectServer = (server_id) => {
    var serverRequest = new Request(`${base_url}/get-server-data`, {
        "method": "POST",
        "body": JSON.stringify({"server_id": server_id})
    });

    // ==================================================
    // Send request to server for server data
    // ==================================================
    fetch(serverRequest).then((response) => {
        response.json().then((json) => {
            // ==================================================
            // Check if server returns error
            // Change sever select header to server name
            // Simulate click on server list (close the collapsible)
            // ==================================================
            if (json.error) { return }
            id("server-select-button").innerHTML = json["server_name"];
            fireEvent(id("server-select-button"), "click");

            // ==================================================
            // For each hall the server has
            // ==================================================
            var halls = [];
            for (var hall_name in json.halls) {
                var channel_elements = [];

                // ==================================================
                // Make a lise of all channels the server has
                // ==================================================
                for (var i = 0; i < json.channels.length; i++) {
                    if (json.channels[i].channel_id == json.halls[hall_name].channel.substring(2, json.halls[hall_name].channel.length-1)) {
                        channel_elements.push(
                            <li key={json.channels[i].channel_id} channelid={json.channels[i].channel_id} className="selected-channel">#{json.channels[i].channel_name}</li>
                        );
                    } else {
                        channel_elements.push(
                            <li key={json.channels[i].channel_id} channelid={json.channels[i].channel_id}>#{json.channels[i].channel_name}</li>
                        );
                    }
                }

                // ==================================================
                // Make one huge hall container element with all info
                // ==================================================
                var element = (
                    <div className="hall-container" key={hall_name} server={hall_name}>
                        <div className="collapsible-container">
                            <div className="collapsible-button">{hall_name}</div>

                            <div className="collapsible-content">
                                <div className="hall-settings-first-group">
                                    <div className="hall-channel-setting-container hall-setting-container">
                                        <div className="hall-channel-setting-title">Channel</div>
                                        <ul className="hall-channel-list">
                                            {channel_elements}
                                        </ul>
                                    </div>

                                    <div className="hall-side-settings-container">
                                        <div className="hall-requirement-setting-container hall-setting-container">
                                            <div className="hall-requirement-title tiny-title">Requirement</div>
                                            <input setting={`${hall_name}-requirement`} className="hall-requirement-input simple-input" defaultValue={json.halls[hall_name].requirement} />
                                        </div>
                                        <hr />
                                        <hr />
                                        <div className="hall-rival-setting-container hall-setting-container">
                                            <div className="hall-rival-title tiny-title">Rival</div>
                                            <input setting={`${hall_name}-rival`} className="hall-rival-input simple-input" defaultValue={json.halls[hall_name]["rival hall"]} />
                                        </div>
                                        <hr />
                                        <hr />
                                        <div className="hall-emoji-setting-container hall-setting-container">
                                            <div className="hall-emoji-button small-button" onClick={() => {setEmoji(hall_name)}}>Set Emoji</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="hall-settings-second-group">
                                    <div className="message-container">
                                        <div className="message-title">Announcement Message</div>
                                        <input setting={`${hall_name}-announcement`} id="announcement-message-input" className="message-input" defaultValue={json.halls[hall_name]["announcement message"]} />
                                        <input setting={`${hall_name}-announcement-enabled`} id="announcement-message-enabled" className="hall-checkbox" type="checkbox" defaultChecked={json.halls[hall_name]["announcement message enabled"]} />
                                    </div>

                                    <hr />
                                    <hr />
                                    <div className="message-container">
                                        <div className="message-title">Removal Message</div>
                                        <input setting={`${hall_name}-removal`} id="removal-message-input" className="message-input" defaultValue={json.halls[hall_name]["removal message"]} />
                                        <input setting={`${hall_name}-removal-enabled`} id="removal-message-enabled" className="hall-checkbox" type="checkbox" defaultChecked={json.halls[hall_name]["removal message enabled"]} />
                                    </div>

                                    <hr />
                                    <hr />
                                    <div className="message-container">
                                        <div className="message-title">Placement Message</div>
                                        <input setting={`${hall_name}-placement`} id="placement-message-input" className="message-input" defaultValue={json.halls[hall_name]["placement message"]} />
                                        <input setting={`${hall_name}-placement-proxied`} id="placement-message-proxied" className="hall-checkbox" type="checkbox" defaultChecked={json.halls[hall_name]["placement message proxied"]} />
                                    </div>
                                </div>
                            </div>
                        </div>
                        <hr className="big-hr" />
                        <hr />
                        <hr />
                    </div>
                );

                halls.push(element);
            }

            // ==================================================
            // Consolidate everything
            // Render
            // Update collapsibles
            // ==================================================
            var final_element = (
                <div id="hall-settings-content-container" className="collapsible-inner-content">
                    <hr />
                    {halls}
                    <hr />
                    <div className="hall-settings-add-hall-button small-button half-width own-line" onClick={() => {addHall()}}>Add Hall</div>
                    <hr />
                </div>
            );

            ReactDOM.render(final_element, id("hall-settings-content"));

            updateCollapsibles();
        });
    });
}



// ==================================================
// Submitting user settings
// ==================================================
var submitUserSettings = () => {
    var user_data = {
        "user_id": user_id,
        "settings": {
            "color": hexToInt(id("user-color-input").value)
        }
    };

    var settingsRequest = new Request(`${base_url}/set-user-data`, {
        "method": "POST",
        "body": JSON.stringify(user_data)
    });

    fetch(settingsRequest).then((response) => {
        response.json().then((json) => {
            var elements = [];

            for (var setting in json) {
                elements.push(
                    <div className="paragraph">{setting} changed to {json[setting]}</div>
                );
            }

            var element = <div id="alert-content-container">{elements}</div>;

            id("alert-title").innerText = "Success!";

            if (elements.length == 0) {
                id("alert-title").innerText = "Whoops!";
                var element = (
                    <div id="alert-content-container">
                        <div className="paragraph">No settings were changed!</div>
                    </div>
                );
            }

            ReactDOM.render(element, id("alert-content"));

            id("alert-container").style.display = "flex";
        });
    });
}











// ==================================================
// Checking if logged in
// ==================================================
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

        fetch(tokenRequest).then((response) => {
            response.json().then((json) => {
                if (json.valid_servers.length == 0) {
                    const element = (
                        <ul id="server-select-list">
                            <li key="1">You aren't in any servers I'm in!</li>
                            <li key="2"> Add me to a server from the homepage!</li>
                            <hr />
                        </ul>
                    )

                    ReactDOM.render(element, document.getElementById("server-select-content-container"));
                } else {
                    var servers = [];
                    for (let i = 0; i < json.valid_servers.length; i++) {
                        servers.push(
                            <li key={json.valid_servers[i][0]} onClick={() => {selectServer(json.valid_servers[i][1])}}>{json.valid_servers[i][0]}</li>
                        )
                    }

                    const element = (
                        <ul id="server-select-list">
                            {servers}
                            <hr />
                        </ul>
                    )

                    ReactDOM.render(element, document.getElementById("server-select-content-container"));
                }

                id("login-button").style.display = "none";
                id("server-settings-warning").style.display = "none";
                var innermost = document.getElementsByClassName("innermost-container");
            
                for (var i = 0; i < innermost.length; i++) {
                    innermost[i].style.display = "flex";
                }
                // id("server-settings-form").style.display = "flex";
                id("user-color-input").value = "#" + intToHex(json.color);
                document.documentElement.style.setProperty('--user-color', "#" + intToHex(json.color));
                user_id = json.id;
            });
        });
    }
}