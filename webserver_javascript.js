function tick() {
    const element = (
        <p>{new Date().toLocaleTimeString()}</p>
    );

    ReactDOM.render(element, document.getElementById("time"));
}

tick();
setInterval(tick, 1000);