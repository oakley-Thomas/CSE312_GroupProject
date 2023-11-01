function postData() {
    const title = document.getElementById("Title").value;
    const description = document.getElementById("Description").value;
    const userAnswers = document.getElementsByName("user-answer");
    var correct = "";
    for (var i = 0; i < userAnswers.length; i++) {
        if (userAnswers[i].checked){
            console.log("Correct Answer: " + userAnswers[i].value)
            correct = userAnswers[i].value
        }
    }

    const post = { title: title, description: description, correct: correct };
    axios.post('/submit-quiz', post)
        .then(response => console.log(response.data))
        .catch(error => console.error(error));
}

