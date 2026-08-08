'use strict';

var _typeof2 = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _typeof = typeof Symbol === "function" && _typeof2(Symbol.iterator) === "symbol" ? function (obj) {
    return typeof obj === "undefined" ? "undefined" : _typeof2(obj);
} : function (obj) {
    return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj === "undefined" ? "undefined" : _typeof2(obj);
};

var _B$State;

var optionChain = void 0,
    closest = void 0,
    currOptionChain = void 0,
    currClosest = void 0;
var opUnderlying = void 0,
    underlyingURL = void 0,
    optionChainType = void 0,
    identifier = void 0,
    index = void 0;
var indicesOptionChain = false,
    eventHandled = false;
var allOCData = void 0,
    allCurrOCData = void 0,
    allGsecOCData = void 0,
    allGoldMOCData = void 0,
    optionGsec = void 0,
    optionCurr = void 0,
    optionIRF = void 0;
var indices = ['NIFTY', 'FINNIFTY', 'BANKNIFTY', 'MIDCPNIFTY', 'NIFTYNXT50'];
var dataLoaded = [];
var equityType = 'equity',
    indicesType = 'indices',
    currencyType = 'currency',
    gsecType = 'irf',
    energyType = 'energy',
    goldmType = 'goldm';

var getQuotes = window.location.href.indexOf("get-quotes") !== -1;

var commodity_ltp = 0;
var OCTablePos = void 0;
var tabWid = void 0;

var updateVal = true;
var tableCont = void 0;
var OCTable = void 0;
var OCTableHead = void 0;
var OCNote = void 0;

var activeTab = void 0;

