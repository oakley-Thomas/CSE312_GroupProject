function clearQuizHistory() {
    const postHistory = document.getElementById("postHistory");
    postHistory.innerHTML = "";
}

function addQuiz(messageJSON) {
    const postHistory = document.getElementById("postHistory");
    postHistory.innerHTML += postHTML(messageJSON);
    postHistory.scrollIntoView(false);
    postHistory.scrollTop = postHistory.scrollHeight - postHistory.clientHeight;
}

function postHTML(messageJSON) {
    const quizTitle = messageJSON.title;
    const timeRemaining = messageJSON.duration
    let postHTML = "<form id='" + quizTitle + "'>"
    postHTML += "<h2 class='postTitle'>" + quizTitle + "</h2>";
    postHTML += "<p> Time Remaining: " + timeRemaining + "</p>";
    for (const [optionLabel, optionValue] of Object.entries(messageJSON.choices))
    {
        postHTML += "<input type='radio' id='" + optionLabel + "' name='user-answer' value='" + optionValue + "'></input>"
        postHTML += "<label for='" + optionLabel + "'>" + optionValue + "</label><br></br>"
    }
    postHTML += "<input type='button' value='Answer' onclick='answerQuiz(this.form)'>"
    postHTML += "</form>"
    postHTML += "<div class='postLine'></div>";
    return postHTML;
}

// TODO: Convert this to answerQuiz
function answerQuiz(form) {
    var selectedRadioButton = form.querySelector("input[name='user-answer']:checked");
    var quizID = form.id
    if (selectedRadioButton){
        const post = { id: quizID, answer: selectedRadioButton.id};
        axios.post('/answer-quiz', post)
            .then(response => confirmSubmission())
            .catch(error => console.error(error));
    }
    else{
        alert("Please choose an answer to submit.");
    }
}

function logout() {
    const token = localStorage.getItem("authtoken");
    localStorage.removeItem("authtoken");
    location.replace("/login");
}

function updatePostHistory() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearQuizHistory();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                for (const [key, value] of Object.entries(message))
                {
                    addQuiz(JSON.parse(value));
                }
                
            }
        }
    }
    request.open("GET", "/quiz-history");
    request.send();
}

function onLoadRun() {
    updatePostHistory();
    setInterval(updatePostHistory, 5000);
}