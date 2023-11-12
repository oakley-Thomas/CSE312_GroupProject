
function update() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clear();
            const grades = JSON.parse(this.response);
            for (const grade of grades) {
                addGrade(grade);
            }
        }
    };
    request.open("GET", "/user_grades");
    request.send();
}

function addGrade(grade) {
    const tableNum = document.getElementById("tableNum");

    const row = tableNum.insertRow();
    const questionCell = row.insertCell(0);
    const scoreCell = row.insertCell(1);

    questionCell.textContent = grade.question.text;
scoreCell.textContent = `${grade.score}/${grade.max_points}`;
}

function clear() {
    const tableNum = document.getElementById("tableNum");
    tableNum.innerHTML = "";
}

document.addEventListener("DOMContentLoaded", function () {
    update();
});