var optionsState = B.State((_B$State = {}, _B$State[equityType] = { currType: indicesType }, _B$State[indicesType] = { currType: indicesType }, _B$State[currencyType] = {}, _B$State[gsecType] = {}, _B$State[energyType] = {}, _B$State[goldmType] = {}, _B$State));
var commodityspotrates = void 0;
var selectedCommodities = void 0;
var getQuoteMetal = false;
var getQuoteEnergy = false;
var ensureURLAndType = function ensureURLAndType(_ref) {
    var symbol = _ref.symbol,
        identifier = _ref.identifier,
        type = _ref.type,
        contractList = _ref.contractList;
    var paramTypeSpEx = void 0,
        selectedExpiry = void 0,
        selectedStrike = void 0;
    if (_ref.contractList) {
        paramTypeSpEx = '&expiry=' + contractList.expiryDates[0];
        selectedExpiry = contractList.expiryDates[0] ? contractList.expiryDates[0] : '';
    } else if (_ref.expiry) {
        paramTypeSpEx = '&expiry=' + _ref.expiry;
        selectedExpiry = _ref.expiry ? _ref.expiry : '';
    } else if (_ref.strike) {
        paramTypeSpEx = '&strike=' + _ref.strike;
        selectedStrike = _ref.strike ? _ref.strike : '';
    }

    var symbolName = encodeURIComponent(symbol);
    if (symbolName === "undefined" && !identifier) {
        identifier = indices[0];
    }
    if (identifier && indices.includes(identifier) && type === 'indices') {
        opUnderlying = identifier;
        underlyingURL = '/api/option-chain-v3?type=Indices&symbol=' + encodeURIComponent(identifier) + paramTypeSpEx;
        optionChainType = type || indicesType;
        B.findOne('#underlying_index_label').innerText = 'Underlying Index : ';
    } else if (!getQuotes && type == currencyType) {
        opUnderlying = symbol;
        underlyingURL = '/api/option-chain-currency?symbol=' + encodeURIComponent(symbol);
        optionChainType = currencyType;
    } else if (type == gsecType) {
        opUnderlying = symbol;
        underlyingURL = '/api/option-chain-irf?symbol=' + encodeURIComponent(symbol);
        optionChainType = gsecType;
    } else if (type == goldmType || type == energyType) {
        opUnderlying = symbol;
        underlyingURL = '/api/option-chain-com?symbol=' + encodeURIComponent(symbol);
        optionChainType = goldmType;
    } else {
        opUnderlying = symbol;
        var toggle = document.getElementById("stream-optionchain-tile");
        if (paramTypeSpEx) {
            streamOptionChain(toggle.checked, symbol, selectedExpiry, selectedStrike);
        }
        underlyingURL = '/api/option-chain-v3?type=Equity&symbol=' + encodeURIComponent(symbolName) + paramTypeSpEx;;
        optionChainType = type || equityType;
        B.findOne('#underlying_index_label').innerText = 'Underlying Symbol : ';
    }
};
B.on(document, 'allGood', function () {

    var optionType = getParameterByName('type');
    if (window.location.href.indexOf('/commodity-getquote') === -1) {

        if (optionType === "currency" && $('#currencyChain').length) {
            $('#currencyChain').trigger('click');
        } else if (optionType === 'gsec') {
            $('#gsecChain').trigger('click');
        } else {
            initIndicesOptionChain();
        }
    }

    // For Option Chain Tab (#param url) default click
    if (window.location.href.indexOf('/option-chain') > 0 && $('#optChainCont').length) {
        var tabLinks = $('#optChainCont nav .nav-tabs .nav-link');
        tabLinks.each(function () {
            var linkHref = $(this).find('a').attr('href');
            if (window.location.href.indexOf(linkHref) > 0) {
                $(this).find('a').click();
            }
        });
    }
    /////////

    $('#optionContract select').change(function () {
        var selectedSymbol = $(this).val();
        if (selectedSymbol === "" || typeof selectedSymbol === "undefined" || selectedSymbol === null) {
            return false;
        }
        $('#select_symbol option').eq(0).prop('selected', 'selected');
        optionsState.equity.currType = indicesType;
        optionsState.indices.currType = indicesType;
        var contractList = void 0;
        B.get("/api/option-chain-contract-info?symbol=" + encodeURIComponent(selectedSymbol)).then(function (resp) {
            if (resp) {
                contractList = JSON.parse(resp);

                // Adding values to Expiry Date
                var $select = $('#expirySelect');
                $select.empty();
                $('<option value=""></option>').html('Select').appendTo($select);
                var expiryDates = contractList.expiryDates || [];
                for (var _iterator3 = expiryDates, _isArray3 = Array.isArray(_iterator3), _i3 = 0, _iterator3 = _isArray3 ? _iterator3 : _iterator3[Symbol.iterator]();;) {
                    var _ref4;

                    if (_isArray3) {
                        if (_i3 >= _iterator3.length) break;
                        _ref4 = _iterator3[_i3++];
                    } else {
                        _i3 = _iterator3.next();
                        if (_i3.done) break;
                        _ref4 = _i3.value;
                    }

                    var key = _ref4;

                    $('<option value="' + key + '"></option>').html(key).appendTo($select);
                }
                $select.find('option').eq(1).prop("selected", "selected");

                // Adding values to Strike Price
                var $select1 = $('#strikeSelect');
                $select1.empty();
                $('<option value=""></option>').html('Select').appendTo($select1);
                var strikePrices = contractList.strikePrice || [];
                for (var _iterator4 = strikePrices, _isArray4 = Array.isArray(_iterator4), _i4 = 0, _iterator4 = _isArray4 ? _iterator4 : _iterator4[Symbol.iterator]();;) {
                    var _ref5;

                    if (_isArray4) {
                        if (_i4 >= _iterator4.length) break;
                        _ref5 = _iterator4[_i4++];
                    } else {
                        _i4 = _iterator4.next();
                        if (_i4.done) break;
                        _ref5 = _i4.value;
                    }

                    var _key = _ref5;

                    var sanitizedKey = DecimalFixed(_key);
                    $('<option value="' + sanitizedKey + '"></option>').html(sanitizedKey).appendTo($select1);
                }

                return contractList;
            }
        }).then(function (contractList) {
            loadOptionChain({
                identifier: selectedSymbol,
                type: indicesType,
                tableID: '#equity_optionChainTable',
                underlyingValFieldID: '#equity_underlyingVal',
                timeStampFieldID: '#equity_timeStamp',
                totalRowFieldId: '#equityOptionChainTotalRow',
                expriySelectFieldId: '#expirySelect',
                strikeSelectFieldId: '#strikeSelect',
                expriyFilterFieldId: '#expiryDateFilter',
                strikeFilterFieldId: '#strikePriceFilter',
                contractList: contractList
            }, function () {
                //$('#expiryDateFilter').addClass('hide');
                $('#strikePriceFilter, #expiryDateFilter, #filterDivider').removeClass('hide').show();
                $('#expiryDateFilter select option:selected, #strikePriceFilter select option:selected').removeAttr("selected");
            });
        });
    });

    $('#expirySelectVal select').change(function () {
        var selectedExpiry = $('#expirySelect').val();
        var selectedIdentifier = $('#equity_optionchain_select').val();
        var selectedSymbol = $('#select_symbol').val();
        var toggle = document.getElementById("stream-optionchain-tile");
        var symbol = selectedIdentifier == undefined || selectedIdentifier === '' ? selectedSymbol : selectedIdentifier;
        if (selectedExpiry === "" || typeof selectedExpiry === "undefined" || selectedExpiry === null) {
            return false;
        }
        streamOptionChain(toggle.checked, symbol, selectedExpiry, '');
        $('#selectedExpiry option').eq(0).prop('selected', 'selected');
        optionsState.equity.currType = indicesType;
        optionsState.indices.currType = indicesType;
        loadOptionChain({
            symbol: selectedIdentifier == undefined || selectedIdentifier === '' ? selectedSymbol : selectedIdentifier,
            identifier: selectedIdentifier == undefined || selectedIdentifier === '' ? selectedSymbol : selectedIdentifier,
            type: indicesType,
            tableID: '#equity_optionChainTable',
            underlyingValFieldID: '#equity_underlyingVal',
            timeStampFieldID: '#equity_timeStamp',
            totalRowFieldId: '#equityOptionChainTotalRow',
            expriySelectFieldId: '#expirySelect',
            strikeSelectFieldId: '#strikeSelect',
            expriyFilterFieldId: '#expiryDateFilter',
            strikeFilterFieldId: '#strikePriceFilter',
            expiry: selectedExpiry,
            strike: ''
        }, function () {
            //$('#expiryDateFilter').addClass('hide');
            $("#strikePriceFilter select option[value=\"\"]").prop("selected", "selected");
            $('#strikePriceFilter, #expiryDateFilter, #filterDivider').removeClass('hide').show();
            $('#expiryDateFilter select option:selected, #strikePriceFilter select option:selected').removeAttr("selected");
        });
    });

    $('#strikeSelectVal select').change(function () {
        var selectedStrike = $('#strikeSelect').val();
        var selectedIdentifier = $('#equity_optionchain_select').val();
        var selectedSymbol = $('#select_symbol').val();
        var symbol = selectedIdentifier == undefined || selectedIdentifier === '' ? selectedSymbol : selectedIdentifier;
        var toggle = document.getElementById("stream-optionchain-tile");
        if (selectedStrike === "" || typeof selectedStrike === "undefined" || selectedStrike === null) {
            return false;
        }
        streamOptionChain(toggle.checked, symbol, '', selectedStrike);
        $('#selectedStrike option').eq(0).prop('selected', 'selected');
        optionsState.equity.currType = indicesType;
        optionsState.indices.currType = indicesType;
        loadOptionChain({
            symbol: selectedIdentifier == undefined || selectedIdentifier === '' ? selectedSymbol : selectedIdentifier,
            identifier: selectedIdentifier == undefined || selectedIdentifier === '' ? selectedSymbol : selectedIdentifier,
            type: indicesType,
            tableID: '#equity_optionChainTable',
            underlyingValFieldID: '#equity_underlyingVal',
            timeStampFieldID: '#equity_timeStamp',
            totalRowFieldId: '#equityOptionChainTotalRow',
            expriySelectFieldId: '#expirySelect',
            strikeSelectFieldId: '#strikeSelect',
            expriyFilterFieldId: '#expiryDateFilter',
            strikeFilterFieldId: '#strikePriceFilter',
            expiry: '',
            strike: selectedStrike
        }, function () {
            $("#expiryDateFilter select option[value=\"\"]").prop("selected", "selected");
            $('#strikePriceFilter, #expiryDateFilter, #filterDivider').removeClass('hide').show();
            $('#expiryDateFilter select option:selected, #strikePriceFilter select option:selected').removeAttr("selected");
        });
    });

    B.get("/api/master-quote").then(function (resp) {
        if (resp) {
            var jsonResp = JSON.parse(resp);
            if (jsonResp) {
                var $select1 = $('#select_symbol');
                $('<option value=""></option>').html('Select').appendTo($select1);
                jsonResp.forEach(function (elem) {
                    if (elem) {
                        $('<option value="' + elem + '"></option>').html(elem).appendTo($select1);
                    }
                });
            }
        }
    });

    $('#select_symbol').change(function () {
        try {
            var selectedVal = $(this).val();
            filterSymbolData(selectedVal, 'equity');
        } catch (e) {
            console.log(e);
        }
    });

    $('#symbolSearchGo').click(function () {
        // const selectedSymbol = companyAutoCompleteData.data('value');
        var selectedVal = $('#select_symbol').val();
        filterSymbolData(selectedVal);
    });

    $('#currencySelect').change(function () {
        try {
            var _optionCurr = $(this).val();
            loadOptionChain({
                symbol: _optionCurr,
                type: currencyType,
                tableID: '#optionChainCurrTable',
                underlyingValFieldID: '#refRate',
                timeStampFieldID: '#currOCTime',
                totalRowFieldId: '#optionChainCurrtotalRow',
                expriySelectFieldId: '#currExpirySelect',
                strikeSelectFieldId: '#currPriceSelect',
                expriyFilterFieldId: '#currExpirySelectFilter',
                strikeFilterFieldId: '#currPriceSelectFilter'
            }, function () {
                $('#currExpirySelectFilter, #currPriceSelectFilter, #filterCurrDivider').removeClass('hide').show();
                //$('#currPriceSelectFilter').addClass('hide');
                $('#currExpirySelectFilter select option:selected, #currPriceSelectFilter select option:selected').removeAttr("selected");
            });
        } catch (e) {
            console.log(e);
        }
    });

    $('#irfSelect').change(function () {
        try {
            var _optionIRF = $(this).val();
            loadOptionChain({
                symbol: _optionIRF,
                type: "irf",
                tableID: '#optionChainIrfTable',
                underlyingValFieldID: '#irfRate',
                timeStampFieldID: '#irfOCTime',
                totalRowFieldId: '#optionChainIrftotalRow',
                expriySelectFieldId: '#irfExpirySelect',
                strikeSelectFieldId: '#irfPriceSelect',
                expriyFilterFieldId: '#irfExpirySelectFilter',
                strikeFilterFieldId: '#irfPriceSelectFilter'
            }, function () {
                $('#irfExpirySelectFilter, #irfPriceSelectFilter, #filterIRFDivider').removeClass('hide').show();
                //$('#currPriceSelectFilter').addClass('hide');
                $('#irfExpirySelectFilter select option:selected, #irfPriceSelectFilter select option:selected').removeAttr("selected");
            });
        } catch (e) {
            console.log(e);
        }
    });

    $('#gsecSelect').change(function () {
        try {
            var _optionGsec = $(this).val();
            loadOptionChain({
                symbol: _optionGsec,
                type: gsecType,
                tableID: '#optionChainGsecTable',
                underlyingValFieldID: '#gsecRate',
                timeStampFieldID: '#gsecOCTime',
                totalRowFieldId: '#optionChainGsectotalRow',
                expriySelectFieldId: '#gsecExpirySelect',
                strikeSelectFieldId: '#gsecPriceSelect',
                expriyFilterFieldId: '#gsecExpirySelectFilter',
                strikeFilterFieldId: '#gsecPriceSelectFilter'
            }, function () {
                $('#gsecExpirySelectFilter, #gsecPriceSelectFilter, #filterGsecDivider').removeClass('hide').show();
                //$('#currPriceSelectFilter').addClass('hide');
                $('#gsecExpirySelectFilter select option:selected, #gsecPriceSelectFilter select option:selected').removeAttr("selected");
            });
        } catch (e) {
            console.log(e);
        }
    });

    $('#metalSelect').change(function () {
        try {
            // const optionGoldm = $(this).val();
            var selectedCommodity = $('#metalSelect option:selected').val();
            // selectedCommodity === 'GOLDM' ? 'GOLD' : 
            updateComRefRate(commodityspotrates, selectedCommodity, true, false);
            loadOptionChain({
                symbol: selectedCommodity,
                type: goldmType,
                tableID: '#optionChainMetalTable',
                underlyingValFieldID: '#metalRate',
                timeStampFieldID: '#metalOCTime',
                totalRowFieldId: '#optionChainMetaltotalRow',
                expriySelectFieldId: '#metalExpirySelect',
                strikeSelectFieldId: '#metalPriceSelect',
                expriyFilterFieldId: '#metalExpirySelectFilter',
                strikeFilterFieldId: '#metalPriceSelectFilter'
            }, function () {
                $('#metalExpirySelectFilter, #metalPriceSelectFilter, #filterMetalDivider').removeClass('hide').show();
                //$('#currPriceSelectFilter').addClass('hide');
                $('#metalExpirySelectFilter select option:selected, #metalPriceSelectFilter select option:selected').removeAttr("selected");
            });
        } catch (e) {
            console.log(e);
        }
    });

    $('#goldmSelect').change(function () {
        try {
            // const optionGoldm = $(this).val();
            var selectedCommodity = $('#goldmSelect option:selected').val();
            // selectedCommodity === 'GOLDM' ? 'GOLD' : 
            updateComRefRate(commodityspotrates, selectedCommodity, false);
            loadOptionChain({
                symbol: selectedCommodity,
                type: goldmType,
                tableID: '#optionChainGoldmTable',
                underlyingValFieldID: '#goldmRate',
                timeStampFieldID: '#goldmOCTime',
                totalRowFieldId: '#optionChainGoldmtotalRow',
                expriySelectFieldId: '#goldmExpirySelect',
                strikeSelectFieldId: '#goldmPriceSelect',
                expriyFilterFieldId: '#goldmExpirySelectFilter',
                strikeFilterFieldId: '#goldmPriceSelectFilter'
            }, function () {
                $('#goldmExpirySelectFilter, #goldmPriceSelectFilter, #filterGoldMDivider').removeClass('hide').show();
                //$('#currPriceSelectFilter').addClass('hide');
                $('#goldmExpirySelectFilter select option:selected, #goldmPriceSelectFilter select option:selected').removeAttr("selected");
            });
        } catch (e) {
            console.log(e);
        }
    });

    $('#energySelect').change(function () {
        try {
            // const optionGoldm = $(this).val();
            var selectedCommodity = $('#energySelect option:selected').val();
            // selectedCommodity === 'GOLDM' ? 'GOLD' : 
            updateComRefRate(commodityspotrates, selectedCommodity, false, true);
            loadOptionChain({
                symbol: selectedCommodity,
                type: energyType,
                tableID: '#optionChainEnergyTable',
                underlyingValFieldID: '#energyRate',
                timeStampFieldID: '#energyOCTime',
                totalRowFieldId: '#optionChainEnergytotalRow',
                expriySelectFieldId: '#energyExpirySelect',
                strikeSelectFieldId: '#energyPriceSelect',
                expriyFilterFieldId: '#energyExpirySelectFilter',
                strikeFilterFieldId: '#energyPriceSelectFilter'
            }, function () {
                $('#goldmExpirySelectFilter, #goldmPriceSelectFilter, #filterEnergyDivider').removeClass('hide').show();
                //$('#currPriceSelectFilter').addClass('hide');
                $('#goldmExpirySelectFilter select option:selected, #goldmPriceSelectFilter select option:selected').removeAttr("selected");
            });
        } catch (e) {
            console.log(e);
        }
    });

    if ($('.optionChainTable:visible').length > 0) {
        OCTablePos = $('.optionChainTable:visible').offset().top - ($('header').height() + $('#betaVerBand').height());
        tabWid = $('.optionChainTable:visible').width();
    }

    $('#modal_options_graph').on("hidden.bs.modal", function () {
        B.findOne("#gsecChartSelect").selectedIndex = 0;;
        B.findOne("#currencyChartSelect").selectedIndex = 0;;
        B.findOne("#equityChartSelect").selectedIndex = 0;
    });

    var table = document.getElementById("equity_optionChainTable");
    setTimeout(function () {
        table.style.minHeight = '0';
    }, 3000);
    $(document).on('click', '.terms_ofuse', function (e) {
        scrollToNote();
    });
});

