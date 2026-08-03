const btn = document.getElementById("startFaceAttendance");

if(btn){

    btn.addEventListener("click", async ()=>{

        const subject =
        document.getElementById("subjectSelect").value;

        const response = await fetch(
            "/start-face-attendance",
            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    subject:subject

                })

            }
        );

        const data = await response.json();

        alert(data.message);

    });

}