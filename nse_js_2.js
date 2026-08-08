"use strict";

var optionChainWS = void 0;
var optionChainSocket = false;
var restartTimeout = void 0;
setupActivityTracking();
resetInactivityTimer();
function getSelectedSymbol() {

    var nifty = document.getElementById("equity_optionchain_select").value;
    var custom = document.getElementById("select_symbol").value;

    if (custom && custom !== "Select") return custom;
    return nifty;
}

function streamOptionChain(status, symbol, expiry, strike) {
    if (status === true && optionChainWS) {

        if (optionChainWS.readyState === WebSocket.OPEN || optionChainWS.readyState === WebSocket.CONNECTING) {
            console.log("Closing existing socket before new connection");
            optionChainWS.close();
        }
    }

    if (status === false) {
        if (optionChainWS) {
            try {
                optionChainWS.close();
            } catch (e) {}
        }

        optionChainSocket = false;
        console.log("Option Chain WebSocket closed.");
        return;
    }
    var url = void 0;
    var strikeprice = strike ? strike.replace(',', '').replace('.00', '.0') : '';
    if (expiry) {
        url = optionchainStreamURL + "streams/fo/mbp?symbol=" + encodeURIComponent(symbol) + "&expiry=" + encodeURIComponent(expiry);
    } else {
        url = optionchainStreamURL + "streams/fo/mbp?symbol=" + encodeURIComponent(symbol) + "&strike=" + encodeURIComponent(strikeprice);
    }

    optionChainWS = new WebSocket(url);
    optionChainWS.onopen = function () {
        optionChainSocket = true;
        console.log("Option Chain WebSocket connected...");
    };

    optionChainWS.onmessage = function (event) {
        try {
            var streamData = JSON.parse(event.data);
            updateOptionChainRow(streamData);
        } catch (e) {
            console.error("Option Chain Stream Parse Error:", e);
        }
    };

    optionChainWS.onclose = function () {
        optionChainSocket = false;
        console.log("Option Chain WebSocket disconnected.");
    };
    optionChainWS.onerror = function (error) {
        console.error("Option Chain WebSocket error:", error);
    };
}

function restartOptionChainStream() {
    clearTimeout(restartTimeout);
    restartTimeout = setTimeout(function () {
        var toggle = document.getElementById("stream-optionchain-tile");
        if (!toggle.checked) return;

        var symbol = getSelectedSymbol();

        var expiry = document.getElementById("expirySelect").value;

        console.log("Switching stream to:", symbol, expiry);

        streamOptionChain(true, symbol, expiry);
    }, 200);
}

