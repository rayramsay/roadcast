"use strict";

// This code is based on the demo for the Google Maps lecture (bears.js),
// examples from the Google Maps JavaScript API docs, and an example from the
// AJAX lecture.

//////////////////////
// global variables //
var map;
var markersArray = [];
var infoWindow = new google.maps.InfoWindow();
//////////////////////

function initMap(){
    
    // Specify where the map is centered.
    // Defining this variable outside of the map options makes
    // it easier to dynamically change if you need to recenter.
    var myLatLng = {lat: 37.788668, lng: -122.411499};  // Hackbright

    var directionsDisplay = new google.maps.DirectionsRenderer({suppressMarkers: true});
    var directionsService = new google.maps.DirectionsService();

    // Create a map object and specify the DOM element for display.
    map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: false,        
    });

    directionsDisplay.setMap(map);
    
    // This event handler is inside initMap so that it has access to
    // directionsService and directionsDisplay.
    var onSubmitHandler = function(evt) {
        evt.preventDefault();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    };

    $("#directions-request").on("submit", onSubmitHandler);
}

function makeAndSetMarkers(response) {
    for (var i = 0; i < response.length; i++) {

        var markerLatLng = new google.maps.LatLng(response[i].lat, response[i].lng);
        var datapoint = response[i];
        var contentString = makeContentString(response[i]);
        // var titleString = makeTitleString(datapoint);
        var myImageURL = pickImage(datapoint);

        var marker = new google.maps.Marker({
            position: markerLatLng,
            icon: myImageURL,
            // title: titleString,
            map: map
        });


        // The marker's map is set above, but alternately we could call setMap();
        // marker.setMap(map);

        // Add marker to global array.
        markersArray.push(marker);

        // Make infoWindows.
        bindInfoWindow(marker, map, infoWindow, contentString);
    }
}

function bindInfoWindow(marker, map, infoWindow, contentString) {
    // When a marker is clicked, set the content for the window with the content
    // that's passed through, then open the window with the new content on the
    // marker that's clicked.

    google.maps.event.addListener(marker, 'mousemove', function () {
        // infoWindow.close();  // This is unnecessary.
        infoWindow.setContent(contentString);
        infoWindow.open(map, marker);
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

    if (datapoint.fStatus === "OK") {
        //FIXME: Update this to include rain probability/intensity if available.
        var contentString;
        contentString = datapoint.fTime + "<br>" + datapoint.fSummary + "<br>" + datapoint.fTemp + "℉";
    } else { 
        contentString = datapoint.fTime + "<br>" + datapoint.fStatus;
    }
    return contentString;
}

function makeTitleString(datapoint) {
    // Write titleString for marker depending on forecast status.
    var titleString;
    if (datapoint.fStatus === "OK") {
        //FIXME: Update this to include rain probability/intensity if available.
        titleString = datapoint.fTime + "\n" + datapoint.fSummary + "\n" + datapoint.fTemp + "℉";
    } else { 
        titleString = datapoint.fTime + "\n" + datapoint.fStatus;
    }
    return titleString;
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
               makeAndSetMarkers);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
}

google.maps.event.addDomListener(window, 'load', initMap);
