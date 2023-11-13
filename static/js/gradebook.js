
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
    tableNum.innerHTML += gradeHTML(data);
}

function gradeHTML(data) {
    const question = data.question;
    const grade = data.grade;
    return `<tr>
                <td>${question}</td>
                <td>${grade}</td>
            </tr>`;
}

function clear() {
    const tableNum = document.getElementById("tableNum");
    tableNum.innerHTML = "";
}

document.addEventListener("DOMContentLoaded", update);