function displayBedwarsDetails {
    var table = document.getElementById('bedwarsDetailsTable');

    var displaySetting = table.style.display;

    var displayBedwarsDetailsButton = document.getElementById('bedwarsDetailsButton');

    if (displaySetting == 'block') {
        table.style.display = 'none';
        displayBedwarsDetailsButton.innerHTML = 'Display Details';
    } else {
        table.style.display = 'block';
        displayBedwarsDetailsButton.innerHTML = 'Hide details';
    }
}