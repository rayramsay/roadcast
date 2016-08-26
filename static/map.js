"use strict";

// This code is based on the demo for the Google Maps lecture (bears.js),
// examples from the Google Maps JavaScript API docs, and an example from the
// AJAX lecture.

//////////////////////
// global variables //

var map;
var markersArray = [];

//////////////////////

function init(){
    initForm();
    initMap();
}

function initForm(){
    $("#start")
        .geocomplete({types:['geocode', 'establishment']})

        // We need to capture the street address to make the directions request.
        .bind("geocode:result", function(event, result){
            var startAddr;
            // There's a weird bug where sometimes the formatted address is just
            // the country, in which case we're better off with the autocomplete.
            if (result.formatted_address === "United States") {
                startAddr = $("#start").val();
            } else {
                startAddr = result.formatted_address;
            }
            $("#start-addr").val(startAddr);
        });

    $("#end")
        .geocomplete({types:['geocode', 'establishment']})
        .bind("geocode:result", function(event, result){
            var endAddr;
            if (result.formatted_address === "United States") {
                endAddr = $("#end").val();
            } else {
                endAddr = result.formatted_address;
            }
            $("#end-addr").val(endAddr);
    });

    var now = new Date();

    function addZero(i) {
        if (i < 10) {
            i = "0" + i;
        }
        return i;
    }

    var hours = addZero(now.getHours());
    var minutes = addZero(now.getMinutes());
    $("#departure-time").val(hours + ":" + minutes);
}

function initMap(){

    var directionsDisplay = new google.maps.DirectionsRenderer({suppressMarkers: true});
    var directionsService = new google.maps.DirectionsService();

    // Create a map object and specify the DOM element for display.
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 37.7886794, lng: -122.41153689999999},  // Hackbright
        zoom: 12,
        mapTypeId: 'roadmap',
        mapTypeControl: false,
        streetViewControl: false,        
    });

    // Try HTML5 geolocation; if successful, center map on user location.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            console.log(initialLocation.lat(), initialLocation.lng());
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

function calculateAndDisplayRoute(directionsService, directionsDisplay) {
    var start;
    var end;
    var mode;

    // If autocomplete wasn't used, the hidden start-addr field is empty, so we
    // need to copy start's value.
    if ($("#start-addr").val() === "") {
        $("#start-addr").val($("#start").val());
    }
    // After we set start to start-addr's value, empty the value so that if the
    // user inputs another address, start-addr gets updated as above.
    start = $("#start-addr").val();
    $("#start-addr").val("");

    console.log("Start:", start);
    
    if ($("#end-addr").val() === "") {
        $("#end-addr").val($("#end").val());
    }
    end = $("#end-addr").val();
    $("#end-addr").val("");

    console.log("End:", end);
    
    mode = $("#mode").val();

    directionsService.route({
      origin: start,
      destination: end,
      travelMode: mode
    }, function(response, status) {
      if (status === 'OK') {
        directionsDisplay.setDirections(response);
        directionsDisplay.setMap(map);

        // Delete existing markers.
        for (var i = 0; i < markersArray.length; i++) {
            markersArray[i].setMap(null);
        }
        markersArray.length = 0;

        // Hide existing weather report.
        $("#weather-report").hide();

        $("#submit-button").val("Loading...");

        var formInputs = {
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

function makeMarkersAndReport(data) {
    var markerInfo = data.markerInfo;
    makeAndSetMarkers(markerInfo);
    var weatherReport = data.weatherReport;
    displayWeatherReport(weatherReport);
    $("#submit-button").val("Submit");

    var before = $("#before").val();
    var after = $("#after").val();

    if (before > 0 || after > 0) {
        $("#recommendation").show();

        var formInputs = {
            "before": before,
            "after": after,
            "data": JSON.stringify(data)
        };

        $.post("/recommendation.json",
               formInputs,
               handleRecs);
    }
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

function handleRecs(data) {
    console.log("hi");
}

google.maps.event.addDomListener(window, 'load', init);