function filterSymbolData(selectedSymbol) {
    try {
        if (typeof selectedSymbol === "undefined" || selectedSymbol === "" || $('#symbolSearch').val() === "") {
            alert("Please Select Symbol");
            return false;
        }
        $('#optionContract option').eq(0).prop('selected', 'selected');
        optionsState.equity.currType = equityType;
        optionsState.indices.currType = equityType;
        ensureURLAndType({ symbol: selectedSymbol });
        var sym = void 0,
            idn = void 0;
        if (indices.indexOf(selectedSymbol) !== -1) {
            idn = selectedSymbol.toUpperCase();
        } else {
            sym = selectedSymbol.toUpperCase();
        };
        var contractList = void 0;
        B.get("/api/option-chain-contract-info?symbol=" + encodeURIComponent(selectedSymbol)).then(function (resp) {
            if (resp) {
                contractList = JSON.parse(resp);

                // Adding values to Expiry Date
                var $select = $('#expirySelect');
                $select.empty();
                $('<option value=""></option>').html('Select').appendTo($select);
                var expiryDates = contractList.expiryDates || [];
                for (var _iterator3 = expiryDates, _isArray3 = Array.isArray(_iterator3), _i3 = 0, _iterator3 = _isArray3 ? _iterator3 : _iterator3[Symbol.iterator]();;) {
                    var _ref4;

                    if (_isArray3) {
                        if (_i3 >= _iterator3.length) break;
                        _ref4 = _iterator3[_i3++];
                    } else {
                        _i3 = _iterator3.next();
                        if (_i3.done) break;
                        _ref4 = _i3.value;
                    }

                    var key = _ref4;

                    $('<option value="' + key + '"></option>').html(key).appendTo($select);
                }
                $select.find('option').eq(1).prop("selected", "selected");

                // Adding values to Strike Price
                var $select1 = $('#strikeSelect');
                $select1.empty();
                $('<option value=""></option>').html('Select').appendTo($select1);
                var strikePrices = contractList.strikePrice || [];
                for (var _iterator4 = strikePrices, _isArray4 = Array.isArray(_iterator4), _i4 = 0, _iterator4 = _isArray4 ? _iterator4 : _iterator4[Symbol.iterator]();;) {
                    var _ref5;

                    if (_isArray4) {
                        if (_i4 >= _iterator4.length) break;
                        _ref5 = _iterator4[_i4++];
                    } else {
                        _i4 = _iterator4.next();
                        if (_i4.done) break;
                        _ref5 = _i4.value;
                    }

                    var _key = _ref5;

                    var sanitizedKey = DecimalFixed(_key);
                    $('<option value="' + sanitizedKey + '"></option>').html(sanitizedKey).appendTo($select1);
                }

                return contractList;
            }
        }).then(function (contractList) {
            loadOptionChain({
                type: equityType,
                symbol: sym,
                identifier: idn,
                tableID: '#equity_optionChainTable',
                underlyingValFieldID: '#equity_underlyingVal',
                timeStampFieldID: '#equity_timeStamp',
                totalRowFieldId: '#equityOptionChainTotalRow',
                expriySelectFieldId: '#expirySelect',
                strikeSelectFieldId: '#strikeSelect',
                expriyFilterFieldId: '#expiryDateFilter',
                strikeFilterFieldId: '#strikePriceFilter',
                contractList: contractList
            });
        });
    } catch (e) {
        console.log(e);
    }
}

function initIndicesOptionChain() {
    activeTab = "equity";
    if (indicesOptionChain || getQuotes) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#equity_optionChainTable');
        OCTable = $('#optionChainTable-indices');
        OCTableHead = $('#optionChainTable-indices thead');
        OCNote = $('#EqNote');
        /* End */
        return;
    } else {
        indicesOptionChain = true;
        loadIndicesOptionChain();
    }
}

function loadIndicesOptionChain() {
    if (dataLoaded.indexOf('indices-option-chain') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#equity_optionChainTable');
        OCTable = $('#optionChainTable-indices');
        OCTableHead = $('#optionChainTable-indices thead');
        OCNote = $('#EqNote');
        /* End */
        return;
    } else {
        dataLoaded.push('indices-option-chain');
        var contractList = void 0;
        B.get("/api/option-chain-contract-info?symbol=" + $('#equity_optionchain_select').val()).then(function (resp) {
            if (resp) {
                contractList = JSON.parse(resp);

                // Adding values to Expiry Date
                var $select = $('#expirySelect');
                $select.empty();
                $('<option value=""></option>').html('Select').appendTo($select);
                var expiryDates = contractList.expiryDates || [];
                for (var _iterator3 = expiryDates, _isArray3 = Array.isArray(_iterator3), _i3 = 0, _iterator3 = _isArray3 ? _iterator3 : _iterator3[Symbol.iterator]();;) {
                    var _ref4;

                    if (_isArray3) {
                        if (_i3 >= _iterator3.length) break;
                        _ref4 = _iterator3[_i3++];
                    } else {
                        _i3 = _iterator3.next();
                        if (_i3.done) break;
                        _ref4 = _i3.value;
                    }

                    var key = _ref4;

                    $('<option value="' + key + '"></option>').html(key).appendTo($select);
                }
                $select.find('option').eq(1).prop("selected", "selected");

                // Adding values to Strike Price
                var $select1 = $('#strikeSelect');
                $select1.empty();
                $('<option value=""></option>').html('Select').appendTo($select1);
                var strikePrices = contractList.strikePrice || [];
                for (var _iterator4 = strikePrices, _isArray4 = Array.isArray(_iterator4), _i4 = 0, _iterator4 = _isArray4 ? _iterator4 : _iterator4[Symbol.iterator]();;) {
                    var _ref5;

                    if (_isArray4) {
                        if (_i4 >= _iterator4.length) break;
                        _ref5 = _iterator4[_i4++];
                    } else {
                        _i4 = _iterator4.next();
                        if (_i4.done) break;
                        _ref5 = _i4.value;
                    }

                    var _key = _ref5;

                    var sanitizedKey = DecimalFixed(_key);
                    $('<option value="' + sanitizedKey + '"></option>').html(sanitizedKey).appendTo($select1);
                }

                return contractList;
            }
        }).then(function (contractList) {
            loadOptionChain({
                identifier: $('#equity_optionchain_select').val(),
                type: 'indices',
                tableID: '#equity_optionChainTable',
                underlyingValFieldID: '#equity_underlyingVal',
                timeStampFieldID: '#equity_timeStamp',
                totalRowFieldId: '#equityOptionChainTotalRow',
                expriySelectFieldId: '#expirySelect',
                strikeSelectFieldId: '#strikeSelect',
                expriyFilterFieldId: '#expiryDateFilter',
                strikeFilterFieldId: '#strikePriceFilter',
                contractList: contractList
            });
        });
    }
}

function loadCurrecnyOptionChain() {
    activeTab = "currency";
    if (dataLoaded.indexOf('all-cd-symbols') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#optionChainCurrTable');
        OCTable = $('#optionChainTable-currency');
        OCTableHead = $('#optionChainTable-currency thead');
        OCNote = $('#CurrNote');
        /* End */
        return;
    } else {
        dataLoaded.push('all-cd-symbols');
        B.get('/api/all-cd-symbols').then(function (resp) {
            var respJSON = JSON.parse(resp);
            var $select1 = $('#currencySelect');
            for (var key in respJSON) {
                if (!key.includes('MIBOR')) {
                    $('<option value="' + key + '"></option>').html(respJSON[key]).appendTo($select1);
                }
            }
            loadOptionChain({
                symbol: Object.keys(respJSON)[0],
                type: 'currency',
                tableID: '#optionChainCurrTable',
                underlyingValFieldID: '#refRate',
                timeStampFieldID: '#currOCTime',
                totalRowFieldId: '#optionChainCurrtotalRow',
                expriySelectFieldId: '#currExpirySelect',
                strikeSelectFieldId: '#currPriceSelect',
                expriyFilterFieldId: '#currExpirySelectFilter',
                strikeFilterFieldId: '#currPriceSelectFilter'
            });
            if (optionCurr) {
                $('#currencySelect option[value="' + optionCurr + '"]').attr("selected", "selected");
            }
        });
    }
}