function updateOptionChainRow(data) {

    if (!data || !data.strikePrice) return;
    if (data.timestamp) {
        var timeContainer = document.getElementById("equity_timeStamp");

        if (timeContainer) {
            timeContainer.innerHTML = '<span id="asontxt">As on </span><span>' + formatWSSTimestamp(data.timestamp) + '</span>';
        }
    }
    var sp = data.strikePrice.toString().replace('.', '_');
    var ex = data.expiryDates.toString().replace(/-/g, '');

    if (data.CE) updateSide(sp + ex, "CE", data.CE);

    if (data.PE) updateSide(sp + ex, "PE", data.PE);
}
function formatWSSTimestamp(timestamp) {
    var dt = new Date(timestamp.replace(' ', 'T'));

    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    var day = String(dt.getDate()).padStart(2, "0");
    var month = months[dt.getMonth()];
    var year = dt.getFullYear();
    var hours = String(dt.getHours()).padStart(2, "0");
    var minutes = String(dt.getMinutes()).padStart(2, "0");
    var seconds = String(dt.getSeconds()).padStart(2, "0");

    return day + "-" + month + "-" + year + " " + hours + ":" + minutes + ":" + seconds + " IST";
}
function updateSide(strike, side, optionData) {
    var decimalColumns = new Set(["buyPrice1", "lastPrice", "sellPrice1", "change"]);
    var allowedColumns = new Set(["buyPrice1", "lastPrice", "sellPrice1", "change", "sellQuantity1", "buyQuantity1"]);
    Object.keys(optionData).forEach(function (key) {
        if (!allowedColumns.has(key)) return;
        var cellId = "" + strike + side + "-" + key;
        var cell = document.getElementById(cellId);

        if (!cell) return;

        var oldValue = cell.innerText;
        var newValue = optionData[key];

        if (newValue === null || newValue === undefined) {
            newValue = "-";
        }

        var useDecimal = decimalColumns.has(key);
        if (typeof newValue === "number") {
            if (newValue === 0 || newValue === 0.00) {
                newValue = '-';
            } else if (useDecimal) {
                newValue = newValue.toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            } else {
                newValue = Math.trunc(newValue).toLocaleString("en-IN");
            }
        }

        if (oldValue !== newValue.toString()) {

            if (typeof highlightPriceChangeop === "function") {

                var oldNum = parseFloat(oldValue.toString().replaceAll(',', "")) || 0;
                var newNum = parseFloat(newValue.toString().replaceAll(',', "")) || 0;
                if (key === "change") {
                    cell.innerHTML = "<span class=\"" + (newNum >= 0 ? "greenTxt" : "redTxt") + "\">" + newValue + "</span>";
                    return;
                }

                var diff = newNum - oldNum;
                var flag = diff >= 0 ? 1 : 0;
                var anchor = cell.querySelector("a");
                if ((key === 'buyQuantity1' || key === 'sellQuantity1') && newValue === '-') {
                    cell.innerText = '-';
                    return;
                }
                var updatedHtml = highlightPriceChangeop(oldValue, newValue, flag, undefined, useDecimal);
                if (anchor) {
                    anchor.innerHTML = updatedHtml;
                } else {
                    cell.innerHTML = updatedHtml;
                }
            } else {
                cell.innerText = newValue;
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("stream-optionchain-tile");
    var niftyDropdown = document.getElementById("equity_optionchain_select");
    var customDropdown = document.getElementById("select_symbol");
    var expiryDropdown = document.getElementById("expirySelect");
    var strikeDropdown = document.getElementById("strikeSelect");

    toggle.checked = false;

    toggle.addEventListener("change", function () {

        var symbol = getSelectedSymbol();
        var expiry = expiryDropdown.value;
        var strike = strikeDropdown.value.replace(',', '').replace('.00', '.0');
        if (this.checked) {
            console.log("Streaming ON");
            streamOptionChain(true, symbol, expiry, strike);
        } else {
            console.log("Streaming OFF");
            streamOptionChain(false);
        }
    });

    if (niftyDropdown) {
        niftyDropdown.addEventListener("change", function () {
            if (customDropdown) customDropdown.value = "Select";
            restartOptionChainStream();
        });
    }

    if (customDropdown) {

        customDropdown.addEventListener("change", function () {
            if (niftyDropdown) niftyDropdown.value = "";
            restartOptionChainStream();
        });
    }

    if (expiryDropdown) {
        expiryDropdown.addEventListener("change", restartOptionChainStream);
    }
});

function highlightPriceChangeop(oldPrice, newPrice, flag) {
    var textClass = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : ["greenBlnk", "redBlnk"];
    var useDecimal = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : false;
    var preservebasecolor = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : false;

    var statusClass = flag ? textClass[0] : textClass[1];

    oldPrice = oldPrice != null ? oldPrice.toString() : "0";
    newPrice = newPrice != null ? newPrice.toString() : "0";

    var oldParts = oldPrice.split(".");
    var newParts = newPrice.split(".");

    var highlightedPrice = "";

    var oldInt = oldParts[0] || "0";
    var newInt = newParts[0] || "0";

    var diffIndex = -1;

    var maxLength = Math.max(oldInt.length, newInt.length);

    for (var i = 0; i < maxLength; i++) {
        if (oldInt[i] !== newInt[i]) {
            diffIndex = i;
            break;
        }
    }

    if (diffIndex === -1) {
        highlightedPrice = preservebasecolor ? "<span>" + newInt + "</span>" : "<span class=\"normattext\">" + newInt + "</span>";
    } else {
        highlightedPrice = preservebasecolor ? "<span>" + newInt.substring(0, diffIndex) + "</span>" : "<span class=\"normattext\">" + newInt.substring(0, diffIndex) + "</span>" + ("<span class=\"highlight " + statusClass + "\">" + newInt.substring(diffIndex) + "</span>");
    }

    if (useDecimal && newParts[1]) {
        if (oldParts[1] && oldParts[1] !== newParts[1]) {
            highlightedPrice += ".<span class=\"highlight " + statusClass + "\">" + newParts[1] + "</span>";
        } else {
            highlightedPrice += "." + newParts[1];
        }
    }

    return highlightedPrice;
}
var inactivityTimer = void 0;
var INACTIVITY_TIMEOUT = 6 * 60 * 1000;
function resetInactivityTimer() {
    clearTimeout(inactivityTimer);

    var toggle = document.getElementById("stream-optionchain-tile");

    if (!toggle || !toggle.checked) return;

    inactivityTimer = setTimeout(function () {

        toggle.checked = false;
        streamOptionChain(false);
    }, INACTIVITY_TIMEOUT);
}

function setupActivityTracking() {
    ["mousemove", "mousedown", "keypress", "scroll", "touchstart", "click"].forEach(function (eventType) {
        document.addEventListener(eventType, resetInactivityTimer, true);
    });
}