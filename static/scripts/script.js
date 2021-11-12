var sourceNamesArray = [];
var currentThumbnailURL = '';
var searchConstrained = false;
var currentIntervalObj = null;
var currentTimeoutObj = null;
var currentColourMode = localStorage.getItem('colourMode');

//This has to happen as early as possible to prevent a flicker of light mode on load when in dark mode
if(!!currentColourMode) {
    document.documentElement.setAttribute('data-colourMode', currentColourMode);
} else {
    localStorage.setItem('colourMode', 'light');
}

$(document).ready(function() {
    window.addEventListener('keydown', enableFocusRings);
    //
    $('.responsive-icon').mouseenter(function() {
        var pos = $(this).offset();
        $(this).css('--top-offset', ((pos.top - window.pageYOffset) + 25) + 'px');
    });
    //
    if(currentColourMode == 'dark') {
        document.getElementById('colourmode-toggle').setAttribute('aria-label', 'Toggle light mode');
    } else {
        document.getElementById('colourmode-toggle').setAttribute('aria-label', 'Toggle dark mode');
    }
    //
    var temp = Array.from(document.getElementsByClassName('responsive-icon'));
    temp = temp.slice(1, temp.length - 1);
    for(var i = 0; i < temp.length; i++) {
        sourceNamesArray.push(temp[i].getAttribute('data-tooltip').toLowerCase());
    }
    //
    var sourceID = localStorage.getItem('redirectTo');
    if(!!sourceID) {
        loadVideosOf(sourceID, true);
        displayMessage('Video source added successfully');
        localStorage.removeItem('redirectTo');
    }
});

function openAddSourceModal() {
    $("#add-source-modal").modal({fadeDuration: 200});
}

function displayMessage(message) {
    document.getElementById('message-container').textContent = message;
    $("#info-messages-modal").modal({fadeDuration: 200});
}

function confirmAction(message, callback) {
    document.getElementById('query-container').textContent = message;
    $("#confirmation-modal").modal({fadeDuration: 200, escapeClose: false, clickClose: false, showClose: false});
    $('#accept-btn').off('click'); $('#reject-btn').off('click');
    $('#accept-btn').on('click', function() {
        $.modal.close();
        callback(true, true);
    });
    $('#reject-btn').on('click', function() {
        $.modal.close();
        callback(true, false);
    });
}

function showLoading() {
    $("#loading-modal").modal({fadeDuration: 200, escapeClose: false, clickClose: false, showClose: false});
}

function setCurrentSource(sourceID) {
    document.getElementById('current-source').value = sourceID;
}

function getCurrentSource(sourceID) {
    return document.getElementById('current-source').value;
}

function searchFocus() {
    document.getElementById('search-text').focus();
}

function clearSearch() {
    document.getElementById('search-text').value = '';
    for(var i = 0; i < sourceNamesArray.length; i++) {
        document.getElementsByClassName('responsive-icon')[i + 1].style.display = 'block';
    }
    searchConstrained = false;
    searchFocus();
}

function filterSources() {
    var searchTerm = document.getElementById('search-text').value.toLowerCase();
    if(searchTerm.length < 1) {
        if(searchConstrained) {clearSearch();}
        return;
    }
    for(var i = 0; i < sourceNamesArray.length; i++) {
        var element = document.getElementsByClassName('responsive-icon')[i + 1];
        if(!sourceNamesArray[i].includes(searchTerm)) {
            element.style.display = 'none';
        } else {
            element.style.display = 'block';
        }
    }
    searchConstrained = true;
}

function showPreview(target, force = false) {
    var preview = target.dataset.preview;
    if(preview != '' && !force) {
        window.currentThumbnailURL = target.src;
        window.currentTimeoutObj = setTimeout(function() {
            target.parentElement.querySelector('.video-duration').style.display = 'none';
            target.src = preview;
            target.onload = function(e) {
                if(target.naturalWidth == 120 && target.naturalHeight == 90) {
                    fallbackPreview(target);
                }
            }
        }, 1000);
    } else {
        var currentIndex = 1;
        var chunks = target.src.split('/');
        window.currentThumbnailURL = target.src;
        var domain = chunks[2]; var videoID = chunks[4];
        window.currentIntervalObj = setInterval(function() {
            target.parentElement.querySelector('.video-duration').style.display = 'none';
            target.src = `https://${domain}/vi/${videoID}/mq${currentIndex}.jpg`;
            currentIndex = (currentIndex === 3)? 1: ++currentIndex;
        }, 1000);
    }
}

function hidePreview(target) {
    if(window.currentIntervalObj != null) {
        clearInterval(window.currentIntervalObj);
    }
    if(window.currentTimeoutObj != null) {
        clearTimeout(window.currentTimeoutObj);
    }
    target.parentElement.querySelector('.video-duration').style.display = 'block';
    target.src = window.currentThumbnailURL;
    window.currentThumbnailURL = '';
}

function fallbackPreview(target) {
    hidePreview(target);
    showPreview(target, true);
}

