"use strict";

// This code is based on the demo for the Google Maps lecture (bears.js),
// examples from the Google Maps JavaScript API docs, and an example from the
// AJAX lecture.

//////////////////////
// global variables //

var map;
var initialLocation;
var markersArray = [];

//////////////////////

function initMap(){

    var directionsDisplay = new google.maps.DirectionsRenderer({suppressMarkers: true});
    var directionsService = new google.maps.DirectionsService();
    directionsDisplay.setMap(map);

    // Create a map object and specify the DOM element for display.
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 37.7888185, lng: -122.41198699999995},  // Hackbright
        zoom: 12,
        mapTypeId: 'roadmap',
        mapTypeControl: false,
        streetViewControl: false,        
    });

    // Try HTML5 geolocation; if successful, center map on user location.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            map.setCenter(initialLocation);
            console.log("Geolocation and recentering successful.");
        });
    }

    // This event handler is inside initMap so that it has access to
    // directionsService and directionsDisplay.
    var onSubmitHandler = function(evt) {
        evt.preventDefault();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    };

    $("#directions-request").on("submit", onSubmitHandler);
}

function makeMarkersAndReport(data) {
    var markerInfo = data.markerInfo;
    makeAndSetMarkers(markerInfo);
    var weatherReport = data.weatherReport;
    displayWeatherReport(weatherReport);
}

function makeAndSetMarkers(markerInfo) {

    for (var i = 0; i < markerInfo.length; i++) {

        var datapoint = markerInfo[i];
        var markerLatLng = new google.maps.LatLng(datapoint.lat, datapoint.lng);
        var contentString = makeContentString(datapoint);
        var markerImageURL = pickImage(datapoint);

        var marker = new google.maps.Marker({
            position: markerLatLng,
            icon: markerImageURL,
            map: map
        });

        // The marker's map is set above, but alternatively we could call setMap();
        // marker.setMap(map);

        // Add marker to global array.
        markersArray.push(marker);

        // Make infoWindows.
        var infoWindow = new google.maps.InfoWindow();
        bindInfoWindow(marker, map, infoWindow, contentString);
    }
}

function bindInfoWindow(marker, map, infoWindow, contentString) {
    // When a marker is moused-over, set the content for the info window with
    // the string that's passed through, and then open the window with the new
    // content above that marker.

    google.maps.event.addListener(marker, 'mouseover', function () {
        infoWindow.setContent(contentString);
        infoWindow.open(map, marker);
    });

    // When a marker is moused-out, close the info window.

    google.maps.event.addListener(marker, 'mouseout', function () {
        infoWindow.close();
    });
}

function pickImage(datapoint) {
    var URLBase = "/static/img/";
    var myImage;

    if (datapoint.fIcon === "clear-night") {
        myImage = "moonstar.png";
    } else if (datapoint.fIcon === "clear-day") {
        myImage = "sunny.png";
    } else if (datapoint.fIcon === "rain" || datapoint.fIcon === "sleet") {
        myImage = "rainy.png";
    } else if (datapoint.fIcon === "snow") {
        myImage = "snowy-2.png";
    } else if (datapoint.fIcon === "wind") {
        myImage = "wind-2.png";
    } else if (datapoint.fIcon === "partly-cloudy-day") {
        myImage = "cloudysunny.png";
    } else if (datapoint.fIcon === "tornado") {
        myImage = "tornado-2.png";
    } else if (datapoint.fIcon === "thunderstorm") {
        myImage = "thunderstorm.png";
    } else {
        myImage = "cloudy.png";
    }
    
    var myImageURL = URLBase + myImage;
    return myImageURL;
}

function makeContentString(datapoint) {
    // Write contentString for infoWindow depending on forecast status.

    var contentString;

    if (datapoint.fStatus === "OK") {    
        contentString = datapoint.fTime + "<br>" + datapoint.fSummary + "<br>" + datapoint.fTemp + "℉";

        if (datapoint.fPrecipProb > 0) {
            contentString += "<br>" + "Chance of precipitation: " + datapoint.fPrecipProb +"%";
        }

    } else {
        contentString = datapoint.fTime + "<br>" + datapoint.fStatus;
    }
    
    return contentString;
}

function displayWeatherReport(weatherReport) {

    var modalWeather = weatherReport.modalWeather;
    var precipProb = weatherReport.precipProb;
    var avgTemp = weatherReport.avgTemp;

    $("#modal-weather").html(modalWeather);
    $("#precip-prob").html(precipProb);
    $("#avg-temp").html(avgTemp);

    $("#weather-report").show();
}

function calculateAndDisplayRoute(directionsService, directionsDisplay) {
    var start = document.getElementById('start').value;
    var end = document.getElementById('end').value;
    var mode = document.getElementById('mode').value;
    directionsService.route({
      origin: start,
      destination: end,
      travelMode: mode
    }, function(response, status) {
      if (status === 'OK') {
        directionsDisplay.setDirections(response);

        // Delete existing markers.
        for (var i = 0; i < markersArray.length; i++) {
            markersArray[i].setMap(null);
        }
        markersArray.length = 0;

        // Hide existing weather report.
        $("#weather-report").hide();

        // FIXME: Display loading thing.

        var formInputs = {
            "start": start,
            "end": end,
            "mode": mode,
            "departure-day": $("#departure-day").val(),
            "departure-time": $("#departure-time").val(),
            "data": JSON.stringify(response)
        };

        $.post("/request.json",
               formInputs,
               makeMarkersAndReport);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
}

google.maps.event.addDomListener(window, 'load', initMap);