function loadIRFOptionChain() {
    if (dataLoaded.indexOf('all-irf-symbols') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#optionChainIrfTable');
        OCTable = $('#optionChainTable-irf');
        OCTableHead = $('#optionChainTable-irf thead');
        OCNote = $('#CurrNote');
        /* End */
        return;
    } else {
        dataLoaded.push('all-irf-symbols');
        B.get('/api/irf-option-contracts').then(function (resp) {
            var respJSON = JSON.parse(resp);
            var $select1 = $('#irfSelect');
            for (var _iterator = respJSON, _isArray = Array.isArray(_iterator), _i = 0, _iterator = _isArray ? _iterator : _iterator[Symbol.iterator]();;) {
                var _ref2;

                if (_isArray) {
                    if (_i >= _iterator.length) break;
                    _ref2 = _iterator[_i++];
                } else {
                    _i = _iterator.next();
                    if (_i.done) break;
                    _ref2 = _i.value;
                }

                var key = _ref2;

                $('<option value="' + key + '"></option>').html(key).appendTo($select1);
            }
            loadOptionChain({
                symbol: respJSON[0],
                type: "irf",
                tableID: '#optionChainIrfTable',
                underlyingValFieldID: '#irfRate',
                timeStampFieldID: '#irfOCTime',
                totalRowFieldId: '#optionChainIrftotalRow',
                expriySelectFieldId: '#irfExpirySelect',
                strikeSelectFieldId: '#irfPriceSelect',
                expriyFilterFieldId: '#irfExpirySelectFilter',
                strikeFilterFieldId: '#irfPriceSelectFilter'
            });
            if (optionIRF) {
                $('#irfSelect option[value="' + optionIRF + '"]').attr("selected", "selected");
            }
        });
    }
}

function loadGsecOptionChain() {
    activeTab = "interestRates";
    if (dataLoaded.indexOf('all-gsec-symbols') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#optionChainGsecTable');
        OCTable = $('#optionChainTable-gsec');
        OCTableHead = $('#optionChainTable-gsec thead');
        OCNote = $('#gsecNote');
        /* End */
        return;
    } else {
        dataLoaded.push('all-gsec-symbols');
        B.get('/api/irf-option-contracts').then(function (resp) {
            var respJSON = JSON.parse(resp);
            var $select1 = $('#gsecSelect');
            for (var _iterator2 = respJSON, _isArray2 = Array.isArray(_iterator2), _i2 = 0, _iterator2 = _isArray2 ? _iterator2 : _iterator2[Symbol.iterator]();;) {
                var _ref3;

                if (_isArray2) {
                    if (_i2 >= _iterator2.length) break;
                    _ref3 = _iterator2[_i2++];
                } else {
                    _i2 = _iterator2.next();
                    if (_i2.done) break;
                    _ref3 = _i2.value;
                }

                var key = _ref3;

                $('<option value="' + key + '"></option>').html(key).appendTo($select1);
            }
            loadOptionChain({
                symbol: respJSON[0],
                type: gsecType,
                tableID: '#optionChainGsecTable',
                underlyingValFieldID: '#gsecRate',
                timeStampFieldID: '#gsecOCTime',
                totalRowFieldId: '#optionChainGsectotalRow',
                expriySelectFieldId: '#gsecExpirySelect',
                strikeSelectFieldId: '#gsecPriceSelect',
                expriyFilterFieldId: '#gsecExpirySelectFilter',
                strikeFilterFieldId: '#gsecPriceSelectFilter'
            });
            if (optionGsec) {
                $('#gsecSelect option[value="' + optionGsec + '"]').attr("selected", "selected");
            }
        });
    }
}

function loadGoldMOptionChain() {
    activeTab = "commodities";
    if (dataLoaded.indexOf('all-goldm-symbols') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#optionChainGoldmTable');
        OCTable = $('#optionChainTable-goldm');
        OCTableHead = $('#optionChainTable-goldm thead');
        OCNote = $('#goldmNote');
        /* End */
        return;
    } else {
        dataLoaded.push('all-goldm-symbols');
        var selectedCommodity = $('#goldmSelect option:selected').val();
        B.get("/api/quotes-commodity-derivatives-master").then(function (resp) {
            if (resp) {
                var jsonResp = JSON.parse(resp);
                if (jsonResp) {

                    var fixedOrder = ['CRUDEOIL', 'NATURALGAS', 'SILVER', 'GOLD', 'COPPER', 'GOLDM', 'SILVERM', 'SILVER100', 'ZINC'];
                    var keysToAdd = new Set();

                    var $select1 = $('#goldmSelect');
                    for (var _iterator5 = Object.entries(jsonResp), _isArray5 = Array.isArray(_iterator5), _i6 = 0, _iterator5 = _isArray5 ? _iterator5 : _iterator5[Symbol.iterator]();;) {
                        var _ref6;

                        if (_isArray5) {
                            if (_i6 >= _iterator5.length) break;
                            _ref6 = _iterator5[_i6++];
                        } else {
                            _i6 = _iterator5.next();
                            if (_i6.done) break;
                            _ref6 = _i6.value;
                        }

                        var _ref7 = _ref6,
                            key = _ref7[0],
                            value = _ref7[1];

                        for (var _iterator6 = value, _isArray6 = Array.isArray(_iterator6), _i7 = 0, _iterator6 = _isArray6 ? _iterator6 : _iterator6[Symbol.iterator]();;) {
                            var _ref8;

                            if (_isArray6) {
                                if (_i7 >= _iterator6.length) break;
                                _ref8 = _iterator6[_i7++];
                            } else {
                                _i7 = _iterator6.next();
                                if (_i7.done) break;
                                _ref8 = _i7.value;
                            }

                            var item = _ref8;

                            if (item.instrumentType && item.instrumentType.substring(0, 3).toLowerCase() === 'opt') {
                                // $('<option value="' + key + '"></option>').html(key).appendTo($select1);
                                keysToAdd.add(key);
                            }
                        }
                    }
                    // Append options in fixed order
                    fixedOrder.forEach(function (key) {
                        if (keysToAdd.has(key)) {
                            $('<option value="' + key + '"></option>').html(key).appendTo($select1);
                        }
                    });
                    selectedCommodity = $('#goldmSelect option:selected').val();
                    selectedCommodities = selectedCommodity;
                    if (commodityspotrates) {
                        // selectedCommodity === 'GOLDM' ? 'GOLD' :
                        updateComRefRate(commodityspotrates, selectedCommodity, false, false);
                    }
                }
            }
        }).then(function (val) {
            loadOptionChain({
                symbol: selectedCommodity ? selectedCommodity : 'CRUDEOIL',
                type: goldmType,
                tableID: '#optionChainGoldmTable',
                underlyingValFieldID: '#goldmRate',
                timeStampFieldID: '#goldmOCTime',
                totalRowFieldId: '#optionChainGoldmtotalRow',
                expriySelectFieldId: '#goldmExpirySelect',
                strikeSelectFieldId: '#goldmPriceSelect',
                expriyFilterFieldId: '#goldmExpirySelectFilter',
                strikeFilterFieldId: '#goldmPriceSelectFilter'
            });
        });
        // B.get('/api/irf-option-contracts').then((resp) => {
        //     let respJSON = JSON.parse(resp);
        //     let $select1 = $('#goldmSelect');
        //     for (let key of respJSON) {
        //         $('<option value="' + key + '"></option>').html(key).appendTo($select1);
        //     }

        //     if (optionGsec) {
        //         $('#goldmSelect option[value="' + optionGsec + '"]').attr("selected", "selected");
        //     }
        // });
    }
}

function loadEnergyOptionChain() {
    activeTab = "commodities";
    if (dataLoaded.indexOf('all-energy-symbols') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#optionChainEnergyTable');
        OCTable = $('#optionChainTable-energy');
        OCTableHead = $('#optionChainTable-energy thead');
        OCNote = $('#energyNote');
        /* End */
        return;
    } else {
        dataLoaded.push('all-energy-symbols');
        getQuoteEnergy = true;
        var selectedCommodity = $('#energySelect option:selected').val();
        loadOptionChain({
            symbol: selectedCommodity,
            type: energyType,
            tableID: '#optionChainEnergyTable',
            underlyingValFieldID: '#energyRate',
            timeStampFieldID: '#energyOCTime',
            totalRowFieldId: '#optionChainEnergytotalRow',
            expriySelectFieldId: '#energyExpirySelect',
            strikeSelectFieldId: '#energyPriceSelect',
            expriyFilterFieldId: '#energyExpirySelectFilter',
            strikeFilterFieldId: '#energyPriceSelectFilter'
        });
        // B.get('/api/irf-option-contracts').then((resp) => {
        //     let respJSON = JSON.parse(resp);
        //     let $select1 = $('#energySelect');
        //     for (let key of respJSON) {
        //         $('<option value="' + key + '"></option>').html(key).appendTo($select1);
        //     }

        //     if (optionGsec) {
        //         $('#energySelect option[value="' + optionGsec + '"]').attr("selected", "selected");
        //     }
        // });
    }
}

