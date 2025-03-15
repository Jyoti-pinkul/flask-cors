document.addEventListener("DOMContentLoaded", function () {
    fetchRecords();

    document.getElementById("filter-form").addEventListener("submit", function (event) {
        event.preventDefault();
        fetchRecords();
    });
});

function fetchRecords() {
    let filter = document.getElementById("filter").value;

    fetch(`/get?filter=${filter}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("total-count").textContent = data.records.length;
            let list = document.getElementById("record-list");
            list.innerHTML = "";

            data.records.forEach(record => {
                let li = document.createElement("li");
                li.textContent = `ID: ${record.id}, Value: ${record.value}, Date: ${record.created_at}`;
                list.appendChild(li);
            });
        });

    document.getElementById("chart").src = `/chart?filter=${filter}`;
}
