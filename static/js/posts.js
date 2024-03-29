function clearPostHistory() {
    const postHistory = document.getElementById("postHistory");
    postHistory.innerHTML = "";
}

function addPost(messageJSON) {
    const postHistory = document.getElementById("postHistory");
    postHistory.innerHTML += postHTML(messageJSON);
    postHistory.scrollIntoView(false);
    postHistory.scrollTop = postHistory.scrollHeight - postHistory.clientHeight;
}

function postHTML(messageJSON) {
    const postTitle = messageJSON.title;
    const postDescription = messageJSON.description;
    const postLikeCount = messageJSON.likes;
    const postSender = messageJSON.username;
    const postId = messageJSON.id;
    const image = messageJSON.image;
    let postHTML = "<div class='post ratingSelected' id='" + postId + "'>";
    postHTML += "<div class='postSender'>" + postSender + ": </div>";
    postHTML += "<div class='postTemplate'>";
    postHTML += "<div class='postTitle'>" + postTitle + "</div>";
    postHTML += "<div class='postLine'></div>";
    postHTML += "<div class='postDescription'>" + postDescription + "</div>";
    if (image) {
        postHTML += "<img src='" + image + "' class='postImage'>";
    }
    postHTML += "</div>";
    postHTML += "<div class='ratingLocation'>";
    postHTML += "<div class='rating'>";
    postHTML += "<button onclick='likePost(" + postId + ")' class='ratingButton material-icons'>thumb_up</button>";
    postHTML += "<span class='ratingCount'>" + postLikeCount + "</span>";
    postHTML += "</div>";
    postHTML += "</div>";
    postHTML += "</div>";
    return postHTML;
}

function likePost(postId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("POST", "/likepost/" + postId);
    request.send();
}


function updatePostHistory() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearPostHistory();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addPost(message);
            }
        }
    }
    request.open("GET", "/post-history");
    request.send();
}

function onLoadRun() {
    updatePostHistory();
    setInterval(updatePostHistory, 2000);
}   