function loadMetalOptionChain() {
    activeTab = "commodities";
    if (dataLoaded.indexOf('all-goldm-symbols') !== -1) {
        /* For Header Fix Header */
        updateVal = true;
        tableCont = $('#optionChainMetalTable');
        OCTable = $('#optionChainTable-metal');
        OCTableHead = $('#optionChainTable-metal thead');
        OCNote = $('#metalNote');
        /* End */
        return;
    } else {
        dataLoaded.push('all-goldm-symbols');
        selectedCommodities = $('#metalSelect option:selected').val();
        getQuoteMetal = true;
        if (commodityspotrates) {
            updateComRefRate(commodityspotrates, selectedCommodities, true);
        }
        loadOptionChain({
            symbol: selectedCommodities,
            type: goldmType,
            tableID: '#optionChainMetalTable',
            underlyingValFieldID: '#metalRate',
            timeStampFieldID: '#metalOCTime',
            totalRowFieldId: '#optionChainMetaltotalRow',
            expriySelectFieldId: '#metalExpirySelect',
            strikeSelectFieldId: '#metalPriceSelect',
            expriyFilterFieldId: '#metalExpirySelectFilter',
            strikeFilterFieldId: '#metalPriceSelectFilter'
        });
    }
}

function getSanitizedSP(type, sp) {
    return [gsecType, currencyType].includes(type) ? CurrDecimalFixed(sp) : DecimalFixed(sp);
}

function loadOptionChain(params, callback) {
    try {
        $(params.tableID).empty(); // clear the table first.
        var optionChainJson = '/json/option-chain/option-chain.json';
        if (params.type === 'indices' || params.type === 'equity') {
            optionChainJson = '/json/option-chain/option-chain-v2.json';
        }
        B.get(optionChainJson).then(function (resp) {
            var respJSONObj = JSON.parse(resp);
            if (params.type === gsecType) {
                respJSONObj.columns = respJSONObj.columns.filter(function (e) {
                    return e.heading !== 'IV';
                });
            }
            if (params.type === goldmType || params.type === energyType) {
                respJSONObj.columns = respJSONObj.columns.filter(function (e) {
                    return e.name !== 'chart';
                });
            }
            if (params.type === 'indices' || params.type === 'equity') {
                if (params.strike) {
                    var indexResp = respJSONObj.columns.findIndex(function (c) {
                        return c.name === "strikePrice";
                    });
                    if (indexResp !== -1) {
                        respJSONObj.columns[indexResp] = {
                            name: "expiryDates",
                            heading: "Expiry Date",
                            subHead: "",
                            width: "6.34%",
                            sort: false,
                            chkVal: false,
                            optionType: ""
                        };
                    }
                }
            }
            ensureURLAndType(params);
            optionChain = CustomTableOptionChain({ tableStyle: { id: 'optionChainTable-' + optionChainType, class: "common_table w-100" }, type: optionChainType, symbol: opUnderlying, ltp: "", colData: respJSONObj.columns || [], rowData: [] });
            B.render(optionChain, B.findOne(params.tableID));
            if (B.findOne('#optionChainTable-' + optionChainType + ' .emptyRow')) {
                B.findOne('#optionChainTable-' + optionChainType + ' .emptyRow').innerHTML = loader;
            }
            if (params.queryParams) {
                underlyingURL = '' + underlyingURL + params.queryParams;
            }

            /* For Header Fix Header */
            updateVal = true;
            tableCont = $(params.tableID);
            OCTable = $('#optionChainTable-indices');
            OCTableHead = $('#optionChainTable-indices thead');

            if (params.type == currencyType) {
                OCNote = $('#CurrNote');
            } else if (params.type == gsecType) {
                OCNote = $('#gsecNote');
            } else {
                OCNote = $('#EqNote');
            }
            if (params.type === goldmType || params.type === energyType) {
                if (!commodityspotrates) {
                    B.get('/api/refrates?index=commodityspotrates').then(function (respRefrates) {
                        var respJSON = JSON.parse(respRefrates);
                        commodityspotrates = respJSON.data || [];

                        if (selectedCommodities) {
                            if (getQuoteMetal) {
                                updateComRefRate(commodityspotrates, selectedCommodities, true, false);
                            } else if (getQuoteEnergy) {
                                updateComRefRate(commodityspotrates, selectedCommodities, false, true);
                            } else {
                                updateComRefRate(commodityspotrates, selectedCommodities, false, false);
                            }
                        }
                    });
                }
            }

            /* End */
            B.get(underlyingURL).then(function (resp) {
                var respJSON = JSON.parse(resp);
                if (Object.keys(respJSON).length === 0) {
                    respJSON = [];
                }
                optionsState[params.type].filteredData = respJSON.length > 0 && respJSON.records && respJSON.records.data;
                optionsState[params.type].total = { "CE": respJSON.CE, "PE": respJSON.PE };
                optionsState[params.type].type = "date";
                optionsState[params.type].currType = params.type;

                var ocs = respJSON.filtered || [];
                var allOcs = respJSON.records || [];
                if (params.type == currencyType) {
                    allCurrOCData = allOcs.data;
                } else if (params.type == gsecType) {
                    allGsecOCData = allOcs.data;
                } else if (params.type == goldmType) {
                    allGoldMOCData = allOcs.data;
                } else {
                    allOCData = allOcs.data;
                }
                var last = allOcs.underlyingValue || 0;

                closest = allOcs.strikePrices && allOcs.strikePrices.reduce(function (prev, curr) {
                    return Math.abs(curr - last) < Math.abs(prev - last) ? curr : prev;
                });

                var totalRowFieldId = params.totalRowFieldId.replace('#', '');
                if (activeTab === "commodities") {
                    optionChain.state.ltp = commodity_ltp;
                } else {
                    optionChain.state.ltp = closest;
                }
                optionChain.state.rowData = ocs.data || [];
                optionChain.state.allData = allOcs.data || [];
                optionChain.state.totalRowFieldId = totalRowFieldId;
                optionChain.state.expriyFilterFieldId = params.expriyFilterFieldId;
                optionChain.state.strikeFilterFieldId = params.strikeFilterFieldId;
                last = last ? DecimalFixed(last) : '-';
                if (params.type === currencyType) {
                    B.findOne('#refRateTime').innerText = respJSON && respJSON.refrate && respJSON.refrate.time ? respJSON.refrate.time : '-';
                    last = CurrDecimalFixed(last);
                    B.findOne(params.underlyingValFieldID).innerText = opUnderlying + " " + last;
                } else if (params.type === gsecType) {
                    last = CurrDecimalFixed(last);
                    if (B.findOne('#irfRefRateTime')) B.findOne('#irfRefRateTime').innerText = allOcs.timestamp;
                    B.findOne('#gsec_underlyingVal').innerText = opUnderlying + " " + last || '';
                } else if (params.type === goldmType) {
                    var selectedCommodity = $('#goldmSelect option:selected').val();
                    if (selectedCommodity) {
                        // selectedCommodity === 'GOLDM' ? 'GOLD' :
                        updateComRefRate(commodityspotrates, selectedCommodity, false, false);
                    }
                } else if (params.type === energyType) {
                    var selectedCommodity = $('#energySelect option:selected').val();
                    if (selectedCommodity) {
                        // selectedCommodity === 'GOLDM' ? 'GOLD' :
                        updateComRefRate(commodityspotrates, selectedCommodity, false, true);
                    }
                } else {
                    B.findOne(params.underlyingValFieldID).innerText = opUnderlying + " " + last;
                }
                B.findOne(params.timeStampFieldID).innerHTML = _typeof(allOcs.timestamp) ? "<span id=\"asontxt\">As on </span> <span>" + allOcs.timestamp + " IST </span>" : "";

                if (!(params.type === 'indices' || params.type === 'equity')) {
                    var $select = $(params.expriySelectFieldId);
                    $select.empty();
                    $('<option value=""></option>').html('Select').appendTo($select);
                    var expiryDates = allOcs.expiryDates || [];
                    for (var _iterator3 = expiryDates, _isArray3 = Array.isArray(_iterator3), _i3 = 0, _iterator3 = _isArray3 ? _iterator3 : _iterator3[Symbol.iterator]();;) {
                        var _ref4;

                        if (_isArray3) {
                            if (_i3 >= _iterator3.length) break;
                            _ref4 = _iterator3[_i3++];
                        } else {
                            _i3 = _iterator3.next();
                            if (_i3.done) break;
                            _ref4 = _i3.value;
                        }

                        var key = _ref4;

                        $('<option value="' + key + '"></option>').html(key).appendTo($select);
                    }
                    $select.find('option').eq(1).prop("selected", "selected");

                    var $select1 = $(params.strikeSelectFieldId);
                    $select1.empty();
                    $('<option value=""></option>').html('Select').appendTo($select1);
                    var strikePrices = allOcs.strikePrices || [];
                    for (var _iterator4 = strikePrices, _isArray4 = Array.isArray(_iterator4), _i4 = 0, _iterator4 = _isArray4 ? _iterator4 : _iterator4[Symbol.iterator]();;) {
                        var _ref5;

                        if (_isArray4) {
                            if (_i4 >= _iterator4.length) break;
                            _ref5 = _iterator4[_i4++];
                        } else {
                            _i4 = _iterator4.next();
                            if (_i4.done) break;
                            _ref5 = _i4.value;
                        }

                        var _key = _ref5;

                        var sanitizedKey = [gsecType, currencyType].includes(params.type) ? CurrDecimalFixed(_key) : DecimalFixed(_key);
                        $('<option value="' + sanitizedKey + '"></option>').html(sanitizedKey).appendTo($select1);
                    }
                }

                var getAllData = function getAllData(type) {
                    var data = void 0;
                    switch (params.type) {
                        case currencyType:
                            data = allCurrOCData;
                            break;
                        case gsecType:
                            data = allGsecOCData;
                            break;
                        case goldmType:
                            data = allGoldMOCData;
                            break;
                        default:
                            data = allOCData;
                    }
                    return data;
                };
                if (!$._data($(params.expriyFilterFieldId + ' select')[0], 'events') || !$._data($(params.expriyFilterFieldId + ' select')[0], 'events').change) {
                    $(params.expriyFilterFieldId + ' select').on('change', function () {
                        var expiryDate = $(this).val();
                        if (expiryDate !== "") {
                            if (params.type === 'indices' || params.type === 'equity') {
                                // updateDataByExpiryDate(params.identifier,expiryDate, params.type);
                            } else {
                                optionChain.updateByDate(getAllData(params.type), expiryDate, params.type);
                            }
                        }
                    });
                }

                if (!$._data($(params.strikeFilterFieldId + ' select')[0], 'events') || !$._data($(params.strikeFilterFieldId + ' select')[0], 'events').change) {
                    $(params.strikeFilterFieldId + ' select').on('change', function () {
                        var strikePrice = $(this).val();
                        if (strikePrice !== "") {
                            if (params.type === 'indices' || params.type === 'equity') {
                                // updateDataByExpiryDate(params.identifier,expiryDate, params.type);
                            } else {
                                optionChain.updateBySP(getAllData(params.type), strikePrice, params.type);
                            }
                        }
                    });
                }

                var tableRowField = B.findOne(params.totalRowFieldId);
                if (tableRowField) {
                    tableRowField.remove();
                }
                /* Total Row Table */
                var totalTd = optionChain.state.colData.map(function (item, index) {
                    var className = "";
                    if (item.format === "number") {
                        className = "text-right";
                    }
                    if (index === 0 && params.type !== "goldm") {
                        return td({ "width": item.width, id: "total" }, "Total");
                    }
                    if (item.name === "openInterest" && item.optionType === "CE") {
                        return td({ id: totalRowFieldId + '-CE-totOI', "width": item.width, class: className }, ocs.CE && ocs.CE.totOI && DecimalFixed(ocs.CE.totOI, true).toString());
                    } else if (item.name === "totalTradedVolume" && item.optionType === "CE") {
                        return td({ id: totalRowFieldId + '-CE-totVol', "width": item.width, class: className }, ocs.CE && ocs.CE.totVol && DecimalFixed(ocs.CE.totVol, true).toString());
                    } else if (item.name === "totalTradedVolume" && item.optionType === "PE") {
                        return td({ id: totalRowFieldId + '-PE-totVol', "width": item.width, class: className }, ocs.PE && ocs.PE.totVol && DecimalFixed(ocs.PE.totVol, true).toString());
                    } else if (item.name === "openInterest" && item.optionType === "PE") {
                        return td({ id: totalRowFieldId + '-PE-totOI', "width": item.width, class: className }, ocs.PE && ocs.PE.totOI && DecimalFixed(ocs.PE.totOI, true).toString());
                    } else {
                        return td({ "width": item.width }, "");
                    }
                });
                if (callback) {
                    callback();
                }
                BlinkUI.render(table({ id: totalRowFieldId, class: "common_table w-100" }, tbody({}, tr(totalTd))), B.findOne(params.tableID));

                // B.findOne(params.totalRowFieldId+" .emptyRow").innerHTML = loader;

                /* End */

                OCTablePos = $('.optionChainTable:visible').offset().top - ($('header').height() + $('#betaVerBand').height());
                tabWid = $('.optionChainTable:visible').width();
            });
        });
    } catch (error) {
        console.log('loadOptionChain::error:: ', error);
    }
};
var seriesOptions = void 0,
    seriesCounter = void 0,
    OCChart = void 0;