function dqEscape(string) {
    return string.replace(/"/g, '&#34;');
}

function enableFocusRings(event) {
    if (event.keyCode === 9) {
        document.body.classList.add('tab-key-used');
        window.removeEventListener('keydown', enableFocusRings);
    }
}

function setFiltered(isFiltered) {
    if(isFiltered) {
        document.getElementById('clear-filter').style.display = 'block';
    } else {
        document.getElementById('clear-filter').style.display = 'none';
    }
}

function toggleColourMode() {
    var currentColourMode = localStorage.getItem('colourMode');
    if(!!currentColourMode) {
        if(currentColourMode == 'dark') {
            localStorage.setItem('colourMode', 'light');
            document.documentElement.setAttribute('data-colourMode', 'light');
            document.getElementById('colourmode-toggle').setAttribute('aria-label', 'Toggle dark mode');
        } else {
            localStorage.setItem('colourMode', 'dark');
            document.documentElement.setAttribute('data-colourMode', 'dark');
            document.getElementById('colourmode-toggle').setAttribute('aria-label', 'Toggle light mode');
        }
    } else {
        localStorage.setItem('colourMode', 'light');
        toggleColourMode();
    }
}

function loadVideosOf(sourceID, isUpdate = false, filterBy = 0) {
    setFiltered(false);
    if(searchConstrained) {clearSearch();}
    if(!isUpdate) { if(getCurrentSource() == sourceID) {return;} }
    $.ajax({
        type: 'GET',
        url: filterBy > 0? `/filter?sourceID=${sourceID}&filterBy=${filterBy}`: `/feed?sourceID=${sourceID}`,
        success: function(data) {
            var container = document.getElementsByClassName('content')[0];
            container.innerHTML = '';
            var html = `
            <div class="source-content">
                <div class="source-name">
                    <a href="${data.sourceURL}" target="_blank">
                        <img src="${data.channelIcon[0]}" />
                        <span>${data.sourceName}</span>
                    </a>
                </div>
                <hr>
                <div class="video-grid">
            `
            for(var i = 0; i < data.entries.length; i++) {
                if(data.entries[i].ratio == 'Rating unavailable') {
                    if(data.entries[i].duration == 'LIVE') {
                        var html2 = `
                            <a class="video-container" href="${data.entries[i].url}" target="_blank">
                                <div class="video-thumbnail">
                                    <img src="${data.entries[i].thumbnail}" onmouseover="showPreview(this);" onmouseout="hidePreview(this);" data-preview="${data.entries[i].preview}" />
                                    <span style="background: rgba(204, 0, 0, .9) !important; padding-right: 5px !important; padding-left: 5px !important;" class="video-duration">${data.entries[i].duration}</span>
                                </div>
                                <div class="rating-bar" aria-label="${data.entries[i].ratio}" data-balloon-pos="down">
                                    <div class="dislikes">
                                        <div class="likes" style="width:100%; background: var(--unavailable-color);"></div>
                                    </div>
                                </div>
                                <div class="video-info">
                                    <b class="video-title" title="${dqEscape(data.entries[i].title)}">${data.entries[i].title}</b>
                                    <span>${data.entries[i].views} views&nbsp;&nbsp;•&nbsp;&nbsp;${data.entries[i].published}</span>
                                </div>
                            </a>
                        `
                    } else {
                        var html2 = `
                            <a class="video-container" href="${data.entries[i].url}" target="_blank">
                                <div class="video-thumbnail">
                                    <img src="${data.entries[i].thumbnail}" onmouseover="showPreview(this);" onmouseout="hidePreview(this);" data-preview="${data.entries[i].preview}" />
                                    <span class="video-duration">${data.entries[i].duration}</span>
                                </div>
                                <div class="rating-bar" aria-label="${data.entries[i].ratio}" data-balloon-pos="down">
                                <div class="dislikes">
                                    <div class="likes" style="width:100%; background: var(--unavailable-color);"></div>
                                </div>
                            </div>
                                <div class="video-info">
                                    <b class="video-title" title="${dqEscape(data.entries[i].title)}">${data.entries[i].title}</b>
                                    <span>${data.entries[i].views} views&nbsp;&nbsp;•&nbsp;&nbsp;${data.entries[i].published}</span>
                                </div>
                            </a>
                        `
                    }
                } else {
                    if(data.entries[i].duration == 'LIVE') {
                        var html2 = `
                            <a class="video-container" href="${data.entries[i].url}" target="_blank">
                                <div class="video-thumbnail">
                                    <img src="${data.entries[i].thumbnail}" onmouseover="showPreview(this);" onmouseout="hidePreview(this);" data-preview="${data.entries[i].preview}" />
                                    <span style="background: rgba(204, 0, 0, .9) !important; padding-right: 5px !important; padding-left: 5px !important;" class="video-duration">${data.entries[i].duration}</span>
                                </div>
                                <div class="rating-bar" aria-label="${data.entries[i].ratio}" data-balloon-pos="down">
                                    <div class="dislikes">
                                        <div class="likes" style="width:${data.entries[i].rating}%;"></div>
                                    </div>
                                </div>
                                <div class="video-info">
                                    <b class="video-title" title="${dqEscape(data.entries[i].title)}">${data.entries[i].title}</b>
                                    <span>${data.entries[i].views} views&nbsp;&nbsp;•&nbsp;&nbsp;${data.entries[i].published}</span>
                                </div>
                            </a>
                        `
                    } else {
                        var html2 = `
                            <a class="video-container" href="${data.entries[i].url}" target="_blank">
                                <div class="video-thumbnail">
                                    <img src="${data.entries[i].thumbnail}" onmouseover="showPreview(this);" onmouseout="hidePreview(this);" data-preview="${data.entries[i].preview}" />
                                    <span class="video-duration">${data.entries[i].duration}</span>
                                </div>
                                <div class="rating-bar" aria-label="${data.entries[i].ratio}" data-balloon-pos="down">
                                    <div class="dislikes">
                                        <div class="likes" style="width:${data.entries[i].rating}%;"></div>
                                    </div>
                                </div>
                                <div class="video-info">
                                    <b class="video-title" title="${dqEscape(data.entries[i].title)}">${data.entries[i].title}</b>
                                    <span>${data.entries[i].views} views&nbsp;&nbsp;•&nbsp;&nbsp;${data.entries[i].published}</span>
                                </div>
                            </a>
                        `
                    }
                }

                html += html2;
            }
            html += `
                </div>
            </div>
            `
            container.innerHTML = html;
            setCurrentSource(sourceID);
        }
    });
}

function getLatestVideos(recall = false, confirmed = false) {
    var sourceID = getCurrentSource();
    if(sourceID == 'home') {
        if(!recall) {
            confirmAction('This operation will attempt to update feeds from all added video sources.\nIt is recommended to perform this operation for individual sites only.\nAre you sure you want to continue?', getLatestVideos);
            return;
        } else {
            if(!confirmed) {return;}
        }
    }
    showLoading();
    $.ajax({
        type: 'POST',
        url: '/update?sourceID=' + sourceID,
        success: function(data) {
            if(data.success) {
                if(sourceID == 'home') {
                    window.location.href = '/';
                    return;
                } else {
                    loadVideosOf(sourceID, true);
                }
                displayMessage('Feed updated successfully');
            } else {
                displayMessage(`An error occurred while updating the feed\n\n${data.details}`);
            }
        }
    });
}

function addVideoSource() {
    var sourceID = document.getElementById('source-id').value;
    document.getElementById('source-id').value = '';
    if(sourceID.length < 20) {return;}
    showLoading();
    $.ajax({
        type: 'POST',
        url: '/addfeed?sourceID=' + sourceID,
        success: function(data) {
            if(data.success) {
                localStorage.setItem('redirectTo', sourceID);
                window.location.href = '/';
            } else {
                displayMessage(`An error occurred while adding the video source\n\n${data.details}`);
            }
        }
    });
}

function deleteVideoSource(recall = false, confirmed = false) {
    var sourceID = getCurrentSource();
    if(sourceID == 'home') {
        displayMessage('Cannot delete home feed. Please select an individual video source in the sidebar and try again');
        return;
    } else {
        if(!recall) {
            confirmAction('Are sure you want to delete this video source?', deleteVideoSource);
            return;
        } else {
            if(!confirmed) {return;}
        }
    }
    $.ajax({
        type: 'POST',
        url: '/remfeed?sourceID=' + sourceID,
        success: function(data) {
            if(data.success) {
                window.location.href = '/';
            } else {
                displayMessage(`An error occurred while deleting the video source\n\n${data.details}`);
            }
        }
    });
}

function downloadVideoSource(recall = false, confirmed = false) {
    var sourceID = getCurrentSource();
    if(sourceID == 'home') {
        if(!recall) {
            confirmAction('This operation will attempt to download feeds from all added video sources.\nThis may take very long to complete and cause your IP address to be flagged by youtube for video scraping.\nIt is recommended to perform this operation for individual sites only.\nAre you sure you want to continue?', downloadVideoSource);
            return;
        } else {
            if(!confirmed) {return;}
        }
    }
    showLoading();
    $.ajax({
        type: 'POST',
        url: '/download?sourceID=' + sourceID,
        success: function(data) {
            if(data.success) {
                if(sourceID == 'home') {
                    window.location.href = '/';
                } else {
                    loadVideosOf(sourceID, true);
                    displayMessage('Feed downloaded successfully');
                }
            } else {
                displayMessage(`An error occurred while downloading the feed\n\n${data.details}`);
            }
        }
    });
}

function filterVideos(hours) {
    var sourceID = getCurrentSource();
    if(!Number.isInteger(hours)) {return;}
    if(sourceID == 'home') {
        displayMessage('Cannot filter home feed. Please select an individual video source in the sidebar and try again');
        return;
    }
    loadVideosOf(sourceID, true, hours);
    setFiltered(true);
}

function clearFilter() {
    var sourceID = getCurrentSource();
    loadVideosOf(sourceID, true);
    setFiltered(false);
}