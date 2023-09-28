
// Function to fetch data from the API
function fetchData() {
    // Replace 'YOUR_API_ENDPOINT' with the actual API endpoint you want to use
    fetch('http://127.0.0.1:5000/display')
        .then(response => response.json())
        .then(data => {
            // Get a reference to the table body
            var tableBody = document.querySelector('tbody');

            // Clear any existing rows in the table
            tableBody.innerHTML = '';

            // Loop through the data and insert it into the table
            data.forEach((item, index) => {
                var row = document.createElement('tr');
                row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${item[0]}</td>
                        <td>${item[1]}</td>
                        <td>${item[2]}</td>
                        <td>${item[3] ? "Internal" : "External"}</td>
                        <td>${item[4]}</td>
                        <td>${item[5]}</td>
                    `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

// Call the fetchData function when the page loads
window.onload = fetchData;

// <td>
//     <button class="btn btn-success" style="margin-left: 5px;" type="submit"><i class="fa fa-check" style="font-size: 15px;"></i></button>
//     <button class="btn btn-danger" style="margin-left: 5px;" type="submit"><i class="fa fa-trash" style="font-size: 15px;"></i></button>
// </td>