function genChainGraph(CEIdenty, PEIdenty, sp, ed, underlying) {
    try {
        if (OCChart) {
            OCChart.destroy();
        }
        $('#chartIdentifer').text(underlying);
        $('#chartStrikePrice').text(DecimalFixed(sp));
        $('#chartExpDate').text(ed);
        B.findOne("#optionChainGraph").innerHTML = loader;
        seriesOptions = [], seriesCounter = 0;
        var graphIdentifer = [CEIdenty, PEIdenty];

        $.each(graphIdentifer, function (i, identity) {
            if (identity === "undefined") {
                seriesOptions[i] = {
                    name: '',
                    data: []
                };

                // As we're loading the data asynchronously, we don't know what order it will arrive. So
                // we keep a counter and create the chart when all the data is loaded.
                seriesCounter += 1;

                if (seriesCounter === graphIdentifer.length) {
                    B.findOne("#optionChainGraph").innerHTML = "";
                    createChart();
                }

                var graphTxt = ' Intraday price chart of ' + underlying + ' ' + sp + ' ' + ed + ' Call vs Put Contract. The extended description is in the view data table option of the chart menu.';
                setTimeout(function () {
                    $('#optionChainGraph').attr({ "role": 'img', "aria-label": graphTxt });
                }, 2000);
            } else {
                B.get('/api/chart-databyindex?index=' + encodeURIComponent(identity)).then(function (resp) {
                    var respJSONObj = JSON.parse(resp);
                    seriesOptions[i] = {
                        name: respJSONObj.name,
                        data: respJSONObj.grapthData || []
                    };

                    // As we're loading the data asynchronously, we don't know what order it will arrive. So
                    // we keep a counter and create the chart when all the data is loaded.
                    seriesCounter += 1;

                    if (seriesCounter === graphIdentifer.length) {
                        B.findOne("#optionChainGraph").innerHTML = "";
                        createChart();
                    }

                    var graphTxt = ' Intraday price chart of ' + underlying + ' ' + sp + ' ' + ed + ' Call vs Put Contract. The extended description is in the view data table option of the chart menu.';
                    setTimeout(function () {
                        $('#optionChainGraph').attr({ "role": 'img', "aria-label": graphTxt });
                    }, 2000);
                });
            }
        });
    } catch (e) {
        console.log("genChainGraph error - option-chain.js :", e.message);
    }
}

function createChart() {
    try {
        OCChart = Highcharts.stockChart('optionChainGraph', {
            rangeSelector: {
                enabled: false,
                selected: 2,
                inputEnabled: false
            },
            credits: {
                enabled: false
            },
            navigator: {
                enabled: false
            },
            scrollbar: {
                enabled: false
            },
            yAxis: {
                opposite: false,
                plotLines: [{
                    value: 0,
                    width: 2,
                    color: 'silver'
                }]
            },
            plotOptions: {
                series: {
                    compare: 'percent',
                    showInNavigator: true
                }
            },
            exporting: {
                enabled: true
            },
            tooltip: {
                pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
                valueDecimals: 2,
                split: true
            },
            series: seriesOptions
        });
    } catch (err) {
        console.log('err', err);
        B.findOne("#optionChainGraph").innerHTML = "No Data";
    }
}
function redirectFutureCon(type, selector) {
    try {
        var chainVal = $(selector).find('option:selected').val();
        switch (type) {
            case "equity":
                var select_symbol = $("#select_symbol").find('option:selected').val();
                if (select_symbol && select_symbol !== "") {
                    window.location.href = '/get-quotes/derivatives?symbol=' + encodeURIComponent(select_symbol) + '&instrument=' + encodeURIComponent('Stock Futures');
                } else {
                    window.location.href = "/market-data/equity-derivatives-watch?name=" + chainVal;
                }
                break;
            case "currency":
                window.location.href = "/market-data/currency-derivatives?symbol=" + chainVal;
                break;
            case "irf":
                window.location.href = '/market-data/bond-market-futures?symbol=' + chainVal;
                break;
            case "goldm":
                window.location.href = '/market-data/commodity-derivatives';
                break;
        }
    } catch (e) {
        console.log(e);
    }
}
function optionChainFullScreen() {
    try {
        $('body').addClass('plainTemplate');
        //$('header, footer, .setting_btn, .feedbackIconBtn, #quickLinkBtn, .footer_strip, .fullViewBtn, #tabs nav').addClass('hide');
        $('header, footer, .setting_btn, .feedbackIconBtn, .loginIconBtn, #quickLinkBtn, .footer_strip, .fullViewBtn, #tabs nav,#betaVerBand').addClass('hide');
        $('#optChainCont').addClass('optionChainApp');
        $('#headerContainer').removeClass('hide');
        // $marketSlider.slick('unslick');
        OCTablePos = tableCont.offset().top - ($('#headerContainer').height() + ($('#betaVerBand').height() || 0));
        tabWid = tableCont.width();
    } catch (e) {
        console.log(e);
    }
}
function optionChainExitFullScreen() {
    try {
        $('body').removeClass('plainTemplate');
        // $('header, footer, .setting_btn, .feedbackIconBtn, #quickLinkBtn, .footer_strip, .fullViewBtn, #tabs nav').removeClass('hide');
        $('header, footer, .setting_btn, .feedbackIconBtn, .loginIconBtn, #quickLinkBtn, .footer_strip, .fullViewBtn, #tabs nav,#betaVerBand').removeClass('hide');
        $('#optChainCont').removeClass('optionChainApp');
        $('#headerContainer').addClass('hide');
        // marketStatusSlick();
        OCTablePos = tableCont.offset().top - ($('header').height() + ($('#betaVerBand').height() || 0));
        tabWid = tableCont.width();
    } catch (e) {
        console.log(e);
    }
}

