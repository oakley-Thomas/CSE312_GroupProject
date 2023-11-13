
function update() {
    const request = new XMLHttpRequest();

    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clear();
            const dataSet = JSON.parse(this.responseText);
            for (const data of dataSet) {
                addGrade(data);
            }
        }
    };

    request.open("GET", "/user_grades");
    request.send();

}

function addGrade(data) {
    const tableNum = document.getElementById("tableNum");
    for (const userGrade of data.userGrades) {
        tableNum.innerHTML += gradeHTML(data.question, userGrade);
    }
}

function gradeHTML(question,userGrade) {
    const username = userGrade.username;
    const grade = userGrade.grade;
    return `<tr>
                <td>${question}</td>
                <td>${grade}</td>
                <td>${username}</td>
            </tr>`;
}

function clear() {
    const tableNum = document.getElementById("tableNum");
    tableNum.innerHTML = "";
}

document.addEventListener("DOMContentLoaded", update);