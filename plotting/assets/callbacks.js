const get_JSON = path => new Promise((res, rej) => {
    fetch(path)
        .then(response => res(response.json()))
        .catch(rej);
});

// See https://dash.plotly.com/clientside-callbacks for an explanation of this
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        // Specify the plotting routine for each file in /plotting/plots here

        "plotting.plots.timehistogram": async function(value) {
            const data = await get_JSON('/stats/activity-times');
            hours = data.map(str => new Date(str).getHours());

            return {
                data: [{
                    xbins: {start: 0, end: 23},
                    nbinsx: 24,
                    x: hours,
                    type: "histogram",
                }],
                layout: {
                    xaxis: {
                        range: [0, 23],
                        title: 'Hour',
                    },
                    yaxis: {
                        showticklabels: false,
                        title: 'No. of activities',
                    }
                },
            }
        }

    }
});