function OCHeaderFix(posTop) {
    try {
        if ($(window).width() > 1024 && tableCont) {
            //let OCTableEndPos = $('footer').offset().top - OCTablePos - 40;
            var OCTableEndPos = OCTablePos + tableCont.height() - 40;
            if (OCTableEndPos <= 0) {
                OCTableEndPos = OCNote.offset().top;
            }

            var tableId = void 0;
            var tableHead = void 0;

            switch (activeTab) {
                case "currency":
                    tableId = $('#optionChainTable-currency');
                    tableHead = $('#optionChainTable-currency thead');
                    break;
                case "interestRates":
                    tableId = $('#optionChainTable-irf');
                    tableHead = $('#optionChainTable-irf thead');
                    break;
                case "commodities":
                    tableId = $('#optionChainTable-goldm');
                    tableHead = $('#optionChainTable-goldm thead');
                    break;
            }

            if (posTop > OCTablePos && posTop < OCTableEndPos && updateVal) {
                setTimeout(function () {
                    var headerHeight = $('body').hasClass('plainTemplate') ? $('#headerContainer').height() : $('header').height();
                    if (tableId && tableHead && tableId !== "" && tableHead !== "") {
                        tableId.addClass('fixHeader');
                        tableHead.css({ top: headerHeight, width: tabWid });
                    } else {
                        OCTable.addClass('fixHeader');
                        OCTableHead.css({ top: headerHeight, width: tabWid });
                    }
                    updateVal = false;
                }, 200);
            }
            if (posTop <= OCTablePos && !updateVal) {
                if (tableId && tableHead && tableId !== "" && tableHead !== "") {
                    tableId.removeClass('fixHeader');
                    tableHead.removeAttr('style');
                } else {
                    OCTable.removeClass('fixHeader');
                    OCTableHead.removeAttr('style');
                }
                updateVal = true;
            }
            if (posTop >= OCTableEndPos && !updateVal) {
                if (tableId && tableHead && tableId !== "" && tableHead !== "") {
                    tableId.removeClass('fixHeader');
                    tableHead.removeAttr('style');
                } else {
                    OCTable.removeClass('fixHeader');
                    OCTableHead.removeAttr('style');
                }
                updateVal = true;
            }
        }
    } catch (e) {
        console.log(e);
    }
}

function onEquityChartSelection(elem, value, type) {
    var graphElem = B.findOne("#optionsChangeGraph");
    if (optionsState[type].currType === equityType) {
        type = equityType;
    } else if (optionsState[type].currType === indicesType) {
        type = indicesType;
    }
    var xAxisValuesFrom = void 0;
    if (optionsState[type].type === "date") {
        xAxisValuesFrom = "strikePrice";
    } else {
        xAxisValuesFrom = "expiryDate";
    }
    switch (value) {
        case "oiChange":
            var xAxisValues = [],
                callOiChanges = [],
                putOiChanges = [];
            var getPercentageChange = function getPercentageChange(currValue, change) {
                var prevValue = void 0;
                if (change > 0) {
                    prevValue = currValue - change;
                } else if (change < 0) {
                    prevValue = currValue + Math.abs(change);
                }
                return parseFloat((change / prevValue * 100).toFixed(2));
            };
            for (var i = 0; i < optionsState[type].filteredData.length; i++) {
                var each = optionsState[type].filteredData[i];
                if (each.CE && each.CE.openInterest || each.PE && each.PE.openInterest) {
                    if (each.CE && (each.CE.openInterest || each.CE.changeinOpenInterest)) {
                        callOiChanges.push(each.CE.changeinOpenInterest);
                    } else {
                        callOiChanges.push(0);
                    }
                    if (each.PE && (each.PE.openInterest || each.PE.changeinOpenInterest)) {
                        putOiChanges.push(each.PE.changeinOpenInterest);
                    } else {
                        putOiChanges.push(0);
                    }
                    xAxisValues.push(each[xAxisValuesFrom]);
                }
            }
            $("#modal_options_graph").modal("show");
            Highcharts.chart(graphElem, getDoubleBarConfig({ data: {
                    text: "Change in Open Interest chart",
                    xValues: xAxisValues,
                    name1: "Calls(OI change)",
                    chart1: callOiChanges,
                    name2: "Puts(OI change)",
                    chart2: putOiChanges
                } }));
            break;
        case "scatterGraph":
            var callScatterData = [],
                putScatterData = [],
                chartOptions = {};
            for (var _i5 = 0; _i5 < optionsState[type].filteredData.length; _i5++) {
                var _each = optionsState[type].filteredData[_i5];
                if (optionsState[type].type === "sp") {
                    _each[xAxisValuesFrom] = new Date(_each[xAxisValuesFrom]);
                    _each[xAxisValuesFrom] = Date.UTC(_each[xAxisValuesFrom].getFullYear(), _each[xAxisValuesFrom].getMonth(), _each[xAxisValuesFrom].getDate());
                }
                if (_each[xAxisValuesFrom] && _each.CE && _each.CE.impliedVolatility) {
                    callScatterData.push([_each[xAxisValuesFrom], _each.CE.impliedVolatility]);
                }
                if (_each[xAxisValuesFrom] && _each.PE && _each.PE.impliedVolatility) {
                    putScatterData.push([_each[xAxisValuesFrom], _each.PE.impliedVolatility]);
                }
            }
            if (optionsState[type].type === "sp") {
                chartOptions = {
                    xAxis: {
                        tickInterval: 24 * 3600 * 1000, // the number of milliseconds in a day
                        allowDecimals: false,
                        title: {
                            enabled: true,
                            text: ''
                        },
                        type: 'datetime',
                        labels: {
                            formatter: function formatter(e, v, t) {
                                return Highcharts.dateFormat('%d-%b-%y', this.value);
                            }
                        }
                    }
                };
            }
            $("#modal_options_graph").modal("show");
            Highcharts.chart(graphElem, getScatterPlot({
                data: {
                    text: "Implied Volatility Scatter chart",
                    name1: "Calls (IV)",
                    chart1: callScatterData,
                    name2: "Puts (IV)",
                    chart2: putScatterData
                }, chartOptions: chartOptions }));
            break;
    }
}

function scrollToNote() {
    try {
        var $target = $('.tab-pane.active .note_container').first();
        if (!$target.length) return;
        var scrollPos = $target.offset().top;
        var headerHeight = $('header').height();
        $('html').animate({
            scrollTop: scrollPos - headerHeight - 50
        }, 800);
    } catch (e) {
        console.log(e);
    }
}

