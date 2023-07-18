window.onload = function () {
    console.log("GOGOGO")
    const formElement = document.querySelector('form');
    formElement.addEventListener('submit', submit_search);
}


function submit_search(event) {
    event.preventDefault();
    form = new FormData(event.target);

    fetch(`/get_dnsty_json?plant_ID=${form.get("plant_ID")}&start_date=${form.get("start_date")}&end_date=${form.get("end_date")}&matters=${form.getAll("matters")}&AI_option=${form.get("AI_option")}`, {
        method: "POST",
        body: form
    })
        .then(response => response.json())
        .then(result => {
            console.log(result);
            const chart_sect = document.getElementById('chart_sect');
            $("#chart_sect").empty();
            for (let i = 0; i < result.length; i++) {
                let new_child = document.createElement(`canvas`)
                let gogo = chart_sect.appendChild(new_child)
                let now_item = result[i]
                let matter_name = Object.keys(now_item)[0]
                let data_arr = Object.values(now_item)[0]
                let day_arr = data_arr.map((item) => { return Object.keys(item)[0] });
                let dnsty_arr = data_arr.map((item) => { return Object.values(item)[0] });
                console.log(data_arr)
                console.log(day_arr)
                console.log(dnsty_arr)

                new Chart(gogo, {
                    type: 'line',
                    data: {
                        labels: day_arr,
                        datasets: [{
                            label: matter_name,
                            data: dnsty_arr,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            }
        })
        .catch(error => {
            console.error(error);
        });
}

function show_chart() {
    const chart_sect = document.getElementById('chart_sect');
    $("#chart_sect").empty();
    async function get_promise() {
        let response = await fetch('http://127.0.0.1:5000/gogo');
        let data = await response.json();
        return await data;
    }
    get_promise().then((result) => {
        const chart_sect = document.getElementById('chart_sect');
        for (let i = 0; i < result.length; i++) {
            let new_child = document.createElement(`canvas`)
            let gogo = chart_sect.appendChild(new_child)
            let now_item = result[i]
            let matter_name = Object.keys(now_item)[0]
            let data_arr = Object.values(now_item)[0]
            let day_arr = data_arr.map((item) => { return Object.keys(item)[0] });
            let dnsty_arr = data_arr.map((item) => { return Object.values(item)[0] });
            // console.log(data_arr)
            // console.log(day_arr)
            // console.log(dnsty_arr)

            new Chart(gogo, {
                type: 'line',
                data: {
                    labels: day_arr,
                    datasets: [{
                        label: matter_name,
                        data: dnsty_arr,
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

    })
}
