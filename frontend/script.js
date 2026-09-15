const API_URL = "http://localhost:5000/api/devices";


async function loadDevices() {

    const response = await fetch(API_URL);

    const devices = await response.json();

    const table =
        document.getElementById("deviceTable");

    table.innerHTML = "";

    let online = 0;

    devices.forEach(device => {

        if (device.status === "Online") {
            online++;
        }

        const row =
            document.createElement("tr");

        row.innerHTML = `

            <td>${device.id}</td>

            <td>${device.name}</td>

            <td>${device.ip}</td>

            <td>${device.device_type}</td>

            <td>${device.status}</td>

            <td>

                <button
                    onclick="deleteDevice(${device.id})">
                    Delete
                </button>

            </td>
        `;

        table.appendChild(row);

    });


    document.getElementById(
        "totalDevices"
    ).innerText = devices.length;


    document.getElementById(
        "onlineDevices"
    ).innerText = online;


    document.getElementById(
        "offlineDevices"
    ).innerText =
        devices.length - online;
}


async function addDevice() {

    const name =
        document.getElementById("name").value;

    const ip =
        document.getElementById("ip").value;

    const device_type =
        document.getElementById(
            "deviceType"
        ).value;


    if (!name || !ip) {

        alert("Please fill all fields");

        return;
    }


    await fetch(API_URL, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            name: name,

            ip: ip,

            device_type: device_type

        })

    });


    document.getElementById("name").value = "";

    document.getElementById("ip").value = "";


    loadDevices();

}


async function deleteDevice(id) {

    await fetch(
        `${API_URL}/${id}`,
        {
            method: "DELETE"
        }
    );

    loadDevices();
}


loadDevices();