function refreshOCPage(type) {
    try {

        switch (type) {
            case "equity":

                var selectedContract = $('#optionContract option:selected').val();
                var selectedSymbol = $('#select_symbol option:selected').val();
                var selectedExpiry = $('#expirySelect option:selected').val();
                var selectedStrike = $('#strikeSelect option:selected').val();

                if (typeof selectedSymbol !== "undefined" && selectedSymbol !== "") {
                    var selectedVal = $('#select_symbol').val();
                    filterSymbolData(selectedVal);
                } else {
                    $('#select_symbol option').eq(0).prop('selected', 'selected');
                    optionsState.equity.currType = indicesType;
                    optionsState.indices.currType = indicesType;
                    // let contractList;
                    // B.get(`/api/option-chain-contract-info?symbol=${encodeURIComponent(selectedContract)}`).then((resp) => {
                    // if(resp){
                    //     contractList = JSON.parse(resp);
                    //     return contractList;
                    // }}).then((contractList)=>{
                    loadOptionChain({
                        identifier: selectedContract,
                        type: indicesType,
                        tableID: '#equity_optionChainTable',
                        underlyingValFieldID: '#equity_underlyingVal',
                        timeStampFieldID: '#equity_timeStamp',
                        totalRowFieldId: '#equityOptionChainTotalRow',
                        expriySelectFieldId: '#expirySelect',
                        strikeSelectFieldId: '#strikeSelect',
                        expriyFilterFieldId: '#expiryDateFilter',
                        strikeFilterFieldId: '#strikePriceFilter',
                        contractList: '',
                        expiry: selectedExpiry,
                        strike: selectedStrike
                    }, function () {
                        //$('#expiryDateFilter').addClass('hide');
                        $('#strikePriceFilter, #expiryDateFilter, #filterDivider').removeClass('hide').show();
                        $('#expiryDateFilter select option:selected, #strikePriceFilter select option:selected').removeAttr("selected");
                    });
                    // })
                }
                break;
            case "currency":
                var _optionCurr2 = $('#currencySelect option:selected').val();
                loadOptionChain({
                    symbol: _optionCurr2,
                    type: currencyType,
                    tableID: '#optionChainCurrTable',
                    underlyingValFieldID: '#refRate',
                    timeStampFieldID: '#currOCTime',
                    totalRowFieldId: '#optionChainCurrtotalRow',
                    expriySelectFieldId: '#currExpirySelect',
                    strikeSelectFieldId: '#currPriceSelect',
                    expriyFilterFieldId: '#currExpirySelectFilter',
                    strikeFilterFieldId: '#currPriceSelectFilter'
                }, function () {
                    $('#currExpirySelectFilter, #currPriceSelectFilter, #filterCurrDivider').removeClass('hide').show();
                    //$('#currPriceSelectFilter').addClass('hide');
                    $('#currExpirySelectFilter select option:selected, #currPriceSelectFilter select option:selected').removeAttr("selected");
                });
                break;
            case "gsec":
                var _optionGsec2 = $('#gsecSelect option:selected').val();
                loadOptionChain({
                    symbol: _optionGsec2,
                    type: gsecType,
                    tableID: '#optionChainGsecTable',
                    underlyingValFieldID: '#gsecRate',
                    timeStampFieldID: '#gsecOCTime',
                    totalRowFieldId: '#optionChainGsectotalRow',
                    expriySelectFieldId: '#gsecExpirySelect',
                    strikeSelectFieldId: '#gsecPriceSelect',
                    expriyFilterFieldId: '#gsecExpirySelectFilter',
                    strikeFilterFieldId: '#gsecPriceSelectFilter'
                }, function () {
                    $('#gsecExpirySelectFilter, #gsecPriceSelectFilter, #filterGsecDivider').removeClass('hide').show();
                    //$('#currPriceSelectFilter').addClass('hide');
                    $('#gsecExpirySelectFilter select option:selected, #gsecPriceSelectFilter select option:selected').removeAttr("selected");
                });
                break;
            case "goldm":
                var selectedCommodity = $('#goldmSelect option:selected').val();
                loadOptionChain({
                    symbol: selectedCommodity,
                    type: goldmType,
                    tableID: '#optionChainGoldmTable',
                    underlyingValFieldID: '#goldmRate',
                    timeStampFieldID: '#goldmOCTime',
                    totalRowFieldId: '#optionChainGoldmtotalRow',
                    expriySelectFieldId: '#goldmExpirySelect',
                    strikeSelectFieldId: '#goldmPriceSelect',
                    expriyFilterFieldId: '#goldmExpirySelectFilter',
                    strikeFilterFieldId: '#goldmPriceSelectFilter'
                }, function () {
                    $('#goldmExpirySelectFilter, #goldmPriceSelectFilter, #filterGoldMDivider').removeClass('hide').show();
                    //$('#currPriceSelectFilter').addClass('hide');
                    $('#goldmExpirySelectFilter select option:selected, #goldmPriceSelectFilter select option:selected').removeAttr("selected");
                });
                break;
        }
    } catch (e) {
        console.log(e);
    }
}
function downloadOCFile(_this, type) {
    try {
        switch (type) {
            case 'equity':
                var selectedContract = $('#optionContract option:selected').val();
                var selectedSymbol = $('#select_symbol option:selected').val();
                var expiryDateVal = $('#expirySelect option:selected').val();
                var strikePriceVal = $('#strikeSelect option:selected').val();
                var fileName = "option-chain-ED";
                if (typeof selectedSymbol !== "undefined" && selectedSymbol !== "") {
                    fileName = fileName + '-' + selectedSymbol;
                } else {
                    fileName = fileName + '-' + selectedContract;
                }

                if (expiryDateVal && expiryDateVal !== "") {
                    fileName = fileName + '-' + expiryDateVal;
                }

                if (strikePriceVal && strikePriceVal !== "") {
                    fileName = fileName + '-' + strikePriceVal;
                }

                $('#downloadOCTable').attr('download', fileName + '.csv');
                if (optionChainType === "equity") {
                    export_table_to_csv(_this, 'optionChainTable-equity', fileName, 'csv');
                } else {
                    export_table_to_csv(_this, 'optionChainTable-indices', fileName, 'csv');
                }
                break;
            case 'currency':
                var selectedCurr = $('#currencySelect option:selected').val();
                var expiryDateCurrVal = $('#currExpirySelect option:selected').val();
                var strikePriceCurrVal = $('#currPriceSelect option:selected').val();
                var curfileName = "option-chain-CD";
                curfileName = curfileName + '-' + selectedCurr;

                if (expiryDateCurrVal && expiryDateCurrVal !== "") {
                    curfileName = curfileName + '-' + expiryDateCurrVal;
                }

                if (strikePriceCurrVal && strikePriceCurrVal !== "") {
                    curfileName = curfileName + '-' + strikePriceCurrVal;
                }

                $('#downloadOCCurTable').attr('download', curfileName + '.csv');
                export_table_to_csv(_this, 'optionChainTable-currency', curfileName, 'csv');
                break;
            case 'gsec':
                var selectedGsec = $('#gsecSelect option:selected').val();

                var expiryDateGsecVal = $('#gsecExpirySelect option:selected').val();
                var strikePriceGsecVal = $('#gsecPriceSelect option:selected').val();

                var gsecfileName = "option-chain-IRF";
                gsecfileName = gsecfileName + '-' + selectedGsec;

                if (expiryDateGsecVal && expiryDateGsecVal !== "") {
                    gsecfileName = gsecfileName + '-' + expiryDateGsecVal;
                }

                if (strikePriceGsecVal && strikePriceGsecVal !== "") {
                    gsecfileName = gsecfileName + '-' + strikePriceGsecVal;
                }

                $('#downloadOCGsecTable').attr('download', gsecfileName + '.csv');
                export_table_to_csv(_this, 'optionChainTable-irf', gsecfileName, 'csv');
                break;
            case 'goldm':
                var selectedCommodity = $('#goldmSelect option:selected').val();

                var expiryDateComVal = $('#goldmExpirySelect option:selected').val();
                var strikePriceComVal = $('#goldmPriceSelect option:selected').val();

                var comfileName = "option-chain-COM";
                comfileName = comfileName + '-' + selectedCommodity;

                if (expiryDateComVal && expiryDateComVal !== "") {
                    comfileName = comfileName + '-' + expiryDateComVal;
                }

                if (strikePriceComVal && strikePriceComVal !== "") {
                    comfileName = comfileName + '-' + strikePriceComVal;
                }

                $('#downloadOCGoldMTable').attr('download', comfileName + '.csv');
                export_table_to_csv(_this, 'optionChainTable-goldm', comfileName, 'csv');
                break;
        }
    } catch (e) {
        console.log(e);
    }
}

// function loadComLov() {
//     try {
//         B.get("/api/quotes-commodity-derivatives-master").then(function (resp) {
//             if (resp) {
//                 var jsonResp = JSON.parse(resp);
//                 if (jsonResp) {
//                     var $select1 = $('#goldmSelect');
//                     for (var _iterator5 = Object.entries(jsonResp), _isArray5 = Array.isArray(_iterator5), _i6 = 0, _iterator5 = _isArray5 ? _iterator5 : _iterator5[Symbol.iterator]();;) {
//                         var _ref6;

//                         if (_isArray5) {
//                             if (_i6 >= _iterator5.length) break;
//                             _ref6 = _iterator5[_i6++];
//                         } else {
//                             _i6 = _iterator5.next();
//                             if (_i6.done) break;
//                             _ref6 = _i6.value;
//                         }

//                         var _ref7 = _ref6,
//                             key = _ref7[0],
//                             value = _ref7[1];

//                         for (var _iterator6 = value, _isArray6 = Array.isArray(_iterator6), _i7 = 0, _iterator6 = _isArray6 ? _iterator6 : _iterator6[Symbol.iterator]();;) {
//                             var _ref8;

//                             if (_isArray6) {
//                                 if (_i7 >= _iterator6.length) break;
//                                 _ref8 = _iterator6[_i7++];
//                             } else {
//                                 _i7 = _iterator6.next();
//                                 if (_i7.done) break;
//                                 _ref8 = _i7.value;
//                             }

//                             var item = _ref8;

//                             if (item.instrumentType && item.instrumentType.substring(0, 3).toLowerCase() === 'opt') {
//                                 $('<option value="' + key + '"></option>').html(key).appendTo($select1);
//                             }
//                         }
//                     }
//                     var selectedCommodity = $('#goldmSelect option:selected').val();
//                     selectedCommodities = selectedCommodity;
//                     if (commodityspotrates) {
//                         // selectedCommodity === 'GOLDM' ? 'GOLD' :
//                         updateComRefRate(commodityspotrates, selectedCommodity, false, false);
//                     }
//                 }
//             }
//         });
//     } catch (e) {
//         console.log(e);
//     }
// }
function updateComRefRate(data, symbol) {
    var metal = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
    var energy = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;
    try {
        if (data && symbol) {
            for (var _iterator7 = data, _isArray7 = Array.isArray(_iterator7), _i8 = 0, _iterator7 = _isArray7 ? _iterator7 : _iterator7[Symbol.iterator]();;) {
                var _ref9;

                if (_isArray7) {
                    if (_i8 >= _iterator7.length) break;
                    _ref9 = _iterator7[_i8++];
                } else {
                    _i8 = _iterator7.next();
                    if (_i8.done) break;
                    _ref9 = _i8.value;
                }

                var key = _ref9;

                if (key.symbol === symbol) {
                    commodity_ltp = key.lastSpotPrice && key.lastSpotPrice || 0;
                    if (metal) {
                        B.findOne('#metal_symbol').innerText = key.symbol || '-';
                        B.findOne('#metal_underlyingVal').innerText = key.lastSpotPrice && DecimalFixed(key.lastSpotPrice) || '-';
                        B.findOne('#metal_unit').innerText = key.lotSize || '-';
                    } else {
                        B.findOne('#goldm_symbol').innerText = key.symbol || '-';
                        B.findOne('#goldm_underlyingVal').innerText = key.lastSpotPrice && DecimalFixed(key.lastSpotPrice) || '-';
                        B.findOne('#goldm_unit').innerText = key.lotSize || '-';
                    }
                    if (energy) {
                        B.findOne('#energy_symbol').innerText = key.symbol || '-';
                        B.findOne('#energy_underlyingVal').innerText = key.lastSpotPrice && DecimalFixed(key.lastSpotPrice) || '-';
                        B.findOne('#energy_unit').innerText = key.lotSize || '-';
                    }
                }
            }
        } else {
            commodity_ltp = 0;
            B.findOne('#goldm_symbol').innerText = '-';
            B.findOne('#goldm_underlyingVal').innerText = '-';
            B.findOne('#goldm_unit').innerText = '-';
        }
    } catch (e) {
        console.log(e);
    }
}