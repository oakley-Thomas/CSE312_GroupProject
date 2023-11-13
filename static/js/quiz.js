function answerQuiz(form) {
    var selectedRadioButton = form.querySelector("input[name='user-answer']:checked");
    var quizID = form.id
    if (selectedRadioButton){
        const post = { id: quizID, answer: selectedRadioButton.id};
        axios.post('/answer-quiz', post)
            .then(response => handleSubmission(response))
            .catch(error => console.error(error));
    }
    else{
        alert("Please choose an answer to submit.");
    }
}

function handleSubmission(response)
{
    if (response.data == "OK"){
        document.getElementById("responseMessage").innerHTML = '<h1>Submitted!</h1>'
    }
    else if (response.data == "Unauthenticated"){
        document.getElementById("responseMessage").innerHTML = '<h1>Sorry, log in to answer this quiz!</h1>'
    }
}